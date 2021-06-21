# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'login.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_LoginWindow(object):
    def setupUi(self, Ui_MainWindow):
        if not Ui_MainWindow.objectName():
            Ui_MainWindow.setObjectName(u"Ui_MainWindow")
        Ui_MainWindow.resize(800, 600)
        self.centralwidget = QWidget(Ui_MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(170, 41, 431, 171))
        self.gridLayout = QGridLayout(self.widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.lineEdit = QLineEdit(self.widget)
        self.lineEdit.setObjectName(u"lineEdit")

        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 2)

        self.label_2 = QLabel(self.widget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.lineEdit_3 = QLineEdit(self.widget)
        self.lineEdit_3.setObjectName(u"lineEdit_3")

        self.gridLayout.addWidget(self.lineEdit_3, 1, 1, 1, 2)

        self.label_3 = QLabel(self.widget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.lineEdit_2 = QLineEdit(self.widget)
        self.lineEdit_2.setObjectName(u"lineEdit_2")

        self.gridLayout.addWidget(self.lineEdit_2, 2, 1, 1, 2)

        self.pushButton = QPushButton(self.widget)
        self.pushButton.setObjectName(u"pushButton")

        self.gridLayout.addWidget(self.pushButton, 3, 2, 1, 1)

        self.checkBox = QCheckBox(self.widget)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setLayoutDirection(Qt.LeftToRight)
        self.checkBox.setAutoFillBackground(False)

        self.gridLayout.addWidget(self.checkBox, 3, 1, 1, 1)

        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 2)
        self.gridLayout.setColumnStretch(2, 1)
        Ui_MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Ui_MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 24))
        Ui_MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(Ui_MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        Ui_MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(Ui_MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        Ui_MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.retranslateUi(Ui_MainWindow)

        QMetaObject.connectSlotsByName(Ui_MainWindow)
    # setupUi

    def retranslateUi(self, Ui_MainWindow):
        Ui_MainWindow.setWindowTitle(QCoreApplication.translate("LoginWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("LoginWindow", u"URL", None))
        self.label_2.setText(QCoreApplication.translate("LoginWindow", u"Email", None))
        self.label_3.setText(QCoreApplication.translate("LoginWindow", u"Password", None))
        self.pushButton.setText(QCoreApplication.translate("LoginWindow", u"Login", None))
        self.checkBox.setText(QCoreApplication.translate("LoginWindow", u"Save Credentials", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("LoginWindow", u"toolBar", None))
    # retranslateUi

