# -*- coding: utf-8 -*-
import os
import warnings

import bw2data as bd
import pandas as pd
import swolfpy_inputdata.data.lcia_methods as m


def import_methods(path_to_methods=None):
    """
    Imports the user defined LCIA methods from the csv files in the path.

    Characterisation factors (CFs) whose biosphere flow cannot be found in
    bw2data are silently skipped with a warning.  This handles two cases:

    * Legacy ecoinvent 3.5 UUIDs that changed in newer biosphere3 datasets
      bundled with bw2io ≥0.9.
    * Custom cost flows (Capital_Cost, etc.) that are only present after
      ``Technosphere.Create_Technosphere()`` has been called; when
      ``import_methods`` is invoked from that method the flows already exist
      so no skipping occurs.

    :param path_to_methods: Directory containing LCIA method CSV files.
        Defaults to the ``lcia_methods`` directory inside
        ``swolfpy_inputdata``.
    :type path_to_methods: str or None
    """
    if not path_to_methods:
        path_to_methods = m.__path__[0]
    files = os.listdir(path_to_methods)
    for f in files:
        if ".csv" not in f:
            continue
        df = pd.read_csv(path_to_methods + "/" + f)
        CF = []
        skipped = 0
        for i in df.index:
            key = eval(df["key"][i])
            # bw2data ≥4.0 Method.write() resolves (db, code) tuples to integer
            # node IDs; validate existence here so we can skip gracefully.
            try:
                bd.get_node(database=key[0], code=key[1])
                CF.append((key, df["value"][i]))
            except bd.errors.UnknownObject:
                skipped += 1

        if skipped:
            warnings.warn(
                f"import_methods: skipped {skipped} characterisation factor(s) in "
                f"'{f}' because the biosphere node was not found in the current "
                "biosphere3 database.  These may be legacy ecoinvent 3.5 UUIDs "
                "not present in the bw2io-bundled biosphere3.",
                stacklevel=2,
            )

        name = eval(f[:-4])
        bd.Method(name).register(
            **{
                "unit": df["unit"][0],
                "num_cfs": len(CF),
                "filename": f,
                "path_source_file": path_to_methods,
            }
        )
        if CF:
            bd.Method(name).write(CF)
    # methods.flush() is called internally by Method.write() in Brightway 2.5
