# -*- coding: utf-8 -*-
"""
Dynamic LCA module for swolfpy using bw_temporalis.

Provides time-resolved carbon accounting for waste management systems, enabling
temporal distribution of biosphere emissions (e.g., landfill CH₄ decay over decades)
and physics-based dynamic GWP characterization via cumulative radiative forcing.

Example:
    >>> from swolfpy import Project
    >>> from swolfpy.LCA_matrix import LCA_matrix
    >>> from swolfpy.dynamic_lca import DynamicLCA
    >>>
    >>> # Standard swolfpy setup
    >>> project = Project("my_project", common_data, treatment_processes, distance)
    >>> project.init_project()
    >>> project.write_project()
    >>>
    >>> # Static LCA
    >>> lca_matrix = LCA_matrix(functional_unit=fu, method=method)
    >>> print(f"Static GWP100: {lca_matrix.score}")
    >>>
    >>> # Dynamic LCA
    >>> dlca = DynamicLCA(lca_matrix, starting_datetime="2024-01-01")
    >>> dlca.attach_temporal_distributions(temporal_profiles)
    >>> timeline_df = dlca.calculate(characterization_period=100)
    >>> print(timeline_df.groupby("year")["gwp_kgco2eq"].sum())
"""

from typing import Dict, Optional, Set

import bw2data as bd
import numpy as np
import pandas as pd
from bw_temporalis import TemporalDistribution, TemporalisLCA, Timeline
from bw_temporalis.lcia import characterize_co2, characterize_methane

from .LCA_matrix import LCA_matrix


