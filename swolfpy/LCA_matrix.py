# -*- coding: utf-8 -*-
import bw2calc as bc
import bw2data as bd
import numpy as np
import pandas as pd
import scipy.sparse


class LCA_matrix(bc.LCA):
    """
    Translates the row and col indices of the technosphere and biosphere sparse matrices
    to activity keys in the Brightway2 database.

    ``self.tech_matrix`` is a dictionary that maps ``(product_key, activity_key)`` tuples
    to exchange amounts. Example:
    ``{(('LF', 'Aerobic_Residual'), ('SF1_product', 'Aerobic_Residual_MRDO')): 0.828}``

    ``self.bio_matrix`` is a dictionary that maps ``(biosphere_key, activity_key)`` tuples
    to exchange amounts. Example:
    ``{(('biosphere3', '0015ec22-72cb-4af1-8c7b-0ba0d041553c'), ('Technosphere', 'Boiler_Diesel')): 6.12e-15}``

    These dicts are updated by ``update_techmatrix`` and ``update_biomatrix`` and then
    used to rebuild the sparse matrices for Monte Carlo and Optimization runs via
    ``rebuild_technosphere_matrix`` and ``rebuild_biosphere_matrix``.

    """

    def __init__(self, functional_unit: dict, method: list) -> None:
        fu, data_objs, _ = bd.prepare_lca_inputs(functional_unit, method=method[0])
        super().__init__(demand=fu, data_objs=data_objs)
        self.lci()
        self.lcia()

        self.functional_unit = functional_unit
        self.method = method
        self._base_method = method[0]

        # Populate lca.dicts.{activity, product, biosphere} with actual keys
        self.remap_inventory_dicts()

        # Note: bc.LCA has properties `activity_dict` and `biosphere_dict` that return
        # forward mappings (key → int). We need reversed mappings (int → key) for
        # compatibility with swolfpy code (e.g., Optimization.py line 194).
        # Use underscored names to avoid collision with parent class properties.
        self._activities_dict_reversed = self.dicts.activity.reversed
        self._biosphere_dict_reversed = self.dicts.biosphere.reversed

        # Build tech_matrix from sparse technosphere matrix (COO preserves entry order)
        tech_coo = self.technosphere_matrix.tocoo()
        self._tech_coo_rows = tech_coo.row.copy()
        self._tech_coo_cols = tech_coo.col.copy()
        self._tech_shape = self.technosphere_matrix.shape

        self.tech_matrix = {}
        for i, j, v in zip(self._tech_coo_rows, self._tech_coo_cols, tech_coo.data):
            row_key = self.dicts.product.reversed[i]
            col_key = self.dicts.activity.reversed[j]
            self.tech_matrix[(row_key, col_key)] = v

        # Build bio_matrix from sparse biosphere matrix (COO preserves entry order)
        bio_coo = self.biosphere_matrix.tocoo()
        self._bio_coo_rows = bio_coo.row.copy()
        self._bio_coo_cols = bio_coo.col.copy()
        self._bio_shape = self.biosphere_matrix.shape

        self.bio_matrix = {}
        _bio_seen: set = set()
        for i, j, v in zip(self._bio_coo_rows, self._bio_coo_cols, bio_coo.data):
            bio_key = self.dicts.biosphere.reversed[i]
            col_key = self.dicts.activity.reversed[j]
            key = (bio_key, col_key)
            if key not in _bio_seen:
                self.bio_matrix[key] = v
                _bio_seen.add(key)
            else:
                # Defensive: handle rare duplicate biosphere flows by appending suffix
                self.bio_matrix[(str(bio_key) + " - 1", col_key)] = v

    # ------------------------------------------------------------------
    # Matrix rebuild helpers (BW2.5 replacement for rebuild_*_matrix)
    # ------------------------------------------------------------------

    def rebuild_technosphere_matrix(self, values: np.ndarray) -> None:
        """
        Rebuild the technosphere sparse matrix from an ordered array of values.

        The values array must be in the same insertion order as ``self.tech_matrix``
        (i.e., COO order from matrix initialisation).

        :param values: New exchange amounts in COO entry order.
        :type values: numpy.ndarray
        """
        self.technosphere_matrix = scipy.sparse.csr_matrix(
            (values, (self._tech_coo_rows, self._tech_coo_cols)),
            shape=self._tech_shape,
        )

    def rebuild_biosphere_matrix(self, values: np.ndarray) -> None:
        """
        Rebuild the biosphere sparse matrix from an ordered array of values.

        The values array must be in the same insertion order as ``self.bio_matrix``
        (i.e., COO order from matrix initialisation).

        :param values: New exchange amounts in COO entry order.
        :type values: numpy.ndarray
        """
        self.biosphere_matrix = scipy.sparse.csr_matrix(
            (values, (self._bio_coo_rows, self._bio_coo_cols)),
            shape=self._bio_shape,
        )

    # ------------------------------------------------------------------
    # Static matrix update helpers
    # ------------------------------------------------------------------

    @staticmethod
    def update_techmatrix(process_name: str, report_dict: dict, tech_matrix: dict) -> None:
        """
        Updates the `tech_matrix` according to the  `report_dict`. `tech_matrix` is an
        instance of ``LCA_matrix.tech_matrix``. Useful for Monte Carlo simulation, and
        optimization.

        :param process_name: Name of the life-cycle process model.
        :type process_name: str

        :param report_dict: LCI report of the life-cycle process model (``swolfpy_processmodels.ProcessModel.report()``).
        :type report_dict: dict

        :param tech_matrix:
        :type tech_matrix: ``LCA_matrix.tech_matrix``

        """
        for material, value in report_dict["Technosphere"].items():
            for key2, value2 in value.items():
                if not np.isnan(value2):
                    if ((key2), (process_name, material)) in tech_matrix.keys():
                        if tech_matrix[((key2), (process_name, material))] != value2:
                            tech_matrix[((key2), (process_name, material))] = value2
                    else:
                        raise KeyError(
                            "Exchange {} is calculated but not exist in LCA technosphere".format(
                                ((key2), (process_name, material))
                            )
                        )
                else:
                    raise ValueError(
                        "Amount for Exchange {} is Nan. The amount should be number, check the calculations in the process model".format(
                            ((key2), (process_name, material))
                        )
                    )

        for material, value in report_dict["Waste"].items():
            for key2, value2 in value.items():
                # Remove prefix from material name in the case of Transfer Station
                if report_dict["process name"][1] == "Transfer_Station":
                    if "DryRes" == material[0:6] or "WetRes" == material[0:6]:
                        material_ = material[7:]
                    elif "ORG" == material[0:3] or "REC" == material[0:3]:
                        material_ = material[4:]
                else:
                    material_ = material
                key2 = (process_name + "_product", material_ + "_" + key2)
                if not np.isnan(value2):
                    if ((key2), (process_name, material)) in tech_matrix.keys():
                        if tech_matrix[((key2), (process_name, material))] != value2:
                            tech_matrix[((key2), (process_name, material))] = value2
                    else:
                        raise KeyError(
                            "Exchange {} is calculated but not exist in LCA technosphere".format(
                                ((key2), (process_name, material))
                            )
                        )

                else:
                    raise ValueError(
                        "Amount for Exchange {} is Nan. The amount should be number, check the calculations in the process model".format(
                            ((key2), (process_name, material))
                        )
                    )

            ### Adding activity for transport between the collection and treatment processes
            if "LCI" in report_dict.keys():
                for y in report_dict["LCI"].keys():
                    for m in report_dict["LCI"][y].keys():
                        for n in report_dict["LCI"][y][m].keys():
                            if "biosphere3" not in n:
                                if not np.isnan(report_dict["LCI"][y][m][n]):
                                    if (
                                        n,
                                        (process_name + "_product", y + "_" + "to" + "_" + m),
                                    ) in tech_matrix.keys():
                                        if (
                                            tech_matrix[
                                                (
                                                    n,
                                                    (
                                                        process_name + "_product",
                                                        y + "_" + "to" + "_" + m,
                                                    ),
                                                )
                                            ]
                                            != report_dict["LCI"][y][m][n]
                                        ):
                                            tech_matrix[
                                                (
                                                    n,
                                                    (
                                                        process_name + "_product",
                                                        y + "_" + "to" + "_" + m,
                                                    ),
                                                )
                                            ] = report_dict["LCI"][y][m][n]
                                    else:
                                        raise KeyError(
                                            "Exchange {} is calculated but not exist in LCA technosphere".format(
                                                (
                                                    n,
                                                    (
                                                        process_name + "_product",
                                                        y + "_" + "to" + "_" + m,
                                                    ),
                                                )
                                            )
                                        )
                                else:
                                    raise ValueError(
                                        """Amount for Exchange {} is Nan. The amount should be number,
                                                     check the calculations in the process model""".format(
                                            (
                                                n,
                                                (
                                                    process_name + "_product",
                                                    y + "_" + "to" + "_" + m,
                                                ),
                                            )
                                        )
                                    )

    @staticmethod
    def update_biomatrix(process_name: str, report_dict: dict, bio_matrix: dict) -> None:
        """
        Updates the `bio_matrix` according to the  report_dict. `bio_matrix` is an
        instance of ``LCA_matrix.bio_matrix``. Useful for Monte Carlo simulation, and
        optimization.

        :param process_name: Name of the life-cycle process model.
        :type process_name: str

        :param report_dict: LCI report of the life-cycle process model (``swolfpy_processmodels.ProcessModel.report()``).
        :type report_dict: dict

        :param bio_matrix:
        :type bio_matrix: ``LCA_matrix.bio_matrix``

        """
        for material, value in report_dict["Biosphere"].items():
            for key2, value2 in value.items():
                if not np.isnan(value2):
                    if bio_matrix[((key2), (process_name, material))] != value2:
                        bio_matrix[((key2), (process_name, material))] = value2
                else:
                    raise ValueError(
                        "Amount for Exchange {} is Nan. The amount should be number, check the calculations in the process model".format(
                            ((key2), (process_name, material))
                        )
                    )
            ### Adding activity for collection cost
            if "LCI" in report_dict.keys():
                for y in report_dict["LCI"].keys():
                    for m in report_dict["LCI"][y].keys():
                        for n in report_dict["LCI"][y][m].keys():
                            if "biosphere3" in n:
                                if not np.isnan(report_dict["LCI"][y][m][n]):
                                    if (
                                        n,
                                        (process_name + "_product", y + "_" + "to" + "_" + m),
                                    ) in bio_matrix.keys():
                                        if (
                                            bio_matrix[
                                                (
                                                    n,
                                                    (
                                                        process_name + "_product",
                                                        y + "_" + "to" + "_" + m,
                                                    ),
                                                )
                                            ]
                                            != report_dict["LCI"][y][m][n]
                                        ):
                                            bio_matrix[
                                                (
                                                    n,
                                                    (
                                                        process_name + "_product",
                                                        y + "_" + "to" + "_" + m,
                                                    ),
                                                )
                                            ] = report_dict["LCI"][y][m][n]
                                    else:
                                        raise KeyError(
                                            "Exchange {} is calculated but not exist in LCA biosphere".format(
                                                (
                                                    n,
                                                    (
                                                        process_name + "_product",
                                                        y + "_" + "to" + "_" + m,
                                                    ),
                                                )
                                            )
                                        )
                                else:
                                    raise ValueError(
                                        """Amount for Exchange {} is Nan. The amount should be number,
                                                     check the calculations in the process model""".format(
                                            (
                                                n,
                                                (
                                                    process_name + "_product",
                                                    y + "_" + "to" + "_" + m,
                                                ),
                                            )
                                        )
                                    )

    @staticmethod
    def get_mass_flow(LCA, process: str) -> float:
        """
        Calculates the total mass of flows to process based on the `supply_array` in
        ``bw2calc.lca.LCA``.

        :param LCA: LCA object.
        :type LCA: ``bw2calc.lca.LCA`` or ``swolfpy.LCA_matrix.LCA_matrix``

        :param process: Name of the process databases.
        :type process: str

        :return: Total mass of flows to `process`
        :rtype: float

        """
        mass = 0
        for i in LCA.dicts.activity:
            if process == i[0]:
                unit = bd.get_node(database=i[0], code=i[1]).as_dict()["unit"].split(" ")
                if len(unit) > 1:
                    mass += LCA.supply_array[LCA.dicts.activity[i]] * float(unit[0])
                else:
                    mass += LCA.supply_array[LCA.dicts.activity[i]]
        return mass

    @staticmethod
    def get_mass_flow_comp(LCA, process: str, index) -> pd.Series:
        """
        Calculates the mass of flows to process based on the `index` and `supply_array` in
        ``bw2calc.lca.LCA``.

        :param LCA: LCA object.
        :type LCA: ``bw2calc.lca.LCA`` or ``swolfpy.LCA_matrix.LCA_matrix``

        :param process: Name of the process databases.
        :type process: str

        :param index: Name of the process databases.
        :type index: str

        :return: Pandas series with mass flows as values and index as rows.
        :rtype: pandas.core.series.Series

        """
        mass = pd.Series(np.zeros(len(index)), index=index)
        for i in LCA.dicts.activity:
            if process == i[0]:
                for j in index:
                    if j == i[1]:
                        unit = bd.get_node(database=i[0], code=i[1]).as_dict()["unit"].split(" ")
                        if len(unit) > 1:
                            mass[j] += LCA.supply_array[LCA.dicts.activity[i]] * float(unit[0])
                        else:
                            mass[j] += LCA.supply_array[LCA.dicts.activity[i]]
        return mass
