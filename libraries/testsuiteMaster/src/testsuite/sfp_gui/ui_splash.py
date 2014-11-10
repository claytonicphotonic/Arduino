# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_splash.ui'
#
# Created: Fri Feb 28 17:27:46 2014
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
        Dialog.resize(479, 300)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(50, 260, 411, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.logo = QtGui.QLabel(Dialog)
        self.logo.setGeometry(QtCore.QRect(40, 10, 331, 101))
        self.logo.setText(_fromUtf8(""))
        self.logo.setPixmap(QtGui.QPixmap(_fromUtf8("../../.designer/backup/PP_Logo.jpg")))
        self.logo.setScaledContents(True)
        self.logo.setObjectName(_fromUtf8("logo"))
        self.serial_text = QtGui.QLineEdit(Dialog)
        self.serial_text.setGeometry(QtCore.QRect(110, 190, 331, 23))
        self.serial_text.setObjectName(_fromUtf8("serial_text"))
        self.label_56 = QtGui.QLabel(Dialog)
        self.label_56.setGeometry(QtCore.QRect(20, 160, 71, 16))
        self.label_56.setObjectName(_fromUtf8("label_56"))
        self.label_83 = QtGui.QLabel(Dialog)
        self.label_83.setGeometry(QtCore.QRect(20, 220, 91, 16))
        self.label_83.setObjectName(_fromUtf8("label_83"))
        self.label_78 = QtGui.QLabel(Dialog)
        self.label_78.setGeometry(QtCore.QRect(20, 190, 81, 16))
        self.label_78.setObjectName(_fromUtf8("label_78"))
        self.list_ports = QtGui.QComboBox(Dialog)
        self.list_ports.setGeometry(QtCore.QRect(20, 130, 331, 27))
        self.list_ports.setObjectName(_fromUtf8("list_ports"))
        self.refresh_portlist_button = QtGui.QPushButton(Dialog)
        self.refresh_portlist_button.setGeometry(QtCore.QRect(370, 130, 91, 31))
        self.refresh_portlist_button.setObjectName(_fromUtf8("refresh_portlist_button"))
        self.device_type_combo = QtGui.QComboBox(Dialog)
        self.device_type_combo.setGeometry(QtCore.QRect(110, 160, 111, 24))
        self.device_type_combo.setObjectName(_fromUtf8("device_type_combo"))
        self.data_location_text = QtGui.QLineEdit(Dialog)
        self.data_location_text.setGeometry(QtCore.QRect(110, 220, 331, 23))
        self.data_location_text.setObjectName(_fromUtf8("data_location_text"))

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label_56.setText(_translate("Dialog", "Device Type", None))
        self.label_83.setText(_translate("Dialog", "Data Location", None))
        self.label_78.setText(_translate("Dialog", "Device ID", None))
        self.refresh_portlist_button.setText(_translate("Dialog", "Refresh List", None))
        self.data_location_text.setText(_translate("Dialog", "../data/", None))

