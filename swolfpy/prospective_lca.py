# -*- coding: utf-8 -*-
"""
Prospective LCA module for swolfpy using premise IAM transformations.

Provides scenario-conditional LCA against REMIND-transformed ecoinvent databases,
enabling future-year impact assessment under SSP2-45 and SSP5-85 climate pathways.

Prerequisites:
    - ecoinvent 3 license (ecoinvent.ch)
    - Premise encryption key (free, request at premise@psi.ch)

Example:
    >>> from swolfpy import ProspectiveLCA
    >>>
    >>> lca = ProspectiveLCA(
    ...     project="my_brightway_project",
    ...     source_db="ecoinvent 3.10 cutoff",
    ...     model="remind",
    ...     scenario="SSP2-45",
    ...     year=2040,
    ...     key="your-premise-key",
    ... )
    >>> activity = bd.get_node(database=lca.db_name, name="treatment of waste")
    >>> result_df = lca.run(activity, method=("IPCC 2021", "GWP100"))
    >>> print(result_df.to_json(orient="records"))

Note:
    Cold transformation (no cached DB) takes 15–45 minutes on standard hardware.
    Subsequent runs on the same scenario/year/version are instant (cache hit).
"""

import importlib.metadata
import logging
from typing import Optional

import bw2calc as bc
import bw2data as bd
import pandas as pd
from premise import NewDatabase  # module-scope: enables mock.patch

logger = logging.getLogger(__name__)  # "swolfpy.prospective_lca"


class ProspectiveLCA:
    """
    Scenario-conditional LCA using premise IAM transformations.

    Instantiates with Brightway project, ecoinvent source database, IAM model,
    scenario, target year, and Premise encryption key. Checks for an existing
    transformed database by 5-part deterministic signature before running
    premise transformation.

    :param project: Brightway project name containing the source ecoinvent database.
    :type project: str

    :param source_db: Name of the base ecoinvent database in the Brightway project.
    :type source_db: str

    :param model: IAM model identifier (see ``SUPPORTED_SCENARIOS``).
    :type model: str

    :param scenario: Scenario identifier (see ``SUPPORTED_SCENARIOS``).
    :type scenario: str

    :param year: Target year for prospective transformation (integer).
    :type year: int

    :param key: Premise encryption key (request at premise@psi.ch).
    :type key: str

    :raises ValueError: If key is missing/empty, source_db not found in project,
        or model/scenario is unsupported.

    Example:
        >>> lca = ProspectiveLCA(
        ...     project="swolfpy_project",
        ...     source_db="ecoinvent 3.10 cutoff",
        ...     model="remind",
        ...     scenario="SSP2-45",
        ...     year=2040,
        ...     key="your-key",
        ... )
        >>> df = lca.run(
        ...     activity=bd.get_node(database=lca.db_name, name="treatment of waste"),
        ...     method=("IPCC 2021", "GWP100"),
        ... )
    """

    SUPPORTED_SCENARIOS: dict[str, list[str]] = {
        "remind": ["SSP2-45", "SSP5-85"],
    }

    def __init__(
        self,
        project: str,
        source_db: str,
        model: str,
        scenario: str,
        year: int,
        key: str,
    ) -> None:
        """
        Validate inputs and initialize or load the transformed Brightway database.

        Validation order (mandatory — do not reorder):
        1. key presence/non-emptiness
        2. bd.projects.set_current(project)
        3. source_db existence in bd.databases
        4. model/scenario against SUPPORTED_SCENARIOS
        5. Resolve premise version (importlib.metadata)
        6. Build cache key (_build_db_name)
        7. Cache check → load or _transform_database()

        :param project: Brightway project name.
        :type project: str

        :param source_db: Base ecoinvent database name.
        :type source_db: str

        :param model: IAM model identifier.
        :type model: str

        :param scenario: Scenario identifier.
        :type scenario: str

        :param year: Target year (integer).
        :type year: int

        :param key: Premise encryption key.
        :type key: str

        :raises ValueError: key empty/missing, source_db not found, unsupported model/scenario.
        """
        raise NotImplementedError

    def run(
        self,
        activity: object,
        method: tuple,
        functional_unit: float = 1,
    ) -> pd.DataFrame:
        """
        Run LCA computation and return scenario-native DataFrame.

        :param activity: Brightway activity node from the transformed database
            (``bd.get_node(database=self.db_name, ...)``). Do NOT pass a node from
            the source ecoinvent database — results will be scientifically incorrect.
        :type activity: bw2data activity node

        :param method: LCIA method tuple, e.g. ``("IPCC 2021", "GWP100")``.
        :type method: tuple

        :param functional_unit: Quantity of activity for functional unit. Default: 1.
        :type functional_unit: float

        :return: DataFrame with columns [scenario, year, impact_category, score].
            Directly serializable via ``.to_json(orient="records")``.
        :rtype: pd.DataFrame

        :raises ValueError: If activity's database does not match ``self.db_name``.
        """
        raise NotImplementedError

    @property
    def db_name(self) -> str:
        """
        Name of the transformed database (cached or newly created).

        Resolved at construction time. Format: ``{base_db}_{model}_{year}_{scenario}_premise{version}``.

        :return: Transformed database name.
        :rtype: str
        """
        raise NotImplementedError

    @property
    def premise_version(self) -> str:
        """
        Installed premise version resolved at construction time.

        Used for traceability and is embedded in the cache key to prevent
        stale results after premise upgrades.

        :return: premise version string from ``importlib.metadata.version("premise")``.
        :rtype: str
        """
        raise NotImplementedError

    def _build_db_name(self) -> str:
        """
        Construct the 5-part deterministic cache key.

        Format: ``{base_db}_{model}_{year}_{scenario}_premise{version}``

        Example: ``ecoinvent_3.10_cutoff_remind_2050_SSP2-45_premise2.3.7``

        :return: Cache key string.
        :rtype: str
        """
        raise NotImplementedError

    def _transform_database(self) -> None:
        """
        Run premise NewDatabase transformation and write result to Brightway.

        Sole caller of ``NewDatabase`` — this is the only patchable surface.

        :raises RuntimeError: Wraps premise exceptions with context message.
        """
        raise NotImplementedError
