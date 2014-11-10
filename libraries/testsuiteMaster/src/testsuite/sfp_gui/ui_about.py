# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_about.ui'
#
# Created: Tue Oct  1 11:49:16 2013
#      by: PyQt4 UI code generator 4.10
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
        Dialog.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(30, 20, 331, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.version_label = QtGui.QLabel(Dialog)
        self.version_label.setGeometry(QtCore.QRect(40, 210, 101, 20))
        self.version_label.setObjectName(_fromUtf8("version_label"))
        self.vendor_rev_label = QtGui.QLabel(Dialog)
        self.vendor_rev_label.setGeometry(QtCore.QRect(150, 190, 201, 20))
        self.vendor_rev_label.setObjectName(_fromUtf8("vendor_rev_label"))
        self.label_79 = QtGui.QLabel(Dialog)
        self.label_79.setGeometry(QtCore.QRect(40, 170, 81, 20))
        self.label_79.setObjectName(_fromUtf8("label_79"))
        self.label_82 = QtGui.QLabel(Dialog)
        self.label_82.setGeometry(QtCore.QRect(40, 189, 71, 21))
        self.label_82.setObjectName(_fromUtf8("label_82"))
        self.sfp_identifier_label = QtGui.QLabel(Dialog)
        self.sfp_identifier_label.setGeometry(QtCore.QRect(150, 170, 201, 20))
        self.sfp_identifier_label.setObjectName(_fromUtf8("sfp_identifier_label"))
        self.version_text = QtGui.QLabel(Dialog)
        self.version_text.setGeometry(QtCore.QRect(150, 210, 101, 20))
        self.version_text.setObjectName(_fromUtf8("version_text"))

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label.setText(_translate("Dialog", "Packet Photonics Test GUI", None))
        self.version_label.setText(_translate("Dialog", "Software Version", None))
        self.vendor_rev_label.setText(_translate("Dialog", "---", None))
        self.label_79.setText(_translate("Dialog", "SFP Identifier", None))
        self.label_82.setText(_translate("Dialog", "Vendor Rev", None))
        self.sfp_identifier_label.setText(_translate("Dialog", "---", None))
        self.version_text.setText(_translate("Dialog", "Software Version", None))

