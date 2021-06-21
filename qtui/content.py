# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'content.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_ContentWindow(object):
    def setupUi(self, Ui_MainWindow):
        if not Ui_MainWindow.objectName():
            Ui_MainWindow.setObjectName(u"Ui_MainWindow")
        Ui_MainWindow.resize(800, 600)
        self.centralwidget = QWidget(Ui_MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tableWidget = QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setGeometry(QRect(-10, -19, 811, 581))
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setMaximumSize(QSize(16777215, 16777215))
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        Ui_MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Ui_MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 24))
        self.menubar.setDefaultUp(True)
        self.menubar.setNativeMenuBar(False)
        Ui_MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(Ui_MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        Ui_MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(Ui_MainWindow)

        QMetaObject.connectSlotsByName(Ui_MainWindow)
    # setupUi

    def retranslateUi(self, Ui_MainWindow):
        Ui_MainWindow.setWindowTitle(QCoreApplication.translate("ContentWindow", u"MainWindow", None))
    # retranslateUi

