# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'glacier.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PyQT5SlackClient(object):
    def setupUi(self, PyQT5SlackClient):
        PyQT5SlackClient.setObjectName("PyQT5SlackClient")
        PyQT5SlackClient.resize(1013, 661)
        self.centralwidget = QtWidgets.QWidget(PyQT5SlackClient)
        self.centralwidget.setObjectName("centralwidget")
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(0, 20, 256, 512))
        self.listWidget.setObjectName("listWidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(910, 560, 88, 34))
        self.pushButton.setObjectName("pushButton")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(0, 0, 60, 20))
        self.label.setObjectName("label")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(320, 500, 541, 87))
        self.textEdit.setObjectName("textEdit")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(280, 20, 701, 451))
        self.textBrowser.setObjectName("textBrowser")
        PyQT5SlackClient.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(PyQT5SlackClient)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1013, 30))
        self.menubar.setObjectName("menubar")
        PyQT5SlackClient.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(PyQT5SlackClient)
        self.statusbar.setObjectName("statusbar")
        PyQT5SlackClient.setStatusBar(self.statusbar)

        self.retranslateUi(PyQT5SlackClient)
        QtCore.QMetaObject.connectSlotsByName(PyQT5SlackClient)

    def retranslateUi(self, PyQT5SlackClient):
        _translate = QtCore.QCoreApplication.translate
        PyQT5SlackClient.setWindowTitle(_translate("PyQT5SlackClient", "Glacier"))
        self.pushButton.setText(_translate("PyQT5SlackClient", "Send"))
        self.label.setText(_translate("PyQT5SlackClient", "Channels"))
