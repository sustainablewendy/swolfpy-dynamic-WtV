# -*- coding: utf-8 -*-
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from . import PyWOLF_Resource_rc


class Ui_MC_Results(object):
    def setupUi(self, MC_Results):
        if not MC_Results.objectName():
            MC_Results.setObjectName("MC_Results")
        MC_Results.resize(1180, 1068)
        icon = QIcon()
        icon.addFile(":/ICONS/PySWOLF_ICONS/PySWOLF.ico", QSize(), QIcon.Normal, QIcon.Off)
        MC_Results.setWindowIcon(icon)
        self.gridLayout = QGridLayout(MC_Results)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QTabWidget(MC_Results)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setEnabled(True)
        self.tabWidget.setMinimumSize(QSize(400, 0))
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.MC_Data = QWidget()
        self.MC_Data.setObjectName("MC_Data")
        self.gridLayout_2 = QGridLayout(self.MC_Data)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.MC_Res_Table = QTableView(self.MC_Data)
        self.MC_Res_Table.setObjectName("MC_Res_Table")

        self.gridLayout_2.addWidget(self.MC_Res_Table, 0, 0, 1, 1)

        self.tabWidget.addTab(self.MC_Data, "")
        self.MC_Plot = QWidget()
        self.MC_Plot.setObjectName("MC_Plot")
        self.gridLayout_5 = QGridLayout(self.MC_Plot)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.scrollArea = QScrollArea(self.MC_Plot)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1136, 1004))
        self.gridLayout_6 = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.splitter = QSplitter(self.scrollAreaWidgetContents)
        self.splitter.setObjectName("splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.frame = QFrame(self.splitter)
        self.frame.setObjectName("frame")
        self.frame.setMinimumSize(QSize(0, 900))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.gridLayout_7 = QGridLayout(self.frame)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.splitter_2 = QSplitter(self.frame)
        self.splitter_2.setObjectName("splitter_2")
        self.splitter_2.setOrientation(Qt.Vertical)
        self.groupBox = QGroupBox(self.splitter_2)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_3 = QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")

        self.gridLayout_3.addWidget(self.label_3, 1, 3, 1, 1)

        self.hexbin = QRadioButton(self.groupBox)
        self.hexbin.setObjectName("hexbin")

        self.gridLayout_3.addWidget(self.hexbin, 1, 5, 1, 1)

        self.y_axis = QComboBox(self.groupBox)
        self.y_axis.setObjectName("y_axis")
        self.y_axis.setMinimumSize(QSize(400, 0))

        self.gridLayout_3.addWidget(self.y_axis, 1, 1, 1, 1)

        self.scatter = QRadioButton(self.groupBox)
        self.scatter.setObjectName("scatter")

        self.gridLayout_3.addWidget(self.scatter, 1, 4, 1, 1)

        self.x_axis = QComboBox(self.groupBox)
        self.x_axis.setObjectName("x_axis")

        self.gridLayout_3.addWidget(self.x_axis, 0, 1, 1, 1)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName("label")

        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)

        self.Update_plot = QPushButton(self.groupBox)
        self.Update_plot.setObjectName("Update_plot")
        icon1 = QIcon()
        icon1.addFile(":/ICONS/PySWOLF_ICONS/Update.png", QSize(), QIcon.Normal, QIcon.Off)
        self.Update_plot.setIcon(icon1)

        self.gridLayout_3.addWidget(self.Update_plot, 1, 6, 1, 1)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")

        self.gridLayout_3.addWidget(self.label_2, 1, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer, 1, 7, 1, 1)

        self.plot = QWidget(self.groupBox)
        self.plot.setObjectName("plot")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plot.sizePolicy().hasHeightForWidth())
        self.plot.setSizePolicy(sizePolicy)
        self.plot.setMinimumSize(QSize(0, 100))

        self.gridLayout_3.addWidget(self.plot, 2, 0, 1, 8)

        self.splitter_2.addWidget(self.groupBox)
        self.groupBox_2 = QGroupBox(self.splitter_2)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_4 = QGridLayout(self.groupBox_2)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName("label_4")

        self.gridLayout_4.addWidget(self.label_4, 1, 0, 2, 1)

        self.plot_dist = QWidget(self.groupBox_2)
        self.plot_dist.setObjectName("plot_dist")
        sizePolicy.setHeightForWidth(self.plot_dist.sizePolicy().hasHeightForWidth())
        self.plot_dist.setSizePolicy(sizePolicy)
        self.plot_dist.setMinimumSize(QSize(0, 100))

        self.gridLayout_4.addWidget(self.plot_dist, 3, 0, 1, 6)

        self.label_5 = QLabel(self.groupBox_2)
        self.label_5.setObjectName("label_5")

        self.gridLayout_4.addWidget(self.label_5, 0, 0, 1, 1)

        self.param = QComboBox(self.groupBox_2)
        self.param.setObjectName("param")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.param.sizePolicy().hasHeightForWidth())
        self.param.setSizePolicy(sizePolicy1)
        self.param.setMinimumSize(QSize(400, 0))

        self.gridLayout_4.addWidget(self.param, 0, 1, 1, 3)

        self.hist = QRadioButton(self.groupBox_2)
        self.hist.setObjectName("hist")

        self.gridLayout_4.addWidget(self.hist, 2, 1, 1, 1)

        self.box = QRadioButton(self.groupBox_2)
        self.box.setObjectName("box")

        self.gridLayout_4.addWidget(self.box, 2, 2, 1, 1)

        self.density = QRadioButton(self.groupBox_2)
        self.density.setObjectName("density")

        self.gridLayout_4.addWidget(self.density, 2, 3, 1, 1)

        self.Update_dist_fig = QPushButton(self.groupBox_2)
        self.Update_dist_fig.setObjectName("Update_dist_fig")
        self.Update_dist_fig.setIcon(icon1)

        self.gridLayout_4.addWidget(self.Update_dist_fig, 2, 4, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_2, 2, 5, 1, 1)

        self.splitter_2.addWidget(self.groupBox_2)

        self.gridLayout_7.addWidget(self.splitter_2, 0, 0, 1, 1)

        self.splitter.addWidget(self.frame)

        self.gridLayout_6.addWidget(self.splitter, 0, 0, 1, 1)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_5.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.tabWidget.addTab(self.MC_Plot, "")
        self.MC_Corr = QWidget()
        self.MC_Corr.setObjectName("MC_Corr")
        self.gridLayout_9 = QGridLayout(self.MC_Corr)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.groupBox_3 = QGroupBox(self.MC_Corr)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_8 = QGridLayout(self.groupBox_3)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.label_6 = QLabel(self.groupBox_3)
        self.label_6.setObjectName("label_6")

        self.gridLayout_8.addWidget(self.label_6, 0, 0, 1, 1)

        self.Corr_Impact = QComboBox(self.groupBox_3)
        self.Corr_Impact.setObjectName("Corr_Impact")
        self.Corr_Impact.setMinimumSize(QSize(400, 0))

        self.gridLayout_8.addWidget(self.Corr_Impact, 0, 1, 1, 1)

        self.Update_Corr_fig = QPushButton(self.groupBox_3)
        self.Update_Corr_fig.setObjectName("Update_Corr_fig")
        self.Update_Corr_fig.setIcon(icon1)

        self.gridLayout_8.addWidget(self.Update_Corr_fig, 0, 2, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(589, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_8.addItem(self.horizontalSpacer_3, 0, 3, 1, 1)

        self.Corr_plot = QWidget(self.groupBox_3)
        self.Corr_plot.setObjectName("Corr_plot")

        self.gridLayout_8.addWidget(self.Corr_plot, 1, 0, 1, 4)

        self.gridLayout_9.addWidget(self.groupBox_3, 0, 0, 1, 1)

        self.tabWidget.addTab(self.MC_Corr, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(MC_Results)

        self.tabWidget.setCurrentIndex(2)

        QMetaObject.connectSlotsByName(MC_Results)

    # setupUi

    def retranslateUi(self, MC_Results):
        MC_Results.setWindowTitle(
            QCoreApplication.translate("MC_Results", "Monte Carlo Results", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.MC_Data),
            QCoreApplication.translate("MC_Results", "Data", None),
        )
        self.groupBox.setTitle(QCoreApplication.translate("MC_Results", "Plot", None))
        self.label_3.setText(QCoreApplication.translate("MC_Results", "Plot type", None))
        self.hexbin.setText(QCoreApplication.translate("MC_Results", "hexbin", None))
        self.scatter.setText(QCoreApplication.translate("MC_Results", "scatter", None))
        self.label.setText(QCoreApplication.translate("MC_Results", "X axis", None))
        self.Update_plot.setText(QCoreApplication.translate("MC_Results", "Update", None))
        self.label_2.setText(QCoreApplication.translate("MC_Results", "Y axis", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MC_Results", "Distribution", None))
        self.label_4.setText(QCoreApplication.translate("MC_Results", "Plot type", None))
        self.label_5.setText(QCoreApplication.translate("MC_Results", "Parameter", None))
        self.hist.setText(QCoreApplication.translate("MC_Results", "hist", None))
        self.box.setText(QCoreApplication.translate("MC_Results", "box", None))
        self.density.setText(QCoreApplication.translate("MC_Results", "density", None))
        self.Update_dist_fig.setText(QCoreApplication.translate("MC_Results", "Update", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.MC_Plot),
            QCoreApplication.translate("MC_Results", "Plot", None),
        )
        self.groupBox_3.setTitle(QCoreApplication.translate("MC_Results", "Correlation plot", None))
        self.label_6.setText(QCoreApplication.translate("MC_Results", "Impact", None))
        self.Update_Corr_fig.setText(QCoreApplication.translate("MC_Results", "Update", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.MC_Corr),
            QCoreApplication.translate("MC_Results", "Correlation", None),
        )

    # retranslateUi
