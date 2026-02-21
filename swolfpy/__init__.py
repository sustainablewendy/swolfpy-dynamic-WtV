# -*- coding: utf-8 -*-
"""
@author: msardar2

Solid Waste Optimization Life-cycle Framework in Python(SwolfPy)
"""

import sys
import warnings

from .dynamic_lca import DynamicLCA
from .Monte_Carlo import Monte_Carlo
from .Optimization import Optimization
from .Project import Project
from .swolfpy_method import import_methods
from .Technosphere import Technosphere
from .uuid_migration import BIOSPHERE_UUID_MIGRATION, migrate_biosphere_key, original_biosphere_key

warnings.filterwarnings("ignore", category=RuntimeWarning)

# GUI components require PySide2 (Python ≤3.10) or PySide6 (Python ≥3.11).
# Make them optional so the core LCA engine can be used in headless environments
# (tests, API servers, notebooks) without a Qt installation.
try:
    from PySide2 import QtWidgets

    from .UI.PySWOLF_run import MyQtApp

    _GUI_AVAILABLE = True
except ImportError:  # PySide2 not installed or wrong Python version
    _GUI_AVAILABLE = False
    MyQtApp = None  # type: ignore[assignment,misc]


__all__ = [
    "DynamicLCA",
    "Technosphere",
    "Project",
    "import_methods",
    "Optimization",
    "Monte_Carlo",
    "MyQtApp",
    "SwolfPy",
    "BIOSPHERE_UUID_MIGRATION",
    "migrate_biosphere_key",
    "original_biosphere_key",
]

__version__ = "1.4.0"


class SwolfPy:
    """
    Desktop GUI launcher for SwolfPy. Requires PySide2 (Python ≤3.10) or PySide6.

    On headless environments (servers, CI) where Qt is unavailable, import the
    individual classes directly::

        from swolfpy import Project, Technosphere, Monte_Carlo, Optimization

    """

    def __init__(self):
        if not _GUI_AVAILABLE:
            raise RuntimeError(
                "SwolfPy GUI requires PySide2 (Python ≤3.10) or PySide6 (Python ≥3.11). "
                "Install one of them to use the desktop interface."
            )
        if not QtWidgets.QApplication.instance():
            self.app = QtWidgets.QApplication(sys.argv)
        else:
            self.app = QtWidgets.QApplication.instance()

        self.qt_app = MyQtApp()
        availableGeometry = self.app.desktop().availableGeometry(self.qt_app)
        self.qt_app.resize(availableGeometry.width() * 2 / 3, availableGeometry.height() * 2.85 / 3)
        self.qt_app.show()
        self.app.exec_()
