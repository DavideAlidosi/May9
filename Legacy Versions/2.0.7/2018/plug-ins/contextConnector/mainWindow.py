# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\Maya_Projects\contextConnector\mainWindow.ui'
#
# Created: Wed Dec 28 23:58:04 2016
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtWidgets, QtGui, QtCore

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(266, 277)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(0, 0))
        MainWindow.setMaximumSize(QtCore.QSize(2220, 3000))
        MainWindow.setDocumentMode(False)
        MainWindow.setDockOptions(QtWidgets.QMainWindow.AllowTabbedDocks|QtWidgets.QMainWindow.AnimatedDocks)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSpacing(2)
        self.gridLayout.setContentsMargins(-1, 0, -1, -1)
        self.gridLayout.setObjectName("gridLayout")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 1, 1, 1)
        self.setSource_btn = QtWidgets.QPushButton(self.centralwidget)
        self.setSource_btn.setObjectName("setSource_btn")
        self.gridLayout.addWidget(self.setSource_btn, 1, 0, 1, 1)
        self.setTarget_btn = QtWidgets.QPushButton(self.centralwidget)
        self.setTarget_btn.setObjectName("setTarget_btn")
        self.gridLayout.addWidget(self.setTarget_btn, 1, 2, 1, 1)
        self.target_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.target_lineEdit.setReadOnly(True)
        self.target_lineEdit.setObjectName("target_lineEdit")
        self.gridLayout.addWidget(self.target_lineEdit, 0, 2, 1, 1)
        self.update_btn = QtWidgets.QPushButton(self.centralwidget)
        self.update_btn.setMaximumSize(QtCore.QSize(50, 16777215))
        self.update_btn.setObjectName("update_btn")
        self.gridLayout.addWidget(self.update_btn, 1, 1, 1, 1)
        self.source_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.source_lineEdit.setReadOnly(True)
        self.source_lineEdit.setObjectName("source_lineEdit")
        self.gridLayout.addWidget(self.source_lineEdit, 0, 0, 1, 1)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(2, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.line_5 = QtWidgets.QFrame(self.centralwidget)
        self.line_5.setMinimumSize(QtCore.QSize(0, 10))
        self.line_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.verticalLayout.addWidget(self.line_5)
        self.nodes_label = QtWidgets.QLabel(self.centralwidget)
        self.nodes_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.nodes_label.setAlignment(QtCore.Qt.AlignCenter)
        self.nodes_label.setObjectName("nodes_label")
        self.verticalLayout.addWidget(self.nodes_label)
        self.line_4 = QtWidgets.QFrame(self.centralwidget)
        self.line_4.setEnabled(False)
        self.line_4.setMinimumSize(QtCore.QSize(0, 10))
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.verticalLayout.addWidget(self.line_4)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.sourceAttr_cbox = QtWidgets.QComboBox(self.centralwidget)
        self.sourceAttr_cbox.setEditable(True)
        self.sourceAttr_cbox.setMaxVisibleItems(20)
        self.sourceAttr_cbox.setFrame(True)
        self.sourceAttr_cbox.setObjectName("sourceAttr_cbox")
        self.horizontalLayout.addWidget(self.sourceAttr_cbox)
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setWordWrap(True)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout.addWidget(self.label_5)
        self.targetAttr_cbox = QtWidgets.QComboBox(self.centralwidget)
        self.targetAttr_cbox.setEditable(True)
        self.targetAttr_cbox.setMaxVisibleItems(20)
        self.targetAttr_cbox.setFrame(True)
        self.targetAttr_cbox.setObjectName("targetAttr_cbox")
        self.horizontalLayout.addWidget(self.targetAttr_cbox)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(2, 1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(2)
        self.horizontalLayout_3.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.save_btn = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.save_btn.sizePolicy().hasHeightForWidth())
        self.save_btn.setSizePolicy(sizePolicy)
        self.save_btn.setMinimumSize(QtCore.QSize(75, 30))
        self.save_btn.setMaximumSize(QtCore.QSize(75, 16777215))
        self.save_btn.setObjectName("save_btn")
        self.horizontalLayout_3.addWidget(self.save_btn)
        self.connect_btn = QtWidgets.QPushButton(self.centralwidget)
        self.connect_btn.setMinimumSize(QtCore.QSize(0, 30))
        self.connect_btn.setMaximumSize(QtCore.QSize(1000, 16777215))
        self.connect_btn.setObjectName("connect_btn")
        self.horizontalLayout_3.addWidget(self.connect_btn)
        self.repeat_btn = QtWidgets.QPushButton(self.centralwidget)
        self.repeat_btn.setMinimumSize(QtCore.QSize(75, 30))
        self.repeat_btn.setMaximumSize(QtCore.QSize(75, 16777215))
        self.repeat_btn.setObjectName("repeat_btn")
        self.horizontalLayout_3.addWidget(self.repeat_btn)
        self.horizontalLayout_3.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setMinimumSize(QtCore.QSize(0, 10))
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.verticalLayout.addWidget(self.line_3)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_3.setFont(font)
        self.label_3.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.context_lay = QtWidgets.QVBoxLayout()
        self.context_lay.setSpacing(2)
        self.context_lay.setContentsMargins(-1, 0, -1, -1)
        self.context_lay.setObjectName("context_lay")
        self.verticalLayout.addLayout(self.context_lay)
        self.macross_line = QtWidgets.QFrame(self.centralwidget)
        self.macross_line.setMinimumSize(QtCore.QSize(0, 10))
        self.macross_line.setFrameShape(QtWidgets.QFrame.HLine)
        self.macross_line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.macross_line.setObjectName("macross_line")
        self.verticalLayout.addWidget(self.macross_line)
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_6.setFont(font)
        self.label_6.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.verticalLayout.addWidget(self.label_6)
        self.macross_lay = QtWidgets.QVBoxLayout()
        self.macross_lay.setSpacing(2)
        self.macross_lay.setContentsMargins(-1, 0, -1, -1)
        self.macross_lay.setObjectName("macross_lay")
        self.verticalLayout.addLayout(self.macross_lay)
        spacerItem = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 266, 18))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "Context Connector", None))
        self.label_4.setText(QtWidgets.QApplication.translate("MainWindow", ">", None))
        self.setSource_btn.setText(QtWidgets.QApplication.translate("MainWindow", "Set Source", None))
        self.setTarget_btn.setText(QtWidgets.QApplication.translate("MainWindow", "Set Targets", None))
        self.update_btn.setText(QtWidgets.QApplication.translate("MainWindow", "Update", None))
        self.nodes_label.setText(QtWidgets.QApplication.translate("MainWindow", "DecomposeMatrix > Transform", None))
        self.label_5.setText(QtWidgets.QApplication.translate("MainWindow", "  >  ", None))
        self.save_btn.setText(QtWidgets.QApplication.translate("MainWindow", "Save", None))
        self.connect_btn.setText(QtWidgets.QApplication.translate("MainWindow", "Connect", None))
        self.repeat_btn.setText(QtWidgets.QApplication.translate("MainWindow", "Repeat", None))
        self.label_3.setText(QtWidgets.QApplication.translate("MainWindow", "Context Connection    ", None))
        self.label_6.setText(QtWidgets.QApplication.translate("MainWindow", "Macross    ", None))

