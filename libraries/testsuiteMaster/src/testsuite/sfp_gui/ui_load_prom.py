# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_load_prom.ui'
#
# Created: Mon Mar 10 17:42:03 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(223, 140)
        self.load_prom_button = QtGui.QPushButton(Dialog)
        self.load_prom_button.setGeometry(QtCore.QRect(10, 110, 91, 24))
        self.load_prom_button.setObjectName(_fromUtf8("load_prom_button"))
        self.ok_button = QtGui.QPushButton(Dialog)
        self.ok_button.setGeometry(QtCore.QRect(110, 110, 91, 24))
        self.ok_button.setFlat(False)
        self.ok_button.setObjectName(_fromUtf8("ok_button"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 201, 51))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.progressBar = QtGui.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(10, 80, 191, 23))
        self.progressBar.setMaximum(1024)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Invalid Device", None))
        self.load_prom_button.setText(_translate("Dialog", "Load PROM", None))
        self.ok_button.setText(_translate("Dialog", "OK", None))
        self.label.setText(_translate("Dialog", "The attached device is not a valid device", None))