class DynamicLCA:
    """
    Time-resolved LCA using bw_temporalis for swolfpy waste management systems.

    Wraps a computed `LCA_matrix` object, attaches temporal distributions to
    biosphere exchanges, runs graph traversal via `TemporalisLCA`, and returns
    annual GWP100 timeline as a pandas DataFrame.

    :param lca_matrix: Pre-computed swolfpy LCA_matrix object (lci + lcia complete).
    :type lca_matrix: LCA_matrix

    :param starting_datetime: Absolute time reference (ISO string or datetime).
        All temporal distributions are relative to this anchor. Default: "2024-01-01".
    :type starting_datetime: str

    :param cutoff: Relative cutoff for graph traversal (see TemporalisLCA docs).
        Default: 1e-3 (0.1%).
    :type cutoff: float

    :param max_calc: Maximum number of graph nodes to visit. Increase for complex
        supply chains. Default: 5000.
    :type max_calc: int

    Example:
        >>> from swolfpy import Project, DynamicLCA
        >>> from swolfpy.LCA_matrix import LCA_matrix
        >>>
        >>> # ... (create project, write databases, etc.)
        >>> lca_matrix = LCA_matrix(functional_unit={...}, method=[...])
        >>> dlca = DynamicLCA(lca_matrix, starting_datetime="2024-01-01")
        >>> dlca.attach_temporal_distributions(lf_temporal_profile)
        >>> timeline_df = dlca.calculate(characterization_period=100)
        >>> print(timeline_df.head())
              year  gwp_kgco2eq              flow                  activity
        0     2024       456.78  ("biosphere3", "...")  ("LF", "Material_1")
        1     2025       432.10  ("biosphere3", "...")  ("LF", "Material_1")
        ...
    """

    def __init__(
        self,
        lca_matrix: LCA_matrix,
        starting_datetime: str = "2024-01-01",
        cutoff: float = 1e-3,
        max_calc: int = 5000,
    ) -> None:
        """
        Initialize DynamicLCA with an existing LCA_matrix object.

        :param lca_matrix: Pre-computed LCA_matrix (lci + lcia already run).
        :type lca_matrix: LCA_matrix

        :param starting_datetime: ISO datetime string for t=0 anchor.
        :type starting_datetime: str

        :param cutoff: Graph traversal relative cutoff.
        :type cutoff: float

        :param max_calc: Max nodes to visit during traversal.
        :type max_calc: int
        """
        self.lca_matrix = lca_matrix
        self.starting_datetime = starting_datetime
        self.cutoff = cutoff
        self.max_calc = max_calc

        # TemporalisLCA will be instantiated after attach_temporal_distributions()
        self._temporalis_lca: Optional[TemporalisLCA] = None
        self._timeline: Optional[Timeline] = None

    def attach_temporal_distributions(
        self,
        process_temporal_profiles: Dict[str, Dict[str, Dict]],
    ) -> None:
        """
        Attach TemporalDistribution objects to biosphere exchanges in Brightway databases.

        Modifies exchanges in-place using bw2data API. Each exchange's
        `temporal_distribution` field is set to a `TemporalDistribution` object
        based on the provided profile configuration.

        :param process_temporal_profiles: Nested dict structure:
            {
                process_name: {
                    flow_name: {
                        "kind": "exponential_decay" | "immediate" | "uniform",
                        "params": {...}  # kind-specific parameters
                    }
                }
            }

            Supported kinds:
            - "exponential_decay": {"k": 0.05, "period": 50} → exp(-k*t) over period years
            - "immediate": {} → single point at t=0
            - "uniform": {"start": 0, "end": 10, "steps": 10} → evenly spread

        :type process_temporal_profiles: dict

        Example:
            >>> lf_profile = {
            ...     "LF": {
            ...         "Methane, fossil": {
            ...             "kind": "exponential_decay",
            ...             "params": {"k": 0.05, "period": 50}
            ...         },
            ...         "Carbon dioxide, biogenic": {
            ...             "kind": "exponential_decay",
            ...             "params": {"k": 0.02, "period": 100}
            ...         },
            ...     }
            ... }
            >>> dlca.attach_temporal_distributions(lf_profile)
        """
        # Ensure we're in the correct Brightway project
        # (LCA_matrix object already has project context via functional_unit)
        for process_name, flow_profiles in process_temporal_profiles.items():
            # Check if database exists
            if process_name not in bd.databases:
                raise ValueError(
                    f"Database '{process_name}' not found in current Brightway project"
                )

            # Get all activities in this process database
            db = bd.Database(process_name)
            for act in db:
                for exc in act.biosphere():
                    flow_name = exc.input["name"]
                    if flow_name in flow_profiles:
                        profile = flow_profiles[flow_name]
                        # TODO(LCA-REVIEW-PR-2): Document decay constant (k) source and site-specificity
                        # Science review flagged: k=0.05/yr (CH4) and k=0.02/yr (CO2) are illustrative, not validated
                        # Recommendation: Add reference to EPA LandGEM/IPCC Tier 2 for production calibration
                        # Tracked in: ../docs/reviews/Review_PR-2_phase2-prd-dynamic-lca_2026-02-21.md
                        td = self._build_temporal_distribution(
                            exc["amount"], profile["kind"], profile.get("params", {})
                        )
                        exc["temporal_distribution"] = td
                        exc.save()

    def _build_temporal_distribution(
        self, amount: float, kind: str, params: dict
    ) -> TemporalDistribution:
        """
        Build a TemporalDistribution from profile specification.

        :param amount: Total exchange amount to distribute over time.
        :type amount: float

        :param kind: Distribution type ("exponential_decay", "immediate", "uniform").
        :type kind: str

        :param params: Kind-specific parameters.
        :type params: dict

        :return: TemporalDistribution instance.
        :rtype: TemporalDistribution
        """
        if kind == "immediate":
            return TemporalDistribution(
                date=np.array([0], dtype="timedelta64[Y]"),
                amount=np.array([amount]),
            )
        elif kind == "exponential_decay":
            k = params["k"]  # decay constant (1/year)
            period = params["period"]  # years
            years = np.arange(0, period + 1, dtype=int)
            # Discretize continuous exponential: amount_i = total * k * exp(-k * t_i)
            # Normalize so sum equals `amount` (mass balance)
            raw_amounts = k * np.exp(-k * years)
            normalized_amounts = (amount / raw_amounts.sum()) * raw_amounts
            return TemporalDistribution(
                date=years.astype("timedelta64[Y]"),
                amount=normalized_amounts,
            )
        elif kind == "uniform":
            start = params.get("start", 0)
            end = params["end"]
            steps = params["steps"]
            years = np.linspace(start, end, steps, dtype=int)
            return TemporalDistribution(
                date=years.astype("timedelta64[Y]"),
                amount=np.full(steps, amount / steps),
            )
        else:
            raise ValueError(f"Unknown temporal distribution kind: {kind}")

    def calculate(
        self,
        characterization_period: int = 100,
        flows_to_characterize: Optional[Set[str]] = None,
    ) -> pd.DataFrame:
        """
        Run dynamic LCA calculation and return time-resolved GWP as DataFrame.

        Steps:
        1. Instantiate TemporalisLCA (graph traversal runs immediately)
        2. Build Timeline from traversal results
        3. Characterize CO₂ and CH₄ flows with dynamic radiative forcing
        4. Aggregate to annual resolution
        5. Return DataFrame

        # TODO(LCA-REVIEW-PR-2): Add GWP100 time horizon justification in docstring
        # Science review flagged: GWP characterization period hardcoded to 100y
        # Recommendation: Document IPCC AR6 alignment and Joos et al. 2013 physics basis
        # Tracked in: ../docs/reviews/Review_PR-2_phase2-prd-dynamic-lca_2026-02-21.md

        :param characterization_period: Time horizon in years (default 100 per IPCC AR6).
            Note: bw_temporalis characterize_co2/methane use Joos et al. 2013 physics,
            which aligns with IPCC AR6 GWP100 methodology (doi:10.5194/acp-13-2793-2013).
        :type characterization_period: int

        :param flows_to_characterize: Set of flow names to include (default: CO2, CH4).
        :type flows_to_characterize: set[str] | None

        :return: DataFrame with columns [year, gwp_kgco2eq, flow, activity].
        :rtype: pd.DataFrame
        """
        if flows_to_characterize is None:
            flows_to_characterize = {
                "Carbon dioxide, fossil",
                "Carbon dioxide, non-fossil",
                "Methane, fossil",
            }

        # Step 1: Instantiate TemporalisLCA (traversal runs in __init__)
        self._temporalis_lca = TemporalisLCA(
            lca_object=self.lca_matrix,
            starting_datetime=self.starting_datetime,
            cutoff=self.cutoff,
            max_calc=self.max_calc,
        )

        # Step 2: Build timeline
        self._timeline = self._temporalis_lca.build_timeline()

        # Step 3: Characterize flows
        # Get flow node IDs for filtering
        flow_node_map = {}
        for flow_name in flows_to_characterize:
            try:
                results = bd.Database("biosphere3").search(flow_name)
                if results:
                    flow_node_map[results[0].id] = flow_name
            except (IndexError, KeyError):
                pass  # Flow not found, skip

        co2_flows = {
            node_id for node_id, name in flow_node_map.items() if "carbon dioxide" in name.lower()
        }
        ch4_flows = {
            node_id for node_id, name in flow_node_map.items() if "methane" in name.lower()
        }

        df_co2 = (
            self._timeline.characterize_dataframe(
                characterization_function=characterize_co2,
                flow=co2_flows,
                cumsum=False,  # Annual (not cumulative)
            )
            if co2_flows
            else pd.DataFrame()
        )

        df_ch4 = (
            self._timeline.characterize_dataframe(
                characterization_function=characterize_methane,
                flow=ch4_flows,
                cumsum=False,
            )
            if ch4_flows
            else pd.DataFrame()
        )

        # Step 4: Combine and aggregate to annual
        df_combined = pd.concat([df_co2, df_ch4], ignore_index=True)
        if df_combined.empty:
            return pd.DataFrame(columns=["year", "gwp_kgco2eq", "flow", "activity"])

        df_combined["year"] = df_combined["date"].dt.year
        annual = (
            df_combined.groupby(["year", "flow", "activity"], as_index=False)
            .agg({"amount": "sum"})
            .rename(columns={"amount": "gwp_kgco2eq"})
        )
        return annual.sort_values("year").reset_index(drop=True)

    def get_timeline(self) -> Timeline:
        """
        Return the raw Timeline object for advanced users.

        Use this to access flow-level temporal distributions before characterization.

        :return: Timeline object from bw_temporalis.
        :rtype: Timeline

        :raises RuntimeError: If calculate() has not been called yet.
        """
        if self._timeline is None:
            raise RuntimeError("Must call calculate() before get_timeline()")
        return self._timeline
