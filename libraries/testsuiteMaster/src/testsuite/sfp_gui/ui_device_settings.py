# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_device_settings.ui'
#
# Created: Thu Mar 13 21:34:56 2014
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
        Dialog.resize(484, 613)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(220, 580, 261, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.groupBox_2 = QtGui.QGroupBox(Dialog)
        self.groupBox_2.setGeometry(QtCore.QRect(0, 440, 331, 111))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.label_5 = QtGui.QLabel(self.groupBox_2)
        self.label_5.setGeometry(QtCore.QRect(10, 60, 161, 20))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.label_6 = QtGui.QLabel(self.groupBox_2)
        self.label_6.setGeometry(QtCore.QRect(10, 80, 131, 20))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.differential_voltage = QtGui.QLineEdit(self.groupBox_2)
        self.differential_voltage.setGeometry(QtCore.QRect(180, 60, 71, 23))
        self.differential_voltage.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.differential_voltage.setObjectName(_fromUtf8("differential_voltage"))
        self.software_los = QtGui.QLineEdit(self.groupBox_2)
        self.software_los.setGeometry(QtCore.QRect(180, 80, 71, 23))
        self.software_los.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.software_los.setObjectName(_fromUtf8("software_los"))
        self.los_hardware = QtGui.QCheckBox(self.groupBox_2)
        self.los_hardware.setGeometry(QtCore.QRect(10, 30, 231, 21))
        self.los_hardware.setObjectName(_fromUtf8("los_hardware"))
        self.label_30 = QtGui.QLabel(self.groupBox_2)
        self.label_30.setGeometry(QtCore.QRect(250, 60, 71, 21))
        self.label_30.setObjectName(_fromUtf8("label_30"))
        self.label_31 = QtGui.QLabel(self.groupBox_2)
        self.label_31.setGeometry(QtCore.QRect(250, 80, 71, 21))
        self.label_31.setObjectName(_fromUtf8("label_31"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 40, 91, 21))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(20, 160, 91, 21))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(20, 130, 91, 21))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(20, 100, 91, 21))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_7 = QtGui.QLabel(Dialog)
        self.label_7.setGeometry(QtCore.QRect(20, 70, 91, 21))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.label_8 = QtGui.QLabel(Dialog)
        self.label_8.setGeometry(QtCore.QRect(20, 190, 91, 21))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.label_9 = QtGui.QLabel(Dialog)
        self.label_9.setGeometry(QtCore.QRect(20, 220, 91, 21))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(110, 30, 111, 401))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.power_value = QtGui.QLineEdit(self.groupBox)
        self.power_value.setGeometry(QtCore.QRect(20, 30, 71, 23))
        self.power_value.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.power_value.setObjectName(_fromUtf8("power_value"))
        self.power_min = QtGui.QLineEdit(self.groupBox)
        self.power_min.setGeometry(QtCore.QRect(20, 60, 71, 23))
        self.power_min.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.power_min.setObjectName(_fromUtf8("power_min"))
        self.power_max = QtGui.QLineEdit(self.groupBox)
        self.power_max.setGeometry(QtCore.QRect(20, 90, 71, 23))
        self.power_max.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.power_max.setObjectName(_fromUtf8("power_max"))
        self.power_yellow = QtGui.QLineEdit(self.groupBox)
        self.power_yellow.setGeometry(QtCore.QRect(20, 120, 71, 23))
        self.power_yellow.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.power_yellow.setObjectName(_fromUtf8("power_yellow"))
        self.power_red = QtGui.QLineEdit(self.groupBox)
        self.power_red.setGeometry(QtCore.QRect(20, 150, 71, 23))
        self.power_red.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.power_red.setObjectName(_fromUtf8("power_red"))
        self.groupBox_3 = QtGui.QGroupBox(Dialog)
        self.groupBox_3.setGeometry(QtCore.QRect(240, 10, 121, 421))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.laser_value = QtGui.QLineEdit(self.groupBox_3)
        self.laser_value.setGeometry(QtCore.QRect(20, 30, 71, 23))
        self.laser_value.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.laser_value.setObjectName(_fromUtf8("laser_value"))
        self.laser_min = QtGui.QLineEdit(self.groupBox_3)
        self.laser_min.setGeometry(QtCore.QRect(20, 60, 71, 23))
        self.laser_min.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.laser_min.setObjectName(_fromUtf8("laser_min"))
        self.laser_max = QtGui.QLineEdit(self.groupBox_3)
        self.laser_max.setGeometry(QtCore.QRect(20, 90, 71, 23))
        self.laser_max.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.laser_max.setObjectName(_fromUtf8("laser_max"))
        self.laser_yellow = QtGui.QLineEdit(self.groupBox_3)
        self.laser_yellow.setGeometry(QtCore.QRect(20, 120, 71, 23))
        self.laser_yellow.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.laser_yellow.setObjectName(_fromUtf8("laser_yellow"))
        self.laser_red = QtGui.QLineEdit(self.groupBox_3)
        self.laser_red.setGeometry(QtCore.QRect(20, 150, 71, 23))
        self.laser_red.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.laser_red.setObjectName(_fromUtf8("laser_red"))
        self.laser_time_constant = QtGui.QLineEdit(self.groupBox_3)
        self.laser_time_constant.setGeometry(QtCore.QRect(20, 180, 71, 23))
        self.laser_time_constant.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.laser_time_constant.setObjectName(_fromUtf8("laser_time_constant"))
        self.laser_gain = QtGui.QLineEdit(self.groupBox_3)
        self.laser_gain.setGeometry(QtCore.QRect(20, 210, 71, 23))
        self.laser_gain.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.laser_gain.setObjectName(_fromUtf8("laser_gain"))
        self.laser_phase1 = QtGui.QLineEdit(self.groupBox_3)
        self.laser_phase1.setGeometry(QtCore.QRect(20, 240, 71, 23))
        self.laser_phase1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.laser_phase1.setObjectName(_fromUtf8("laser_phase1"))
        self.laser_max_current = QtGui.QLineEdit(self.groupBox_3)
        self.laser_max_current.setGeometry(QtCore.QRect(20, 270, 71, 23))
        self.laser_max_current.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.laser_max_current.setObjectName(_fromUtf8("laser_max_current"))
        self.label_12 = QtGui.QLabel(self.groupBox_3)
        self.label_12.setGeometry(QtCore.QRect(90, 30, 16, 21))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.label_13 = QtGui.QLabel(self.groupBox_3)
        self.label_13.setGeometry(QtCore.QRect(90, 90, 16, 21))
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.label_14 = QtGui.QLabel(self.groupBox_3)
        self.label_14.setGeometry(QtCore.QRect(90, 60, 16, 21))
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.label_15 = QtGui.QLabel(self.groupBox_3)
        self.label_15.setGeometry(QtCore.QRect(90, 120, 21, 21))
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.label_16 = QtGui.QLabel(self.groupBox_3)
        self.label_16.setGeometry(QtCore.QRect(90, 150, 21, 21))
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.label_17 = QtGui.QLabel(self.groupBox_3)
        self.label_17.setGeometry(QtCore.QRect(90, 180, 21, 21))
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.label_18 = QtGui.QLabel(self.groupBox_3)
        self.label_18.setGeometry(QtCore.QRect(90, 210, 21, 21))
        self.label_18.setObjectName(_fromUtf8("label_18"))
        self.label_19 = QtGui.QLabel(self.groupBox_3)
        self.label_19.setGeometry(QtCore.QRect(90, 270, 21, 21))
        self.label_19.setObjectName(_fromUtf8("label_19"))
        self.label_20 = QtGui.QLabel(self.groupBox_3)
        self.label_20.setGeometry(QtCore.QRect(90, 240, 21, 21))
        self.label_20.setObjectName(_fromUtf8("label_20"))
        self.tec_coeff_a = QtGui.QLineEdit(self.groupBox_3)
        self.tec_coeff_a.setGeometry(QtCore.QRect(20, 300, 71, 23))
        self.tec_coeff_a.setText(_fromUtf8(""))
        self.tec_coeff_a.setMaxLength(16383)
        self.tec_coeff_a.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.tec_coeff_a.setObjectName(_fromUtf8("tec_coeff_a"))
        self.tec_coeff_b = QtGui.QLineEdit(self.groupBox_3)
        self.tec_coeff_b.setGeometry(QtCore.QRect(20, 330, 71, 23))
        self.tec_coeff_b.setText(_fromUtf8(""))
        self.tec_coeff_b.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.tec_coeff_b.setObjectName(_fromUtf8("tec_coeff_b"))
        self.tec_coeff_c = QtGui.QLineEdit(self.groupBox_3)
        self.tec_coeff_c.setGeometry(QtCore.QRect(20, 360, 71, 23))
        self.tec_coeff_c.setText(_fromUtf8(""))
        self.tec_coeff_c.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.tec_coeff_c.setObjectName(_fromUtf8("tec_coeff_c"))
        self.tec_coeff_d = QtGui.QLineEdit(self.groupBox_3)
        self.tec_coeff_d.setGeometry(QtCore.QRect(20, 390, 71, 23))
        self.tec_coeff_d.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.tec_coeff_d.setObjectName(_fromUtf8("tec_coeff_d"))
        self.label_36 = QtGui.QLabel(self.groupBox_3)
        self.label_36.setGeometry(QtCore.QRect(90, 300, 21, 21))
        self.label_36.setObjectName(_fromUtf8("label_36"))
        self.label_37 = QtGui.QLabel(self.groupBox_3)
        self.label_37.setGeometry(QtCore.QRect(90, 330, 21, 21))
        self.label_37.setObjectName(_fromUtf8("label_37"))
        self.label_38 = QtGui.QLabel(self.groupBox_3)
        self.label_38.setGeometry(QtCore.QRect(90, 360, 21, 21))
        self.label_38.setObjectName(_fromUtf8("label_38"))
        self.label_39 = QtGui.QLabel(self.groupBox_3)
        self.label_39.setGeometry(QtCore.QRect(90, 390, 21, 21))
        self.label_39.setObjectName(_fromUtf8("label_39"))
        self.groupBox_4 = QtGui.QGroupBox(Dialog)
        self.groupBox_4.setGeometry(QtCore.QRect(360, 10, 121, 421))
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.etalon_value = QtGui.QLineEdit(self.groupBox_4)
        self.etalon_value.setGeometry(QtCore.QRect(20, 30, 71, 23))
        self.etalon_value.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.etalon_value.setObjectName(_fromUtf8("etalon_value"))
        self.etalon_min = QtGui.QLineEdit(self.groupBox_4)
        self.etalon_min.setGeometry(QtCore.QRect(20, 60, 71, 23))
        self.etalon_min.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.etalon_min.setObjectName(_fromUtf8("etalon_min"))
        self.etalon_max = QtGui.QLineEdit(self.groupBox_4)
        self.etalon_max.setGeometry(QtCore.QRect(20, 90, 71, 23))
        self.etalon_max.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.etalon_max.setObjectName(_fromUtf8("etalon_max"))
        self.etalon_yellow = QtGui.QLineEdit(self.groupBox_4)
        self.etalon_yellow.setGeometry(QtCore.QRect(20, 120, 71, 23))
        self.etalon_yellow.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.etalon_yellow.setObjectName(_fromUtf8("etalon_yellow"))
        self.etalon_red = QtGui.QLineEdit(self.groupBox_4)
        self.etalon_red.setGeometry(QtCore.QRect(20, 150, 71, 23))
        self.etalon_red.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.etalon_red.setObjectName(_fromUtf8("etalon_red"))
        self.etalon_time_constant = QtGui.QLineEdit(self.groupBox_4)
        self.etalon_time_constant.setGeometry(QtCore.QRect(20, 180, 71, 23))
        self.etalon_time_constant.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.etalon_time_constant.setObjectName(_fromUtf8("etalon_time_constant"))
        self.etalon_gain = QtGui.QLineEdit(self.groupBox_4)
        self.etalon_gain.setGeometry(QtCore.QRect(20, 210, 71, 23))
        self.etalon_gain.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.etalon_gain.setObjectName(_fromUtf8("etalon_gain"))
        self.etalon_phase1 = QtGui.QLineEdit(self.groupBox_4)
        self.etalon_phase1.setGeometry(QtCore.QRect(20, 240, 71, 23))
        self.etalon_phase1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.etalon_phase1.setObjectName(_fromUtf8("etalon_phase1"))
        self.etalon_max_current = QtGui.QLineEdit(self.groupBox_4)
        self.etalon_max_current.setGeometry(QtCore.QRect(20, 270, 71, 23))
        self.etalon_max_current.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.etalon_max_current.setObjectName(_fromUtf8("etalon_max_current"))
        self.label_21 = QtGui.QLabel(self.groupBox_4)
        self.label_21.setGeometry(QtCore.QRect(90, 30, 16, 21))
        self.label_21.setObjectName(_fromUtf8("label_21"))
        self.label_22 = QtGui.QLabel(self.groupBox_4)
        self.label_22.setGeometry(QtCore.QRect(90, 60, 16, 21))
        self.label_22.setObjectName(_fromUtf8("label_22"))
        self.label_23 = QtGui.QLabel(self.groupBox_4)
        self.label_23.setGeometry(QtCore.QRect(90, 90, 16, 21))
        self.label_23.setObjectName(_fromUtf8("label_23"))
        self.label_24 = QtGui.QLabel(self.groupBox_4)
        self.label_24.setGeometry(QtCore.QRect(90, 120, 21, 21))
        self.label_24.setObjectName(_fromUtf8("label_24"))
        self.label_25 = QtGui.QLabel(self.groupBox_4)
        self.label_25.setGeometry(QtCore.QRect(90, 150, 21, 21))
        self.label_25.setObjectName(_fromUtf8("label_25"))
        self.label_26 = QtGui.QLabel(self.groupBox_4)
        self.label_26.setGeometry(QtCore.QRect(90, 180, 21, 21))
        self.label_26.setObjectName(_fromUtf8("label_26"))
        self.label_27 = QtGui.QLabel(self.groupBox_4)
        self.label_27.setGeometry(QtCore.QRect(90, 210, 21, 21))
        self.label_27.setObjectName(_fromUtf8("label_27"))
        self.label_28 = QtGui.QLabel(self.groupBox_4)
        self.label_28.setGeometry(QtCore.QRect(90, 270, 21, 21))
        self.label_28.setObjectName(_fromUtf8("label_28"))
        self.label_29 = QtGui.QLabel(self.groupBox_4)
        self.label_29.setGeometry(QtCore.QRect(90, 240, 21, 21))
        self.label_29.setObjectName(_fromUtf8("label_29"))
        self.modulator_on = QtGui.QCheckBox(Dialog)
        self.modulator_on.setGeometry(QtCore.QRect(360, 440, 111, 21))
        self.modulator_on.setObjectName(_fromUtf8("modulator_on"))
        self.label_10 = QtGui.QLabel(Dialog)
        self.label_10.setGeometry(QtCore.QRect(20, 250, 91, 21))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.label_11 = QtGui.QLabel(Dialog)
        self.label_11.setGeometry(QtCore.QRect(20, 280, 101, 16))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.load_button = QtGui.QPushButton(Dialog)
        self.load_button.setGeometry(QtCore.QRect(290, 560, 91, 24))
        self.load_button.setObjectName(_fromUtf8("load_button"))
        self.save_button = QtGui.QPushButton(Dialog)
        self.save_button.setGeometry(QtCore.QRect(390, 560, 91, 24))
        self.save_button.setObjectName(_fromUtf8("save_button"))
        self.defaults_button = QtGui.QPushButton(Dialog)
        self.defaults_button.setGeometry(QtCore.QRect(380, 530, 101, 24))
        self.defaults_button.setObjectName(_fromUtf8("defaults_button"))
        self.label_32 = QtGui.QLabel(Dialog)
        self.label_32.setGeometry(QtCore.QRect(20, 310, 101, 16))
        self.label_32.setObjectName(_fromUtf8("label_32"))
        self.label_33 = QtGui.QLabel(Dialog)
        self.label_33.setGeometry(QtCore.QRect(20, 340, 101, 16))
        self.label_33.setObjectName(_fromUtf8("label_33"))
        self.label_34 = QtGui.QLabel(Dialog)
        self.label_34.setGeometry(QtCore.QRect(20, 370, 101, 16))
        self.label_34.setObjectName(_fromUtf8("label_34"))
        self.label_35 = QtGui.QLabel(Dialog)
        self.label_35.setGeometry(QtCore.QRect(20, 400, 101, 16))
        self.label_35.setObjectName(_fromUtf8("label_35"))

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Device Settings", None))
        self.groupBox_2.setTitle(_translate("Dialog", "LOS", None))
        self.label_5.setText(_translate("Dialog", "Differential Output Voltage", None))
        self.label_6.setText(_translate("Dialog", "Software Defined LOS", None))
        self.los_hardware.setText(_translate("Dialog", "LOS of signal hardware controlled", None))
        self.label_30.setText(_translate("Dialog", "ADC Counts", None))
        self.label_31.setText(_translate("Dialog", "ADC Counts", None))
        self.label.setText(_translate("Dialog", "Set Value", None))
        self.label_2.setText(_translate("Dialog", "Red Alarm", None))
        self.label_3.setText(_translate("Dialog", "Yellow Alarm", None))
        self.label_4.setText(_translate("Dialog", "Maximum", None))
        self.label_7.setText(_translate("Dialog", "Minimum", None))
        self.label_8.setText(_translate("Dialog", "Time Constant", None))
        self.label_9.setText(_translate("Dialog", "Gain", None))
        self.groupBox.setTitle(_translate("Dialog", "Output Power", None))
        self.groupBox_3.setTitle(_translate("Dialog", "Laser TEC", None))
        self.label_12.setText(_translate("Dialog", "°C", None))
        self.label_13.setText(_translate("Dialog", "°C", None))
        self.label_14.setText(_translate("Dialog", "°C", None))
        self.label_15.setText(_translate("Dialog", "Δ°C", None))
        self.label_16.setText(_translate("Dialog", "Δ°C", None))
        self.label_17.setText(_translate("Dialog", "µs", None))
        self.label_18.setText(_translate("Dialog", "N/A", None))
        self.label_19.setText(_translate("Dialog", "N/A", None))
        self.label_20.setText(_translate("Dialog", "N/A", None))
        self.label_36.setText(_translate("Dialog", "N/A", None))
        self.label_37.setText(_translate("Dialog", "N/A", None))
        self.label_38.setText(_translate("Dialog", "N/A", None))
        self.label_39.setText(_translate("Dialog", "N/A", None))
        self.groupBox_4.setTitle(_translate("Dialog", "Etalon TEC", None))
        self.label_21.setText(_translate("Dialog", "°C", None))
        self.label_22.setText(_translate("Dialog", "°C", None))
        self.label_23.setText(_translate("Dialog", "°C", None))
        self.label_24.setText(_translate("Dialog", "Δ°C", None))
        self.label_25.setText(_translate("Dialog", "Δ°C", None))
        self.label_26.setText(_translate("Dialog", "µs", None))
        self.label_27.setText(_translate("Dialog", "N/A", None))
        self.label_28.setText(_translate("Dialog", "N/A", None))
        self.label_29.setText(_translate("Dialog", "N/A", None))
        self.modulator_on.setText(_translate("Dialog", "Modulator On", None))
        self.label_10.setText(_translate("Dialog", "Phase 1", None))
        self.label_11.setText(_translate("Dialog", "Maximum Current", None))
        self.load_button.setText(_translate("Dialog", "Load Settings", None))
        self.save_button.setText(_translate("Dialog", "Save Settings", None))
        self.defaults_button.setText(_translate("Dialog", "Load Defaults", None))
        self.label_32.setText(_translate("Dialog", "TEC Coeff [A]", None))
        self.label_33.setText(_translate("Dialog", "TEC Coeff [B]", None))
        self.label_34.setText(_translate("Dialog", "TEC Coeff [C]", None))
        self.label_35.setText(_translate("Dialog", "TEC Coeff [D]", None))

