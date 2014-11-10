# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 10:53:00 2013

@author: bay
"""

import sys
import time
import datetime
import socket
import os
import math

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QPalette
from PyQt4 import QtGui
from PyQt4 import QtCore
import serial.tools.list_ports
import numpy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as ml
import scipy.ndimage as ndimage

from . ui_sweeptest import Ui_MainWindow
from . ui_about import Ui_Dialog as AboutDialog
from . ui_current_maximums import Ui_Dialog as MaximumsDialog
from  .ui_device_settings import Ui_Dialog as DeviceSettingsDialog
from . ui_etalon_alignment import Ui_Dialog as EtalonAlignmentDialog
from . ui_splash import Ui_Dialog as SplashDialog
from . ui_load_prom import Ui_Dialog as LoadPROMDialog
from testsuite.instruments import testrig
from testsuite.instruments import LambdaInserter  
#import testrig
from . strictdoublevalidator import StrictDoubleValidator
from testsuite.instruments import AQ6331
from testsuite.instruments import HP86120B
from testsuite.instruments import LDT5910B
from testsuite.instruments import gpib_ethernet_socket
from testsuite.instruments import K2420

# FOR TESTING USE ONLY
# There should never be uncommented in production
# from testsuite.instruments import temp_controller_dummy as LDT5910B
# from testsuite.instruments import gpib_ethernet_socket_dummy as gpib_ethernet_socket
# from testsuite.instruments import keithley_dummy as K2420

VERSION_STRING = "0.10"
FORMAT_STRING = ".4f"
FORMAT_STRING_DEVICE_SETTINGS = ".2f"

TEC_VOLTAGE_DROP = 0.7

class SweepTest(QMainWindow):
    
    def __init__(self):
        QWidget.__init__(self)

        # Set up the user interface from Designer.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.label_29.setPixmap(QtGui.QPixmap("testsuite/sfp_gui/PP_Logo.png"))

        # Setup data
        self.rig = None
        #self.osa = None
        
        #Setup Menu
        self.ui.actionExit.triggered.connect(self.exit_slot)
        self.ui.actionAbout.triggered.connect(self.about_slot)
        self.ui.actionMaximums.triggered.connect(self.maximums_slot)
        self.ui.actionDevice_Settings.triggered.connect(self.device_settings_slot)
        self.ui.actionEtalon_Alignment.triggered.connect(self.etalon_alignment_slot)

        # Connect up the buttons.
        self.ui.disconnect_button.clicked.connect(self.disconnect_slot)
        self.ui.basic_scan_button.clicked.connect(self.basic_scan_slot)
        self.ui.control_mirror1_button.clicked.connect(self.control_mirror1_slot)
        self.ui.control_laser_phase_button.clicked.connect(self.control_laser_phase_slot)
        self.ui.control_gain_button.clicked.connect(self.control_gain_slot)
        self.ui.control_phase1_button.clicked.connect(self.control_phase1_slot)
        self.ui.control_mirror2_button.clicked.connect(self.control_mirror2_slot)
        self.ui.control_soa1_button.clicked.connect(self.control_soa1_slot)
        self.ui.control_soa2_button.clicked.connect(self.control_soa2_slot)
        self.ui.iv_curves_button.clicked.connect(self.iv_curves_slot)
        self.ui.control_zero_laser_button.clicked.connect(self.control_zero_laser_slot)
        self.ui.control_load_currents_button.clicked.connect(self.control_load_currents_slot)
        self.ui.control_save_currents_button.clicked.connect(self.control_save_currents_slot)
        self.ui.control_mod1_bias_button.clicked.connect(self.control_modulator_1_bias_slot)
        self.ui.control_mod2_bias_button.clicked.connect(self.control_modulator_2_bias_slot)
        self.ui.control_mod_chirp_button.clicked.connect(self.control_modulator_chirp_slot)
        self.ui.control_mod_amplitude_button.clicked.connect(self.control_modulator_amplitude_slot)
        self.ui.control_itu_channel_read.clicked.connect(self.control_itu_read_slot)
        self.ui.control_itu_channel_write.clicked.connect(self.control_itu_write_slot)
        self.ui.control_wavelength_set_button.clicked.connect(self.control_wavelength_set_slot)
        self.ui.control_offset_button.clicked.connect(self.control_offset_slot)
        self.ui.control_save_map_button.clicked.connect(self.control_save_map_slot)
        self.ui.control_load_map_button.clicked.connect(self.control_load_map_slot)
        self.ui.reload_wavelenth_button.clicked.connect(self.reload_wavelength_slot)
        self.ui.reload_i2c_button.clicked.connect(self.reload_i2c_slot)
        self.ui.soft_reset_button.clicked.connect(self.soft_reset_slot)
        self.ui.minima_load_button.clicked.connect(self.minima_load_data_slot)
        self.ui.minima_find_button.clicked.connect(self.minima_find_slot)
        self.ui.minima_output_file_button.clicked.connect(self.minima_output_file_slot)
        self.ui.minima_save_config.clicked.connect(self.minima_save_config_slot)
        self.ui.minima_load_config.clicked.connect(self.minima_load_config_slot)
        self.ui.osa_load_button.clicked.connect(self.osa_load_data_slot)
        self.ui.osa_output_file_button.clicked.connect(self.osa_output_file_slot)
        self.ui.osa_find_wavelengths_button.clicked.connect(self.osa_find_wavelengths_slot)
        self.ui.flash_read_button.clicked.connect(self.flash_read_slot)
        self.ui.flash_write_button.clicked.connect(self.flash_write_slot)
        self.ui.write_back_memmap_button.clicked.connect(self.write_memmap_init_file)
        self.ui.load_lambda_prom.clicked.connect(self.load_lambda_init_file)
        self.ui.flash_read_file_button.clicked.connect(self.flash_read_file_slot)
        self.ui.flash_write_file_button.clicked.connect(self.flash_write_file_slot)
        self.ui.stability_button.clicked.connect(self.stability_test_slot)
        self.ui.lambda_add_button.clicked.connect(self.lambda_add_slot)
        self.ui.lambda_scan_button.clicked.connect(self.lambda_scan_slot)
        self.ui.lambda_save_button.clicked.connect(self.lambda_save_slot)
        self.ui.lambda_load_button.clicked.connect(self.lambda_load_slot)
        
        # Setup sliders
        self.ui.control_mirror1_slider.valueChanged.connect(self.control_mirror1_slider_slot)
        self.ui.control_laser_phase_slider.valueChanged.connect(self.control_laser_phase_slider_slot)
        self.ui.control_gain_slider.valueChanged.connect(self.control_gain_slider_slot)
        self.ui.control_phase1_slider.valueChanged.connect(self.control_phase1_slider_slot)
        self.ui.control_mirror2_slider.valueChanged.connect(self.control_mirror2_slider_slot)
        self.ui.control_soa1_slider.valueChanged.connect(self.control_soa1_slider_slot)
        self.ui.control_soa2_slider.valueChanged.connect(self.control_soa2_slider_slot)

        # Setup return
        self.ui.control_mirror1_current.returnPressed.connect(self.control_mirror1_slot)
        self.ui.control_laser_phase_current.returnPressed.connect(self.control_laser_phase_slot)
        self.ui.control_gain_current.returnPressed.connect(self.control_gain_slot)
        self.ui.control_phase1_current.returnPressed.connect(self.control_phase1_slot)
        self.ui.control_mirror2_current.returnPressed.connect(self.control_mirror2_slot)
        self.ui.control_soa1_current.returnPressed.connect(self.control_soa1_slot)
        self.ui.control_soa2_current.returnPressed.connect(self.control_soa2_slot)
        self.ui.control_mod1_bias_voltage.returnPressed.connect(self.control_modulator_1_bias_slot)
        self.ui.control_mod2_bias_voltage.returnPressed.connect(self.control_modulator_2_bias_slot)
        self.ui.control_mod_chirp_voltage.returnPressed.connect(self.control_modulator_chirp_slot)
        self.ui.control_mod_amplitude_voltage.returnPressed.connect(self.control_modulator_amplitude_slot)
        
        # Setup comboboxes
        # self.ui.averaging_combo.activated.connect(self.averaging_slot)
        
        # Averaging comboboxes
        self.ui.averaging_combo_1.activated.connect(lambda: self.averaging_slot(1, self.ui.averaging_combo_1))
        self.ui.averaging_combo_2.activated.connect(lambda: self.averaging_slot(2, self.ui.averaging_combo_2))
        self.ui.averaging_combo_3.activated.connect(lambda: self.averaging_slot(3, self.ui.averaging_combo_3))
        self.ui.averaging_combo_4.activated.connect(lambda: self.averaging_slot(4, self.ui.averaging_combo_4))
        self.ui.averaging_combo_5.activated.connect(lambda: self.averaging_slot(5, self.ui.averaging_combo_5))
        self.ui.averaging_combo_6.activated.connect(lambda: self.averaging_slot(6, self.ui.averaging_combo_6))
        self.ui.averaging_combo_7.activated.connect(lambda: self.averaging_slot(7, self.ui.averaging_combo_7))
        self.ui.averaging_combo_8.activated.connect(lambda: self.averaging_slot(8, self.ui.averaging_combo_8))
        self.ui.averaging_combo_9.activated.connect(lambda: self.averaging_slot(9, self.ui.averaging_combo_9))
        self.ui.averaging_combo_10.activated.connect(lambda: self.averaging_slot(10, self.ui.averaging_combo_10))
        self.ui.averaging_combo_11.activated.connect(lambda: self.averaging_slot(11, self.ui.averaging_combo_11))
        self.ui.averaging_combo_12.activated.connect(lambda: self.averaging_slot(12, self.ui.averaging_combo_12))
        self.ui.averaging_combo_13.activated.connect(lambda: self.averaging_slot(13, self.ui.averaging_combo_13))
        self.ui.averaging_combo_14.activated.connect(lambda: self.averaging_slot(14, self.ui.averaging_combo_14))
        self.ui.averaging_combo_15.activated.connect(lambda: self.averaging_slot(15, self.ui.averaging_combo_15))
        self.ui.averaging_combo_16.activated.connect(lambda: self.averaging_slot(16, self.ui.averaging_combo_16))
        
        #Setup checkboxes
        self.ui.laser_switch.stateChanged.connect(self.laser_switch_slot)
        self.ui.laser_tec_switch.stateChanged.connect(self.laser_tec_switch_slot)
        self.ui.etalon_tec_switch.stateChanged.connect(self.etalon_tec_switch_slot)
        self.ui.apc_switch.stateChanged.connect(self.apc_switch_slot)
        self.ui.non_persist_checkbox.stateChanged.connect(self.non_persist_switch_slot)
        self.ui.locker_switch.stateChanged.connect(self.locker_switch_slot)
        self.ui.power_monitor_check.stateChanged.connect(self.power_monitor_slot)
        
        #Setup Spreadsheets
        self.ui.memory_map_table.setRowCount(8)
        self.ui.memory_map_table.setColumnCount(10)
        self.ui.memory_map_table.setHorizontalHeaderLabels([
            '#', 'Label', 'ADC', 'Voltage', 'Value', 
            '#', 'Label', 'ADC', 'Voltage', 'Value'])
        self.ui.memory_map_table.verticalHeader().hide()
        self.ui.memory_map_table.setColumnWidth(0, 25)
        self.ui.memory_map_table.setColumnWidth(1, 140)
        self.ui.memory_map_table.setColumnWidth(2, 40)
        self.ui.memory_map_table.setColumnWidth(3, 50)
        self.ui.memory_map_table.setColumnWidth(4, 60)
        self.ui.memory_map_table.setColumnWidth(5, 25)
        self.ui.memory_map_table.setColumnWidth(6, 140)
        self.ui.memory_map_table.setColumnWidth(7, 40)
        self.ui.memory_map_table.setColumnWidth(8, 50)
        self.ui.memory_map_table.setColumnWidth(9, 60)
        
        monitor_string = ["Bias Voltage",
                  "Laser Temp",
                  "Etalon Temp",
                  "Laser TEC Current",
                  "Locker TEC Current",
                  "Reference Power In",
                  "Etalon Power In",
                  "LIA Receive Power",
                  "Output Power",
                  "Mirror 1",
                  "Laser Phase",
                  "Gain",
                  "Phase 1",
                  "Mirror 2",
                  "SOA 1",
                  "SOA 2"]
        
        for i in range(self.ui.memory_map_table.rowCount()):
            self.ui.memory_map_table.setRowHeight(i, 25)
            
            item = QtGui.QTableWidgetItem(format(i + 1))
            self.ui.memory_map_table.setItem(i, 0, item)
            item = QtGui.QTableWidgetItem(monitor_string[i])
            self.ui.memory_map_table.setItem(i, 1, item)
            
            item = QtGui.QTableWidgetItem(format(i + 9))
            self.ui.memory_map_table.setItem(i, 5, item)
            item = QtGui.QTableWidgetItem(monitor_string[i + 8])
            self.ui.memory_map_table.setItem(i, 6, item)
            
            
        self.ui.custom_monitor_table.setRowCount(4)
        self.ui.custom_monitor_table.setColumnCount(8)
        self.ui.custom_monitor_table.setHorizontalHeaderLabels([
            'Register', '16-bit', 'Name', 'ADC', 
            'Register', '16-bit', 'Name', 'ADC'])
        self.ui.custom_monitor_table.verticalHeader().hide()
        self.ui.custom_monitor_table.setColumnWidth(0, 55)
        self.ui.custom_monitor_table.setColumnWidth(1, 40)
        self.ui.custom_monitor_table.setColumnWidth(2, 170)
        self.ui.custom_monitor_table.setColumnWidth(3, 50)
        self.ui.custom_monitor_table.setColumnWidth(4, 55)
        self.ui.custom_monitor_table.setColumnWidth(5, 40)
        self.ui.custom_monitor_table.setColumnWidth(6, 170)
        self.ui.custom_monitor_table.setColumnWidth(7, 50)
        
        for i in range(self.ui.custom_monitor_table.rowCount()):
            self.ui.custom_monitor_table.setRowHeight(i, 25)
            
            item = QtGui.QTableWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.ui.custom_monitor_table.setItem(i, 1, item)
            self.ui.custom_monitor_table.setItem(i, 5, item.clone())
        
        self.ui.monitor_values_checkbox.stateChanged.connect(self.monitor_values_slot)
        
        self.ui.lambda_table.itemClicked.connect(self.lambda_table_clicked_slot)
        
        #Initialize timers
        self.uptime_timer = QtCore.QTimer()
        self.uptime_timer.timeout.connect(self.uptime_slot)
        
        self.memory_map_timer = QtCore.QTimer()
        self.memory_map_timer.timeout.connect(self.memory_map_slot)
        
        self.update_header_timer = QtCore.QTimer()
        self.update_header_timer.timeout.connect(self.update_header_slot)
        
        self.update_power_monitor_timer = QtCore.QTimer()
        self.update_power_monitor_timer.timeout.connect(self.update_power_monitor_slot)
        
        self.stability_timer = QtCore.QTimer()
        self.stability_timer.timeout.connect(self.stability_timer_slot)
        
        #Initialize validators
        positive_validator = QtGui.QDoubleValidator()
        positive_validator.setBottom(0)
        
        modulator_bias_validator = StrictDoubleValidator()
        modulator_bias_validator.setBottom(-5)
        modulator_bias_validator.setTop(0)
        
        modulator_drive_validator = StrictDoubleValidator()
        modulator_drive_validator.setBottom(1)
        modulator_drive_validator.setTop(3)
        
        self.ui.control_mod1_bias_voltage.setValidator(modulator_bias_validator)
        self.ui.control_mod2_bias_voltage.setValidator(modulator_bias_validator)
        self.ui.control_mod_chirp_voltage.setValidator(QtGui.QIntValidator(0, (2 ** 16) - 1))
        self.ui.control_mod_amplitude_voltage.setValidator(modulator_drive_validator)
        
        self.ui.control_itu_channel_text.setValidator(QtGui.QIntValidator(0,96))
        self.ui.control_wavelength_index.setValidator(QtGui.QIntValidator(0,96))
        
        self.ui.control_offset_value.setValidator(QtGui.QIntValidator(0, (2 ** 8) - 1))
        
        #self.set_validators()
        
        self.lambda_scan_running = False
        self.iv_running = False
        self.osa_running = False
        self.gpib_ethernet = None
        
        self.splash_screen()

        self.show()
        
# Splash Screen

    def splash_screen(self):
        self.splash_dialog = QDialog()
        self.splash_dialog.ui = SplashDialog()
        self.splash_dialog.ui.setupUi(self.splash_dialog)
        self.splash_dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.splash_dialog.ui.logo.setPixmap(QtGui.QPixmap("testsuite/sfp_gui/PP_Logo.png"))
        self.splash_dialog.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.connect_slot)
        self.splash_dialog.ui.buttonBox.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(self.exit_slot)
        
        self.refresh_portlist()
        
        self.splash_dialog.ui.device_type_combo.addItem("Debug Board")
        self.splash_dialog.ui.device_type_combo.addItem("SFP Breakout")
        self.splash_dialog.ui.device_type_combo.addItem("Dummy Board")
        
        self.splash_dialog.exec_()
        
    def refresh_portlist_slot(self):
        self.refresh_portlist()
        
    def refresh_portlist(self):
        self.splash_dialog.ui.list_ports.clear()
        self.portlist = []
        for porttuple in serial.tools.list_ports.comports():
            self.splash_dialog.ui.list_ports.addItem(porttuple[1] + ' (' + porttuple[0] + ')')
            #self.ui.list_ports_osa.addItem(porttuple[0])
            self.portlist.append(porttuple)
            
    def connect_slot(self):
        if self.splash_dialog.ui.device_type_combo.currentIndex() == testrig.DEVICE_SFP_BREAKOUT:
            self.rig = testrig.Testrig(self.portlist[self.splash_dialog.ui.list_ports.currentIndex()][0], testrig.DEVICE_SFP_BREAKOUT)
            label = self.portlist[self.splash_dialog.ui.list_ports.currentIndex()][1]
        elif self.splash_dialog.ui.device_type_combo.currentIndex() == testrig.DEVICE_DEBUG_BOARD:
            self.rig = testrig.Testrig(self.portlist[self.splash_dialog.ui.list_ports.currentIndex()][0], testrig.DEVICE_DEBUG_BOARD)
            label = self.portlist[self.splash_dialog.ui.list_ports.currentIndex()][1]
        elif self.splash_dialog.ui.device_type_combo.currentIndex() == testrig.DEVICE_DUMMY_BOARD:
            self.rig = testrig.Testrig('', testrig.DEVICE_DUMMY_BOARD)
            label = "DUMMY BOARD"
        else:
            raise IOError("Invalid device type index")
        
        if not self.rig.verify_connection():
            #self.msgbox("The attached device is not a valid device")
            #self.rig = None
            self.prom_dialog = QDialog()
            self.prom_dialog.ui = LoadPROMDialog()
            self.prom_dialog.ui.setupUi(self.prom_dialog)
            self.prom_dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            
            self.prom_dialog.ui.load_prom_button.clicked.connect(self.load_prom_slot)
            self.prom_dialog.ui.ok_button.clicked.connect(self.prom_exit_slot)
            
            self.prom_dialog.exec_()
            
            return
        self.ui.serial_label.setText(label)
#             self.ui.connect_button.setText("DISCONNECT")
#             self.ui.list_ports.setEnabled(False)
        
        self.set_validators()
        
        #Initially set voltage readout values
        mirror1 = format(self.rig.mirror1.read_voltage(), FORMAT_STRING)
        laser_phase = format(self.rig.laser_phase.read_voltage(), FORMAT_STRING)
        gain = format(self.rig.gain.read_voltage(), FORMAT_STRING)
        phase1 = format(self.rig.phase1.read_voltage(), FORMAT_STRING)
        mirror2 = format(self.rig.mirror2.read_voltage(), FORMAT_STRING)
        soa1 = format(self.rig.soa1.read_voltage(), FORMAT_STRING)
        soa2 = format(self.rig.soa2.read_voltage(), FORMAT_STRING)
        
        self.ui.control_mirror1_voltage.setText(mirror1)
        self.ui.control_laser_phase_voltage.setText(laser_phase)
        self.ui.control_gain_voltage.setText(gain)
        self.ui.control_phase1_voltage.setText(phase1)
        self.ui.control_mirror2_voltage.setText(mirror2)
        self.ui.control_soa1_voltage.setText(soa1)
        self.ui.control_soa2_voltage.setText(soa2)
        
        self.currents_from_laser()
        
        self.ui.vendor_name_label.setText(self.rig.read_vendor_name())
        self.ui.vendor_pn_label.setText(self.rig.read_vendor_pn())
        self.ui.firmware_rev.setText(self.rig.read_firmware_rev())
        self.ui.firmware_timestamp.setText(time.asctime(time.localtime(self.rig.read_firmware_timestamp())))
        
        self.uptime_slot()
        self.uptime_timer.start(1000)
        
        self.update_header_slot()
        self.update_header_timer.start(1000)
        
        self.device_id = self.splash_dialog.ui.serial_text.text()
        self.ui.serial_text.setText(self.device_id)
        self.data_location_text = self.splash_dialog.ui.data_location_text.text()
        self.ui.data_location_text.setText(self.data_location_text)
        
        #Setup sweep parameters
        
        self.lambda_ilx = None
        self.lambda_ilx_temp = None
        
        self.lambda_dropdown_list = []
        def mirror1_write(value):
            self.ui.control_mirror1_current.setText(format(value, FORMAT_STRING))
            self.control_mirror1_slot()
        self.lambda_dropdown_list.append(SweepParameter("Mirror 1", 0, 60, .1, mirror1_write, lambda rig, block: block.mirror1.read_voltage(), "Mirr1_current"))
        
        def mirror2_write(value):
            self.ui.control_mirror2_current.setText(format(value, FORMAT_STRING))
            self.control_mirror2_slot()
        self.lambda_dropdown_list.append(SweepParameter("MIrror 2", 0, 90, .1, mirror2_write, lambda rig, block: block.mirror2.read_voltage(), "Mirr2_current"))
        
        def laser_phase_write(value):
            self.ui.control_laser_phase_current.setText(format(value, FORMAT_STRING))
            self.control_laser_phase_slot()
        self.lambda_dropdown_list.append(SweepParameter("Laser Phase", 0, 20, .1, laser_phase_write, lambda rig, block: block.laser_phase.read_voltage(), "laser_phase_current"))
        
        def gain_write(value):
            self.ui.control_gain_current.setText(format(value, FORMAT_STRING))
            self.control_gain_slot()
        self.lambda_dropdown_list.append(SweepParameter("Gain", 0, 180, .1, gain_write, lambda rig, block: block.gain.read_voltage(), "gain_current"))
        
        def soa1_write(value):
            self.ui.control_soa1_current.setText(format(value, FORMAT_STRING))
            self.control_soa1_slot()
        self.lambda_dropdown_list.append(SweepParameter("SOA 1", 0, 300, .1, soa1_write, lambda rig, block: block.soa1.read_voltage(), "soa1_current"))
        
        def soa2_write(value):
            self.ui.control_soa2_current.setText(format(value, FORMAT_STRING))
            self.control_soa2_slot()
        self.lambda_dropdown_list.append(SweepParameter("SOA 2", 0, 100, .1, soa2_write, lambda rig, block: block.soa2.read_voltage(), "soa2_current"))
        
        def ilx_external_init():
            if self.gpib_ethernet is None:
                self.gpib_ethernet = gpib_ethernet_socket.GPIBEthernet(self.ui.hardware_ip.text(), 1234)
            self.lambda_ilx_external = LDT5910B.TEC(self.gpib_ethernet, self.ui.hardware_ilx_external_gpib.text())
        
        def ilx_external_close():
            self.lambda_ilx_external = None
            self.lambda_ilx_external_temp = None
            if self.gpib_ethernet is not None:
                self.gpib_ethernet.closesocket()
                self.gpib_ethernet = None
            
        def ilx_external_read():
            self.lambda_ilx_external_temp = self.lambda_ilx_external.check_temperature()
            return self.lambda_ilx_external_temp
        
        def ilx_external_write(value):
            self.lambda_ilx_external.write_setpoint_temperature(value)
        
        self.lambda_dropdown_list.append(SweepParameter("MZM1 Bias", -5, 0, .1, self.rig.write_mzm1_bias, lambda rig, block: rig.read_mzm1_bias(), "mzm1_bias_voltage"))
        self.lambda_dropdown_list.append(SweepParameter("MZM2 Bias", -5, 0, .1, self.rig.write_mzm2_bias, lambda rig, block: rig.read_mzm2_bias(), "mzm2_bias_voltage"))
        self.lambda_dropdown_list.append(SweepParameter("Wavelength Select", 1, 96, 1, self.rig.write_wavelength, lambda rig, block: 0, "wavelength_index"))
        self.lambda_dropdown_list.append(SweepParameter("Laser Temp", 20, 50, .1, self.rig.set_laser_tec, lambda rig, block: rig.read_laser_temp(), "Laser Temp"))
        self.lambda_dropdown_list.append(SweepParameter("Etalon Temp", 20, 50, .1, self.rig.set_etalon_tec, lambda rig, block: rig.read_etalon_temp(), "Etalon Temp"))
        self.lambda_dropdown_list.append(SweepParameter("ILX (External) Set Temp", 25.0, 75.0, 2.5, ilx_external_write, lambda rig, block: ilx_external_read(), "ilx_set_temp", init_func=ilx_external_init, close_func=ilx_external_close))
        
        self.lambda_sweep_list = []
        
        self.lambda_update_gui()
        
    def prom_exit_slot(self):
        self.rig = None
        self.prom_dialog.close()
        self.splash_screen()
        return
    
    def load_prom_slot(self):
        filename = QtGui.QFileDialog.getOpenFileName(self,
                                                     'Open binary PROM file',
                                                     '',
                                                     '')
        if len(filename) == 0:
            return
            
        file = open(filename, 'rb')
        
        self.prom_dialog.ui.progressBar.setValue(0)
            
        while self.rig.flash_check_busy():
            QtGui.QApplication.processEvents()
        self.rig.flash_enable_direct_control(True)
        self.rig.flash_write_address(458752)
#         self.rig.flash_write(file.read())
        for i in range(1024): #there will always be 1024 bytes read in, no more, no less
            self.prom_dialog.ui.progressBar.setValue(i)
            byte = int(file.read(2),16)
            space_char = int.from_bytes(file.read(1), 'big')
            if((space_char != 32) and i < 1023):
                self.msgbox("The PROM Init File is Improperly Constructed!\nThe Init file should be space delimited, with two characters representing each hex byte")
                break
            self.rig.flash_write_byte(byte)
            QtGui.QApplication.processEvents()
        self.rig.flash_set_read(False)
        self.rig.flash_trigger_readwrite(True)
        while self.rig.flash_check_busy():
            QtGui.QApplication.processEvents()
        self.rig.flash_enable_direct_control(False)
        
        file.close()

# Menu Items

    def etalon_alignment_slot(self):
        self.etalon_dialog = QDialog()
        self.etalon_dialog.ui = EtalonAlignmentDialog()
        self.etalon_dialog.ui.setupUi(self.etalon_dialog)
        self.etalon_dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.etalon_alignment_timer = QtCore.QTimer()
        self.etalon_alignment_timer.timeout.connect(self.etalon_alignment_refresh_slot)
        self.etalon_alignment_timer.start(200)
        
        self.etalon_alignment_refresh_slot()
        
        #self.etalon_dialog.ui.buttonBox.clicked.connect(self.etalon_ok_slot)
        self.etalon_dialog.finished.connect(self.etalon_ok_slot)
        
        self.etalon_dialog.exec_()
        
    def etalon_alignment_refresh_slot(self):
        self.etalon_dialog.ui.reference_power_in_adc.setText(format(self.rig.to_adc(self.rig.read_ref_power())))
        self.etalon_dialog.ui.reference_power_in.setText(format(self.rig.read_ref_power(), FORMAT_STRING))
        self.etalon_dialog.ui.etalon_power_in_adc.setText(format(self.rig.to_adc(self.rig.read_etalon_power())))
        self.etalon_dialog.ui.etalon_power_in.setText(format(self.rig.read_etalon_power(), FORMAT_STRING))
        self.etalon_dialog.ui.output_power_adc.setText(format(self.rig.to_adc(self.rig.read_output_power())))
        self.etalon_dialog.ui.output_power.setText(format(self.rig.read_output_power(), FORMAT_STRING))
        self.etalon_dialog.ui.laser_temp_adc.setText(format(self.rig.to_adc_from_celcius(self.rig.read_laser_temp())))
        self.etalon_dialog.ui.laser_temp.setText(format(self.rig.read_laser_temp(), FORMAT_STRING))
        
    def etalon_ok_slot(self):
        self.etalon_alignment_timer.stop()
        
    def device_settings_slot(self):
        validator8 = QtGui.QIntValidator(0, (2 ** 8) - 1)
        validator12 = QtGui.QIntValidator(0, (2 ** 12) - 1)
        validator16 = QtGui.QIntValidator(0, (2 ** 16) - 1)
        
        def setup_TEC_text(lineedit, readfunction):
            lineedit.setText(format(readfunction()))
            lineedit.setValidator(validator12)
            
        def setup_TEC_gain_text(lineedit, readfunction):
            lineedit.setText(format(readfunction()))
            lineedit.setValidator(validator8)
            
        def setup_TEC_time_text(lineedit, readfunction):
            lineedit.setText(format(readfunction(), '.1f'))
            lineedit.setValidator(StrictDoubleValidator(0,5000,1))
            
        def setup_TEC_current_text(lineedit, readfunction):
            lineedit.setText(format(readfunction(), FORMAT_STRING_DEVICE_SETTINGS))
            lineedit.setValidator(StrictDoubleValidator(0, (2 ** 12) - 1, 4))
            
        def setup_TEC_coeff_text(lineedit, readfunction):
            lineedit.setText(format(readfunction(), FORMAT_STRING_DEVICE_SETTINGS))
            #lineedit.setValidator(StrictDoubleValidator(0, (2 ** 12) - 1, 4))
        
        def setup_TEC_temp_text(lineedit, readfunction):
            try:
                lineedit.setText(format(readfunction(), FORMAT_STRING_DEVICE_SETTINGS))
            except (ValueError, ZeroDivisionError): #These can only occurs if using the nonlinear temp conversions
                lineedit.setText("")
            lineedit.setValidator(StrictDoubleValidator(-78, 70, 4))
        
        self.device_settings_dialog = QDialog()
        self.device_settings_dialog.ui = DeviceSettingsDialog()
        self.device_settings_dialog.ui.setupUi(self.device_settings_dialog)
        self.device_settings_dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        setup_TEC_text(self.device_settings_dialog.ui.power_value, self.rig.read_laser_apc_dac)
        setup_TEC_text(self.device_settings_dialog.ui.power_min, self.rig.read_laser_apc_min_dac)
        setup_TEC_text(self.device_settings_dialog.ui.power_max, self.rig.read_laser_apc_max_dac)
        setup_TEC_text(self.device_settings_dialog.ui.power_yellow, self.rig.read_laser_apc_yellow_dac)
        setup_TEC_text(self.device_settings_dialog.ui.power_red, self.rig.read_laser_apc_red_dac)
        
        setup_TEC_temp_text(self.device_settings_dialog.ui.laser_value, self.rig.read_laser_tec)
        setup_TEC_temp_text(self.device_settings_dialog.ui.laser_min, self.rig.read_laser_tec_min) # Due to the negative slope of the conversion, the max of degrees is the min of ADC!
        setup_TEC_temp_text(self.device_settings_dialog.ui.laser_max, self.rig.read_laser_tec_max) 
        setup_TEC_temp_text(self.device_settings_dialog.ui.laser_yellow, self.rig.read_laser_tec_yellow)
        setup_TEC_temp_text(self.device_settings_dialog.ui.laser_red, self.rig.read_laser_tec_red)
        setup_TEC_time_text(self.device_settings_dialog.ui.laser_time_constant, self.rig.read_laser_tec_time)
        setup_TEC_gain_text(self.device_settings_dialog.ui.laser_gain, self.rig.read_laser_tec_gain)
        setup_TEC_gain_text(self.device_settings_dialog.ui.laser_phase1, self.rig.read_laser_tec_phase1)
        setup_TEC_current_text(self.device_settings_dialog.ui.laser_max_current, self.rig.read_laser_max_current)
        setup_TEC_coeff_text(self.device_settings_dialog.ui.tec_coeff_a, self.rig.read_laser_tec_coeff_a)
        setup_TEC_coeff_text(self.device_settings_dialog.ui.tec_coeff_b, self.rig.read_laser_tec_coeff_b)
        setup_TEC_coeff_text(self.device_settings_dialog.ui.tec_coeff_c, self.rig.read_laser_tec_coeff_c)
        setup_TEC_coeff_text(self.device_settings_dialog.ui.tec_coeff_d, self.rig.read_laser_tec_coeff_d)
        
        setup_TEC_temp_text(self.device_settings_dialog.ui.etalon_value, self.rig.read_etalon_tec)
        setup_TEC_temp_text(self.device_settings_dialog.ui.etalon_min, self.rig.read_etalon_tec_max) # Due to the negative slope of the conversion, the max of degrees is the min of ADC!
        setup_TEC_temp_text(self.device_settings_dialog.ui.etalon_max, self.rig.read_etalon_tec_min)
        setup_TEC_temp_text(self.device_settings_dialog.ui.etalon_yellow, self.rig.read_etalon_tec_yellow)
        setup_TEC_temp_text(self.device_settings_dialog.ui.etalon_red, self.rig.read_etalon_tec_red)
        setup_TEC_time_text(self.device_settings_dialog.ui.etalon_time_constant, self.rig.read_etalon_tec_time)
        setup_TEC_gain_text(self.device_settings_dialog.ui.etalon_gain, self.rig.read_etalon_tec_gain)
        setup_TEC_gain_text(self.device_settings_dialog.ui.etalon_phase1, self.rig.read_etalon_tec_phase1)
        setup_TEC_current_text(self.device_settings_dialog.ui.etalon_max_current, self.rig.read_etalon_max_current)
        
        self.device_settings_dialog.ui.los_hardware.setChecked(self.rig.read_los_hardware_controlled())
        setup_TEC_text(self.device_settings_dialog.ui.software_los, self.rig.read_software_los_dac)
        setup_TEC_text(self.device_settings_dialog.ui.differential_voltage, self.rig.read_differential_output_dac)
        
        self.device_settings_dialog.ui.modulator_on.setChecked(self.rig.read_modulator_on())
        
        self.device_settings_dialog.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.device_settings_ok_slot)
        self.device_settings_dialog.ui.buttonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.device_settings_apply_slot)
        self.device_settings_dialog.ui.save_button.clicked.connect(self.device_settings_save_slot)
        self.device_settings_dialog.ui.load_button.clicked.connect(self.device_settings_load_slot)
        self.device_settings_dialog.ui.defaults_button.clicked.connect(self.device_settings_default_slot)
        
        self.device_settings_dialog.exec_()
        
    def device_settings_save_slot(self):
        filename = QtGui.QFileDialog.getSaveFileName(self,
                                                     'Open device config file',
                                                     '',
                                                     "Device Config File (*.devicecfg)")
        if len(filename) == 0:
            return
        if not filename.endswith('.devicecfg'):
            filename += '.devicecfg'
        
        file = open(filename, 'w')
        file.write(self.device_settings_dialog.ui.power_max.text() + '\n')
        file.write(self.device_settings_dialog.ui.power_min.text() + '\n')
        file.write(self.device_settings_dialog.ui.power_red.text() + '\n')
        file.write(self.device_settings_dialog.ui.power_value.text() + '\n')
        file.write(self.device_settings_dialog.ui.power_yellow.text() + '\n')
        
        file.write(self.device_settings_dialog.ui.laser_gain.text() + '\n')
        file.write(self.device_settings_dialog.ui.laser_phase1.text() + '\n')
        file.write(self.device_settings_dialog.ui.laser_max.text() + '\n')
        file.write(self.device_settings_dialog.ui.laser_max_current.text() + '\n')
        file.write(self.device_settings_dialog.ui.laser_min.text() + '\n')
        file.write(self.device_settings_dialog.ui.laser_red.text() + '\n')
        file.write(self.device_settings_dialog.ui.laser_time_constant.text() + '\n')
        file.write(self.device_settings_dialog.ui.laser_value.text() + '\n')
        file.write(self.device_settings_dialog.ui.laser_yellow.text() + '\n')
        
        file.write(self.device_settings_dialog.ui.etalon_gain.text() + '\n')
        file.write(self.device_settings_dialog.ui.etalon_phase1.text() + '\n')
        file.write(self.device_settings_dialog.ui.etalon_max.text() + '\n')
        file.write(self.device_settings_dialog.ui.etalon_max_current.text() + '\n')
        file.write(self.device_settings_dialog.ui.etalon_min.text() + '\n')
        file.write(self.device_settings_dialog.ui.etalon_red.text() + '\n')
        file.write(self.device_settings_dialog.ui.etalon_time_constant.text() + '\n')
        file.write(self.device_settings_dialog.ui.etalon_value.text() + '\n')
        file.write(self.device_settings_dialog.ui.etalon_yellow.text() + '\n')
        
        file.write(format(self.device_settings_dialog.ui.los_hardware.isChecked()) + '\n')
        file.write(self.device_settings_dialog.ui.differential_voltage.text() + '\n')
        file.write(self.device_settings_dialog.ui.software_los.text() + '\n')
        
        file.write(format(self.device_settings_dialog.ui.modulator_on.isChecked()) + '\n')
        
        file.close()
    
    def device_settings_load_slot(self):
        filename = QtGui.QFileDialog.getOpenFileName(self,
                                                     'Open device config file',
                                                     '',
                                                     "Device Config File (*.devicecfg)")
        if len(filename) == 0:
            return
        
        self.device_settings_load(filename)
        
    def device_settings_load(self, filename):
        file = open(filename, 'r')
        self.device_settings_dialog.ui.power_max.setText(file.readline().splitlines()[0])
        self.device_settings_dialog.ui.power_min.setText(file.readline().splitlines()[0])
        self.device_settings_dialog.ui.power_red.setText(file.readline().splitlines()[0])
        self.device_settings_dialog.ui.power_value.setText(file.readline().splitlines()[0])
        self.device_settings_dialog.ui.power_yellow.setText(file.readline().splitlines()[0])
        
        self.device_settings_dialog.ui.laser_gain.setText(file.readline().splitlines()[0])
        self.device_settings_dialog.ui.laser_phase1.setText(file.readline().splitlines()[0])
        self.device_settings_dialog.ui.laser_max.setText(file.readline().splitlines()[0])
        self.device_settings_dialog.ui.laser_max_current.setText(file.readline().splitlines()[0])
        self.device_settings_dialog.ui.laser_min.setText(file.readline().splitlines()[0])
        self.device_settings_dialog.ui.laser_red.setText(file.readline().splitlines()[0])
        self.device_settings_dialog.ui.laser_time_constant.setText(file.readline().splitlines()[0])
        self.device_settings_dialog.ui.laser_value.setText(file.readline().splitlines()[0])
        self.device_settings_dialog.ui.laser_yellow.setText(file.readline().splitlines()[0])
        
        self.device_settings_dialog.ui.etalon_gain.setText(file.readline().splitlines()[0])
        self.device_settings_dialog.ui.etalon_phase1.setText(file.readline().splitlines()[0])
        self.device_settings_dialog.ui.etalon_max.setText(file.readline().splitlines()[0])
        self.device_settings_dialog.ui.etalon_max_current.setText(file.readline().splitlines()[0])
        self.device_settings_dialog.ui.etalon_min.setText(file.readline().splitlines()[0])
        self.device_settings_dialog.ui.etalon_red.setText(file.readline().splitlines()[0])
        self.device_settings_dialog.ui.etalon_time_constant.setText(file.readline().splitlines()[0])
        self.device_settings_dialog.ui.etalon_value.setText(file.readline().splitlines()[0])
        self.device_settings_dialog.ui.etalon_yellow.setText(file.readline().splitlines()[0])
        
        if file.readline().splitlines()[0] == 'True':
            self.device_settings_dialog.ui.los_hardware.setChecked(True)
        else:
            self.device_settings_dialog.ui.los_hardware.setChecked(False)
        self.device_settings_dialog.ui.differential_voltage.setText(file.readline().splitlines()[0])
        self.device_settings_dialog.ui.software_los.setText(file.readline().splitlines()[0])
        
        if file.readline().splitlines()[0] == 'True':
            self.device_settings_dialog.ui.modulator_on.setChecked(True)
        else:
            self.device_settings_dialog.ui.modulator_on.setChecked(False)
        
        file.close()
        
    def device_settings_default_slot(self):
        filename = "testsuite/sfp_gui/device_settings.defaultconfig"
        self.device_settings_load(filename)
        
    def device_settings_apply_slot(self):
        self.rig.set_laser_apc_dac(int(self.device_settings_dialog.ui.power_value.text()))
        self.rig.set_laser_apc_min_dac(int(self.device_settings_dialog.ui.power_min.text()))
        self.rig.set_laser_apc_max_dac(int(self.device_settings_dialog.ui.power_max.text()))
        self.rig.set_laser_apc_yellow_dac(int(self.device_settings_dialog.ui.power_yellow.text()))
        self.rig.set_laser_apc_red_dac(int(self.device_settings_dialog.ui.power_red.text()))
        
        self.rig.set_laser_tec(float(self.device_settings_dialog.ui.laser_value.text()))
        self.rig.set_laser_tec_max(float(self.device_settings_dialog.ui.laser_max.text())) # Due to the negative slope of the conversion, the max of degrees is the min of ADC!
        self.rig.set_laser_tec_min(float(self.device_settings_dialog.ui.laser_min.text()))
        self.rig.set_laser_tec_yellow(float(self.device_settings_dialog.ui.laser_yellow.text()))
        self.rig.set_laser_tec_red(float(self.device_settings_dialog.ui.laser_red.text()))
        self.rig.set_laser_tec_time(float(self.device_settings_dialog.ui.laser_time_constant.text()))
        self.rig.set_laser_tec_gain(int(self.device_settings_dialog.ui.laser_gain.text()))
        self.rig.set_laser_tec_phase1(int(self.device_settings_dialog.ui.laser_phase1.text()))
        self.rig.set_laser_max_current(float(self.device_settings_dialog.ui.laser_max_current.text()))
        self.rig.set_laser_tec_coeff_a(float(self.device_settings_dialog.ui.tec_coeff_a.text()))
        self.rig.set_laser_tec_coeff_b(float(self.device_settings_dialog.ui.tec_coeff_b.text()))
        self.rig.set_laser_tec_coeff_c(float(self.device_settings_dialog.ui.tec_coeff_c.text()))
        self.rig.set_laser_tec_coeff_d(float(self.device_settings_dialog.ui.tec_coeff_d.text()))
        
        
        self.rig.set_etalon_tec(float(self.device_settings_dialog.ui.etalon_value.text()))
        self.rig.set_etalon_tec_max(float(self.device_settings_dialog.ui.etalon_min.text())) # Due to the negative slope of the conversion, the max of degrees is the min of ADC!
        self.rig.set_etalon_tec_min(float(self.device_settings_dialog.ui.etalon_max.text()))
        self.rig.set_etalon_tec_yellow(float(self.device_settings_dialog.ui.etalon_yellow.text()))
        self.rig.set_etalon_tec_red(float(self.device_settings_dialog.ui.etalon_red.text()))
        self.rig.set_etalon_tec_time(float(self.device_settings_dialog.ui.etalon_time_constant.text()))
        self.rig.set_etalon_tec_gain(int(self.device_settings_dialog.ui.etalon_gain.text()))
        self.rig.set_etalon_tec_phase1(int(self.device_settings_dialog.ui.etalon_phase1.text()))
        self.rig.set_etalon_max_current(float(self.device_settings_dialog.ui.etalon_max_current.text()))
        
        self.rig.set_los_hardware_controlled(self.device_settings_dialog.ui.los_hardware.isChecked())
        self.rig.set_differential_output_dac(int(self.device_settings_dialog.ui.differential_voltage.text()))
        self.rig.set_software_los_dac(int(self.device_settings_dialog.ui.software_los.text()))
        
        self.rig.set_modulator_on(self.device_settings_dialog.ui.modulator_on.isChecked())
        
    def device_settings_ok_slot(self):
        self.device_settings_apply_slot()
        self.device_settings_dialog.close()
        
    def about_slot(self):
        dialog = QDialog()
        dialog.ui = AboutDialog()
        dialog.ui.setupUi(dialog)
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        dialog.ui.version_text.setText(VERSION_STRING)
        
        dialog.ui.sfp_identifier_label.setText(testrig.sfp_string(self.rig.read_sfp_identifier()))
        dialog.ui.vendor_rev_label.setText(self.rig.read_vendor_rev())
        
        dialog.exec_()
        
    def maximums_slot(self):
        self.maximums_dialog = QDialog()
        self.maximums_dialog.ui = MaximumsDialog()
        self.maximums_dialog.ui.setupUi(self.maximums_dialog)
        self.maximums_dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.maximums_dialog.ui.mirror1_maximum.setText(format(self.rig.mirror1.validator.top(), FORMAT_STRING))
        self.maximums_dialog.ui.laser_phase_maximum.setText(format(self.rig.laser_phase.validator.top(), FORMAT_STRING))
        self.maximums_dialog.ui.gain_maximum.setText(format(self.rig.gain.validator.top(), FORMAT_STRING))
        self.maximums_dialog.ui.phase1_maximum.setText(format(self.rig.phase1.validator.top(), FORMAT_STRING))
        self.maximums_dialog.ui.mirror2_maximum.setText(format(self.rig.mirror2.validator.top(), FORMAT_STRING))
        self.maximums_dialog.ui.soa1_maximum.setText(format(self.rig.soa1.validator.top(), FORMAT_STRING))
        self.maximums_dialog.ui.soa2_maximum.setText(format(self.rig.soa2.validator.top(), FORMAT_STRING))
        
        self.maximums_dialog.ui.mirror1_maximum.setValidator(self.rig.mirror1.max_validator)
        self.maximums_dialog.ui.laser_phase_maximum.setValidator(self.rig.laser_phase.max_validator)
        self.maximums_dialog.ui.gain_maximum.setValidator(self.rig.gain.max_validator)
        self.maximums_dialog.ui.phase1_maximum.setValidator(self.rig.phase1.max_validator)
        self.maximums_dialog.ui.mirror2_maximum.setValidator(self.rig.mirror2.max_validator)
        self.maximums_dialog.ui.soa1_maximum.setValidator(self.rig.soa1.max_validator)
        self.maximums_dialog.ui.soa2_maximum.setValidator(self.rig.soa2.max_validator)
        
        self.maximums_dialog.ui.mirror1_dithering.setText(format(self.rig.mirror1.read_dithering(), FORMAT_STRING))
        self.maximums_dialog.ui.laser_phase_dithering.setText(format(self.rig.laser_phase.read_dithering(), FORMAT_STRING))
        self.maximums_dialog.ui.mirror2_dithering.setText(format(self.rig.mirror2.read_dithering(), FORMAT_STRING))
        
        self.maximums_dialog.ui.mirror1_dithering.setValidator(self.rig.mirror1.validator)
        self.maximums_dialog.ui.laser_phase_dithering.setValidator(self.rig.laser_phase.validator)
        self.maximums_dialog.ui.mirror2_dithering.setValidator(self.rig.mirror2.validator)
        
        self.maximums_dialog.ui.mirror1_time_constant.setText(format(self.rig.mirror1.read_time_constant()))
        self.maximums_dialog.ui.laser_phase_time_constant.setText(format(self.rig.laser_phase.read_time_constant()))
        
        self.maximums_dialog.ui.buttonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.maximums_apply_slot)
        
        self.maximums_dialog.ui.save_button.clicked.connect(self.maximums_save_slot)
        self.maximums_dialog.ui.load_button.clicked.connect(self.maximums_load_slot)
        self.maximums_dialog.ui.default_button.clicked.connect(self.maximums_default_slot)
        
        self.maximums_dialog.exec_()
        
    def maximums_apply_slot(self):
        self.rig.mirror1.validator.setTop(float(self.maximums_dialog.ui.mirror1_maximum.text()))
        self.rig.mirror1.write_max_current(float(self.maximums_dialog.ui.mirror1_maximum.text()))
        self.rig.laser_phase.validator.setTop(float(self.maximums_dialog.ui.laser_phase_maximum.text()))
        self.rig.laser_phase.write_max_current(float(self.maximums_dialog.ui.laser_phase_maximum.text()))
        self.rig.gain.validator.setTop(float(self.maximums_dialog.ui.gain_maximum.text()))
        self.rig.gain.write_max_current(float(self.maximums_dialog.ui.gain_maximum.text()))
        self.rig.phase1.validator.setTop(float(self.maximums_dialog.ui.phase1_maximum.text()))
        self.rig.phase1.write_max_current(float(self.maximums_dialog.ui.phase1_maximum.text()))
        self.rig.mirror2.validator.setTop(float(self.maximums_dialog.ui.mirror2_maximum.text()))
        self.rig.mirror2.write_max_current(float(self.maximums_dialog.ui.mirror2_maximum.text()))
        self.rig.soa1.validator.setTop(float(self.maximums_dialog.ui.soa1_maximum.text()))
        self.rig.soa1.write_max_current(float(self.maximums_dialog.ui.soa1_maximum.text()))
        self.rig.soa2.validator.setTop(float(self.maximums_dialog.ui.soa2_maximum.text()))
        self.rig.soa2.write_max_current(float(self.maximums_dialog.ui.soa2_maximum.text()))
        
        self.rig.mirror1.write_dithering(float(self.maximums_dialog.ui.mirror1_dithering.text()))
        self.rig.laser_phase.write_dithering(float(self.maximums_dialog.ui.laser_phase_dithering.text()))
        self.rig.mirror2.write_dithering(float(self.maximums_dialog.ui.mirror2_dithering.text()))
        
        self.rig.mirror1.write_time_constant(float(self.maximums_dialog.ui.mirror1_time_constant.text()))
        self.rig.laser_phase.write_time_constant(float(self.maximums_dialog.ui.laser_phase_time_constant.text()))
        
        self.set_validators()
        
        self.maximums_dialog.close()
        
    def maximums_save_slot(self):
        filename = QtGui.QFileDialog.getSaveFileName(self,
                                                     'Open device config file',
                                                     '',
                                                     "Device Config File (*.devicecfg)")
        if len(filename) == 0:
            return
        if not filename.endswith('.devicecfg'):
            filename += '.devicecfg'
        
        file = open(filename, 'w')
        file.write(self.maximums_dialog.ui.mirror1_maximum.text() + '\n')
        file.write(self.maximums_dialog.ui.mirror1_dithering.text() + '\n')
        file.write(self.maximums_dialog.ui.mirror1_time_constant.text() + '\n')
        file.write(self.maximums_dialog.ui.laser_phase_maximum.text() + '\n')
        file.write(self.maximums_dialog.ui.laser_phase_dithering.text() + '\n')
        file.write(self.maximums_dialog.ui.laser_phase_time_constant.text() + '\n')
        file.write(self.maximums_dialog.ui.gain_maximum.text() + '\n')
        file.write(self.maximums_dialog.ui.phase1_maximum.text() + '\n')
        file.write(self.maximums_dialog.ui.mirror2_maximum.text() + '\n')
        file.write(self.maximums_dialog.ui.mirror2_dithering.text() + '\n')
        file.write(self.maximums_dialog.ui.soa1_maximum.text() + '\n')
        file.write(self.maximums_dialog.ui.soa2_maximum.text() + '\n')
        
        file.close()
        
    def maximums_load(self, filename):
        file = open(filename, 'r')
        
        self.maximums_dialog.ui.mirror1_maximum.setText(file.readline().splitlines()[0])
        self.maximums_dialog.ui.mirror1_dithering.setText(file.readline().splitlines()[0])
        self.maximums_dialog.ui.mirror1_time_constant.setText(file.readline().splitlines()[0])
        self.maximums_dialog.ui.laser_phase_maximum.setText(file.readline().splitlines()[0])
        self.maximums_dialog.ui.laser_phase_dithering.setText(file.readline().splitlines()[0])
        self.maximums_dialog.ui.laser_phase_time_constant.setText(file.readline().splitlines()[0])
        self.maximums_dialog.ui.gain_maximum.setText(file.readline().splitlines()[0])
        self.maximums_dialog.ui.phase1_maximum.setText(file.readline().splitlines()[0])
        self.maximums_dialog.ui.mirror2_maximum.setText(file.readline().splitlines()[0])
        self.maximums_dialog.ui.mirror2_dithering.setText(file.readline().splitlines()[0])
        self.maximums_dialog.ui.soa1_maximum.setText(file.readline().splitlines()[0])
        self.maximums_dialog.ui.soa2_maximum.setText(file.readline().splitlines()[0])
        
        file.close()
        
    def maximums_load_slot(self):
        filename = QtGui.QFileDialog.getOpenFileName(self,
                                                     'Open device config file',
                                                     '',
                                                     "Device Config File (*.devicecfg)")
        if len(filename) == 0:
            return
        self.maximums_load(filename)
        
    def maximums_default_slot(self):
        filename = "testsuite/sfp_gui/maximums.defaultconfig"
        self.maximums_load(filename)

# Header

    def power_monitor_slot(self):
        if self.ui.power_monitor_check.isChecked():
            self.update_power_monitor_slot()
            self.update_power_monitor_timer.start(200)
        else:
            self.update_power_monitor_timer.stop()
        
    def update_power_monitor_slot(self):        
        blockread = testrig.Testrig.LaserBlockRead(self.rig)
        pic_power = blockread.mirror1.read_current() * blockread.mirror1.read_voltage() + \
            blockread.laser_phase.read_current() * blockread.laser_phase.read_voltage() + \
            blockread.gain.read_current() * blockread.gain.read_voltage() + \
            blockread.phase1.read_current() * blockread.phase1.read_voltage() + \
            blockread.mirror2.read_current() * blockread.mirror2.read_voltage() + \
            blockread.soa1.read_current() * blockread.soa1.read_voltage() + \
            blockread.soa2.read_current() * blockread.soa2.read_voltage()
        self.ui.total_pic_power.setText(format(pic_power, FORMAT_STRING))
        
        laser_tec_current = self.rig.read_laser_tec_current()
        self.ui.laser_tec_current.setText(format(laser_tec_current, FORMAT_STRING))
        
        etalon_tec_current = self.rig.read_etalon_tec_current()
        self.ui.etalon_tec_current.setText(format(etalon_tec_current, FORMAT_STRING))
        
        self.ui.tec_power.setText(format(((self.rig.read_laser_tec_power(pic_power) * 1000) + etalon_tec_current * TEC_VOLTAGE_DROP), FORMAT_STRING))
        
    def locker_switch_slot(self):
        if self.ui.locker_switch.isChecked():
            self.rig.set_locker_on(True)
        else:
            self.rig.set_locker_on(False)
            
    def non_persist_switch_slot(self):
        non_persist = self.ui.non_persist_checkbox.isChecked()
        self.rig.non_persistence(non_persist)
            
    def laser_switch_slot(self):
        if self.ui.laser_switch.isChecked():
            self.rig.set_laser_on(True)
        else:
            self.rig.set_laser_on(False)
            
    def laser_tec_switch_slot(self):
        if self.ui.laser_tec_switch.isChecked():
            self.rig.set_laser_tec_on(True)
        else:
            self.rig.set_laser_tec_on(False)
            
    def etalon_tec_switch_slot(self):
        if self.ui.etalon_tec_switch.isChecked():
            self.rig.set_etalon_tec_on(True)
        else:
            self.rig.set_etalon_tec_on(False)
            
    def apc_switch_slot(self):
        if self.ui.apc_switch.isChecked():
            self.rig.set_apc_on(True)
        else:
            self.rig.set_apc_on(False)
    
    def update_header_slot(self):
        def set_color(widget, status_value):
            if status_value == testrig.ALARM_STATUS_RED:
                palette = widget.palette()
                palette.setColor(QPalette.Base, QtCore.Qt.red)
                widget.setPalette(palette)
            elif status_value == testrig.ALARM_STATUS_YELLOW:
                palette = widget.palette()
                palette.setColor(QPalette.Base, QtCore.Qt.yellow)
                widget.setPalette(palette)
            elif status_value == testrig.ALARM_STATUS_GREEN:
                palette = widget.palette()
                palette.setColor(QPalette.Base, QtCore.Qt.green)
                widget.setPalette(palette)
            else:
                raise ValueError("Invalid Status Value")
        
        try:
            self.ui.laser_temp_main.setText(format(self.rig.read_laser_temp(), FORMAT_STRING))
        except (ValueError, ZeroDivisionError):
            self.ui.laser_temp_main.setText("---")
        
        try:
            self.ui.etalon_temp_main.setText(format(self.rig.read_etalon_temp(), FORMAT_STRING))
        except (ValueError, ZeroDivisionError):
            self.ui.etalon_temp_main.setText("---")
            
        self.ui.bias_voltage.setText(format(self.rig.read_bias_voltage(), FORMAT_STRING))
        
        set_color(self.ui.laser_tec_status, self.rig.read_laser_tec_alarm())
        set_color(self.ui.etalon_tec_status, self.rig.read_etalon_tec_alarm())
        set_color(self.ui.laser_status, self.rig.read_laser_alarm())
        
        set_color(self.ui.rx_los_status, int(not(self.rig.read_rx_los())) * 2)
        set_color(self.ui.rx_los_sw_status, int(not(self.rig.read_rx_los_sw())) * 2)
        set_color(self.ui.rx_los_hw_status, int(not(self.rig.read_rx_los_hw())) * 2)
        
    def uptime_slot(self):
        uptime = datetime.timedelta(seconds=int(self.rig.read_uptime() / 1000000))
        self.ui.uptime.setText(str(uptime))
        
    def disconnect_slot(self):
        self.rig = None
        self.ui.serial_label.setText("NOT CONNECTED")
        self.uptime_timer.stop()
        self.memory_map_timer.stop()
        self.update_header_timer.stop()
        
        self.splash_screen()

# Tab: Sweep

    def basic_scan_slot(self):
        pass

# Tab: Lambda Sweep

    def lambda_add_slot(self):
        if len(self.lambda_dropdown_list) > 0:
            self.lambda_sweep_list.append(self.lambda_dropdown_list.pop(self.ui.lambda_add_combo.currentIndex()))
            self.lambda_update_gui()
    
    def lambda_table_clicked_slot(self, item):
        if item.column() in [1, 2, 3]:
            self.ui.lambda_table.editItem(item)
        if item.column() == 6:
            self.lambda_dropdown_list.append(self.lambda_sweep_list.pop(item.row()))
            self.lambda_update_gui()
            
    def lambda_update_gui(self):
        self.ui.lambda_add_combo.clear()
        for item in self.lambda_dropdown_list:
            self.ui.lambda_add_combo.addItem(item.name)
            
        self.ui.lambda_table.setRowCount(0)
        for item in self.lambda_sweep_list:
            item.add_row(self.ui.lambda_table)
            
    def lambda_stop_scan(self, file):
        file.close()
        self.ui.lambda_progress.setValue(0)
        self.ui.lambda_scan_button.setText("Start Sweep")
        self.lambda_scan_running = False
        if self.ui.power_monitor_check.isChecked():
            self.update_power_monitor_timer.start(200)
            
        for parameter in self.lambda_sweep_list:
            if parameter.close_func is not None:
                parameter.close_func()
                
        if self.gpib_ethernet is not None:
            self.gpib_ethernet.closesocket()
            self.gpib_ethernet = None
                
        if self.lambda_ilx_external is not None:
            self.lambda_ilx_external = None

        if self.lambda_ilx_sfp is not None:
            self.lambda_ilx_sfp = None
            
        if self.lambda_ilx_tosa is not None:
            self.lambda_ilx_tosa = None
            
        if self.lambda_power_keithley is not None:
            self.lambda_power_keithley = None
            
        if self.lambda_pic_tec_keithley is not None:
            self.lambda_pic_tec_keithley = None
            
    def lambda_scan_slot(self):
        if not(self.lambda_scan_running):
            #Change button
            #self.lambda_scan_text = self.ui.lambda_scan_button.text()
            self.ui.lambda_scan_button.setText("Stop Sweep")
            self.lambda_scan_running = True
            
            if self.ui.power_monitor_check.isChecked():
                self.update_power_monitor_timer.stop()
                
            #Open data file
            file = open(self.data_location() + 'sweepdata' + format(int(time.time())) + '.csv', 'w')
            self.datafile_header(file)
            file.write('Mirror1,' + self.ui.control_mirror1_current.text() + '\n')
            file.write('Laser Phase,' + self.ui.control_laser_phase_current.text() + '\n')
            file.write('Gain,' + self.ui.control_gain_current.text() + '\n')
            file.write('Phase 1,' + self.ui.control_phase1_current.text() + '\n')
            file.write('MIrror 2,' + self.ui.control_mirror2_current.text() + '\n')
            file.write('SOA1,' + self.ui.control_soa1_current.text() + '\n')
            file.write('SOA2,' + self.ui.control_soa2_current.text() + '\n')
            for item in self.lambda_sweep_list:
                file.write(item.column_name + ',')
            file.write('mirr1_voltage,laser_phase_voltage,gain_voltage,phase1_voltage,mirror2_voltage,soa1_voltage,soa2_voltage,out_power_voltage,laser_temp,etalon_temp,laser_tec_current,etalon_power,reference_power_adc,etalon_power_in,uptime')
            if self.ui.lambda_osa_check.isChecked():
                file.write(',osa_wavelength,osa_power')
            if self.ui.lambda_ilx_external_temp_check.isChecked():
                file.write(',external_temp')
            if self.ui.lambda_ilx_sfp_temp_check.isChecked():
                file.write(',T_SFP')
            if self.ui.lambda_ilx_tosa_temp_check.isChecked():
                file.write(',T_Tosa')
            if self.ui.lambda_keithleys_check.isChecked():
                file.write(',sfp_set_voltage,sfp_current,pic_tec_voltage')
            file.write('\n')
            
            #Validate sweep values and offload spreadsheet
            for row in range(self.ui.lambda_table.rowCount()):
                if float(self.ui.lambda_table.item(row, 2).text()) < float(self.ui.lambda_table.item(row, 1).text()):
                    self.msgbox("Max must be higher than min")
                    self.lambda_stop_scan(file)
                    return
                self.lambda_sweep_list[row].minimum = float(self.ui.lambda_table.item(row, 1).text())
                self.lambda_sweep_list[row].maximum = float(self.ui.lambda_table.item(row, 2).text())
                self.lambda_sweep_list[row].step = float(self.ui.lambda_table.item(row, 3).text())
            
            #Set constant values
            #Any values in the sweep parameters will be overwritten
            self.rig.mirror1.write_current(float(self.ui.control_mirror1_current.text()))
            self.rig.laser_phase.write_current(float(self.ui.control_laser_phase_current.text()))
            self.rig.gain.write_current(float(self.ui.control_gain_current.text()))
            self.rig.phase1.write_current(float(self.ui.control_phase1_current.text()))
            self.rig.mirror2.write_current(float(self.ui.control_mirror2_current.text()))
            self.rig.soa1.write_current(float(self.ui.control_soa1_current.text()))
            self.rig.soa2.write_current(float(self.ui.control_soa2_current.text()))
            
            self.lambda_ilx_external = None
            self.lambda_ilx_external_temp = None
            
            #Initialize sweep parameters
            for parameter in self.lambda_sweep_list:
                if parameter.init_func is not None:
                    parameter.init_func()
                    
            if self.gpib_ethernet is None and (self.ui.lambda_ilx_external_temp_check.isChecked() or self.ui.lambda_ilx_sfp_temp_check.isChecked() or self.ui.lambda_ilx_tosa_temp_check.isChecked() or self.ui.lambda_keithleys_check.isChecked()):
                self.gpib_ethernet = gpib_ethernet_socket.GPIBEthernet(self.ui.hardware_ip.text(), 1234)
                    
            if self.ui.lambda_ilx_external_temp_check.isChecked() and self.lambda_ilx_external is None:
                self.lambda_ilx_external = LDT5910B.TEC(self.gpib_ethernet, self.ui.hardware_ilx_external_gpib.text())
                
            if self.ui.lambda_ilx_sfp_temp_check.isChecked():
                self.lambda_ilx_sfp = LDT5910B.TEC(self.gpib_ethernet, self.ui.hardware_ilx_sfp_gpib.text())
            else:
                self.lambda_ilx_sfp = None
                
            if self.ui.lambda_ilx_tosa_temp_check.isChecked():
                self.lambda_ilx_tosa = LDT5910B.TEC(self.gpib_ethernet, self.ui.hardware_ilx_tosa_gpib.text())
            else:
                self.lambda_ilx_tosa = None
                
            if self.ui.lambda_keithleys_check.isChecked():
                self.lambda_power_keithley = K2420.Keithley(self.gpib_ethernet, self.ui.hardware_sfp_power_gpib.text())
                self.lambda_pic_tec_keithley = K2420.Keithley(self.gpib_ethernet, self.ui.hardware_pic_tec_gpib.text())
            else:
                self.lambda_power_keithley = None
                self.lambda_pic_tec_keithley = None
            
            #Turn laser on
            self.ui.laser_switch.setChecked(True)
            
            #Setup progress bar
            progress_max = 1
            for item in self.lambda_sweep_list:
                progress_max = progress_max * item.iterations()
            self.ui.lambda_progress.setMinimum(0)
            self.ui.lambda_progress.setMaximum(progress_max)
            self.ui.lambda_progress.setValue(0)
            
            self.lambda_sweep(file, 0)
            
            self.rig.device.printdebug()
            self.msgbox("Scan finished")
            self.ui.basic_progress.setValue(0)
            
            self.lambda_stop_scan(file)
        else:
            self.lambda_scan_running = False
            
    def lambda_sweep(self, file, index):
        if not(self.lambda_scan_running):
            self.lambda_stop_scan(file)
            return
        
        if index + 1 <= len(self.lambda_sweep_list):
            for input_value in ml.frange(self.lambda_sweep_list[index].minimum, self.lambda_sweep_list[index].maximum, self.lambda_sweep_list[index].step):
                self.lambda_sweep_list[index].input_func(input_value)
                self.lambda_sweep_list[index].input_value = input_value
                self.ui.lambda_table.item(index, 4).setText(format(input_value, FORMAT_STRING))
                
                self.lambda_sweep(file, index + 1)
        else:
            if float(self.ui.lambda_time_delay.text()) > 0:
                time.sleep(float(self.ui.lambda_time_delay.text()))
            
            blockread = testrig.Testrig.LaserBlockRead(self.rig)
            
            for row in range(len(self.lambda_sweep_list)):
                self.ui.lambda_table.item(row, 5).setText(format(self.lambda_sweep_list[row].output_func(self.rig, blockread), FORMAT_STRING))
                file.write(format(self.lambda_sweep_list[row].input_value, FORMAT_STRING) + ',')
                
            mirror1_adc = blockread.mirror1.read_voltage_adc()
            laser_phase_adc = blockread.laser_phase.read_voltage_adc()
            gain_adc = blockread.gain.read_voltage_adc()
            phase1_adc = blockread.phase1.read_voltage_adc()
            mirror2_adc = blockread.mirror2.read_voltage_adc()
            soa1_adc = blockread.soa1.read_voltage_adc()
            soa2_adc = blockread.soa2.read_voltage_adc()
            
            output_power_adc = self.rig.read_output_power()
            laser_temp = self.rig.read_laser_temp()
            etalon_temp = self.rig.read_etalon_temp()
            laser_tec_current = self.rig.read_laser_tec_current()
            etalon_power = self.rig.read_etalon_tec_current() * TEC_VOLTAGE_DROP
            reference_power_adc = self.rig.to_adc(self.rig.read_ref_power())
            etalon_power_in_adc = self.rig.to_adc(self.rig.read_etalon_power())
            uptime = self.rig.read_uptime()
            
            #Update power monitor
            if self.ui.power_monitor_check.isChecked():
                pic_power = float(self.ui.control_mirror1_current.text()) * blockread.mirror1.read_voltage() + \
                    float(self.ui.control_laser_phase_current.text()) * blockread.laser_phase.read_voltage() + \
                    float(self.ui.control_gain_current.text()) * blockread.gain.read_voltage() + \
                    float(self.ui.control_phase1_current.text()) * blockread.phase1.read_voltage() + \
                    float(self.ui.control_mirror2_current.text()) * blockread.mirror2.read_voltage() + \
                    float(self.ui.control_soa1_current.text()) * blockread.soa1.read_voltage() + \
                    float(self.ui.control_soa2_current.text()) * blockread.soa2.read_voltage()
                self.ui.total_pic_power.setText(format(pic_power, FORMAT_STRING))
                 
                self.ui.laser_tec_current.setText(format(laser_tec_current, FORMAT_STRING))
                 
                etalon_tec_current = self.rig.read_etalon_tec_current() #Only line for power monitor that requires a device read
                self.ui.etalon_tec_current.setText(format(etalon_tec_current, FORMAT_STRING))
                 
                self.ui.tec_power.setText(format(((self.rig.read_laser_tec_power(pic_power, tec_current = laser_tec_current) * 1000) + etalon_tec_current * TEC_VOLTAGE_DROP), FORMAT_STRING))
                
            file.write(format(blockread.mirror1.read_voltage(), FORMAT_STRING) + ',')
            file.write(format(blockread.laser_phase.read_voltage(), FORMAT_STRING) + ',')
            file.write(format(blockread.gain.read_voltage(), FORMAT_STRING) + ',')
            file.write(format(blockread.phase1.read_voltage(), FORMAT_STRING) + ',')
            file.write(format(blockread.mirror2.read_voltage(), FORMAT_STRING) + ',')
            file.write(format(blockread.soa1.read_voltage(), FORMAT_STRING) + ',')
            file.write(format(blockread.soa2.read_voltage(), FORMAT_STRING) + ',')
            file.write(format(output_power_adc, FORMAT_STRING) + ',')
            file.write(format(laser_temp, FORMAT_STRING) + ',')
            file.write(format(etalon_temp, FORMAT_STRING) + ',')
            file.write(format(laser_tec_current, FORMAT_STRING) + ',')
            file.write(format(etalon_power, FORMAT_STRING) + ',')
            file.write(format(reference_power_adc) + ',')
            file.write(format(etalon_power_in_adc) + ',')
            file.write(format(uptime))
            if self.ui.lambda_osa_check.isChecked():
                self.add_osa_columns(file)
            if self.ui.lambda_ilx_external_temp_check.isChecked():
                if self.lambda_ilx_external_temp is None:
                    file.write(',' + format(self.lambda_ilx_external.check_temperature()))
                else:
                    file.write(',' + format(self.lambda_ilx_external_temp))
            if self.ui.lambda_ilx_sfp_temp_check.isChecked():
                file.write(',' + format(self.lambda_ilx_sfp.check_temperature()))
            if self.ui.lambda_ilx_tosa_temp_check.isChecked():
                file.write(',' + format(self.lambda_ilx_tosa.check_temperature()))
            if self.ui.lambda_keithleys_check.isChecked():
                file.write(',' + format(self.lambda_power_keithley.read_voltage()))
                file.write(',' + format(self.lambda_power_keithley.read_current()))
                file.write(',' + format(self.lambda_pic_tec_keithley.read_voltage()))
            file.write('\n')
            
            self.ui.lambda_progress.setValue(self.ui.lambda_progress.value() + 1)
            
            #Check against max voltage
            voltage_max_adc = self.rig.to_adc(float(self.ui.lambda_voltage_max.text()))
            
            QtGui.QApplication.processEvents()
            
            if (mirror1_adc > voltage_max_adc):
                self.msgbox("Mirror 1 voltage above safe value!")
                self.lambda_stop_scan(file)
                return
            if (laser_phase_adc > voltage_max_adc):
                self.msgbox("Laser Phase voltage above safe value!")
                self.lambda_stop_scan(file)
                return
            if (gain_adc > voltage_max_adc):
                self.msgbox("Gain voltage above safe value!")
                self.lambda_stop_scan(file)
                return
            if (phase1_adc > voltage_max_adc):
                self.msgbox("Phase 1 voltage above safe value!")
                self.lambda_stop_scan(file)
                return
            if (mirror2_adc > voltage_max_adc):
                self.msgbox("Mirror 2 voltage above safe value!")
                self.lambda_stop_scan(file)
                return
            if (soa1_adc > voltage_max_adc):
                self.msgbox("SOA 1 voltage above safe value!")
                self.lambda_stop_scan(file)
                return
            if (soa2_adc > voltage_max_adc):
                self.msgbox("SOA 2 voltage above safe value!")
                self.lambda_stop_scan(file)
                return
            
    def lambda_save_slot(self):
        filename = QtGui.QFileDialog.getSaveFileName(self,
                                                     'Open lambda config file',
                                                     '',
                                                     "Lambda Config File (*.lambdacfg)")
        if len(filename) == 0:
            return
        if not filename.endswith('.lambdacfg'):
            filename += '.lambdacfg'
        
        file = open(filename, 'w')
        
        file.write(self.ui.lambda_voltage_max.text() + '\n')
        file.write(str(self.ui.lambda_osa_check.isChecked()) + '\n')
        
        for item in self.lambda_sweep_list:
            file.write(item.name + '\n')
        
        file.close()
        self.ui.lambda_config_file_label.setText(os.path.basename(filename))
        
    def lambda_load_slot(self):
        filename = QtGui.QFileDialog.getOpenFileName(self,
                                                     'Open lambda config file',
                                                     '',
                                                     "Lambda Config File (*.lambdacfg)")
        if len(filename) == 0:
            return
        
        file = open(filename, 'r')
        
        fileline = file.readlines()
        
        self.ui.lambda_voltage_max.setText(fileline[0])
        self.ui.lambda_osa_check.setChecked(fileline[1] == "True")
        
        self.lambda_dropdown_list.extend(self.lambda_sweep_list)
        self.lambda_sweep_list = []
        for name in fileline[2:]:
            print(name)
            for index in range(len(self.lambda_dropdown_list)):
                item = self.lambda_dropdown_list[index]
                if (item.name + '\n' == name):
                    self.lambda_sweep_list.append(self.lambda_dropdown_list.pop(index))
                    break
        self.lambda_update_gui()

# Tab: Monitor Values

    def monitor_values_slot(self):
        if self.ui.monitor_values_checkbox.isChecked():
            self.memory_map_slot()
            self.memory_map_timer.start(1000)
        else:
            self.memory_map_timer.stop()
            
    def memory_map_slot(self):
        def display_monitor(monitor, value_conversion):
            if monitor < 9:
                row = monitor - 1
                col_offset = 0
            else:
                row = monitor - 9
                col_offset = 5
                
            voltage = self.rig.read_monitor_voltage(monitor)
                
            adc_value = self.rig.to_adc(voltage)
            item = QtGui.QTableWidgetItem(format(adc_value))
            self.ui.memory_map_table.setItem(row, col_offset + 2, item)
            item = QtGui.QTableWidgetItem(format(voltage, FORMAT_STRING))
            self.ui.memory_map_table.setItem(row, col_offset + 3, item)
            try:
                item = QtGui.QTableWidgetItem(format(value_conversion(voltage), FORMAT_STRING))
            except (ValueError, ZeroDivisionError):
                item = QtGui.QTableWidgetItem("---")
            self.ui.memory_map_table.setItem(row, col_offset + 4, item)
        
        display_monitor(1, self.rig.to_bias_voltage)
        display_monitor(2, self.rig.to_celsius)
        display_monitor(3, self.rig.to_celsius)
        display_monitor(4, self.rig.to_TEC_current)
        display_monitor(5, self.rig.to_TEC_current)
        display_monitor(6, self.rig.to_power_microamps)
        display_monitor(7, self.rig.to_power_microamps)
        display_monitor(8, self.rig.to_LIA_receive_power)
        display_monitor(9, self.rig.to_power_microamps)
        display_monitor(10, (lambda x: x))
        display_monitor(11, (lambda x: x))
        display_monitor(12, (lambda x: x))
        display_monitor(13, (lambda x: x))
        display_monitor(14, (lambda x: x))
        display_monitor(15, (lambda x: x))
        display_monitor(16, (lambda x: x))
        
        for row in range(self.ui.custom_monitor_table.rowCount()):
            registeritem = self.ui.custom_monitor_table.item(row, 0)
            try:
                register = int(registeritem.text())
                if (self.ui.custom_monitor_table.item(row, 1).checkState() == 0): # 8-bit
                    item = QtGui.QTableWidgetItem(format(self.rig.device.readregister(register)))
                else: # 16-bit
                    item = QtGui.QTableWidgetItem(format(self.rig.read16bit(register)))
            except:
                item = QtGui.QTableWidgetItem("")
            self.ui.custom_monitor_table.setItem(row, 3, item)
            
            registeritem = self.ui.custom_monitor_table.item(row, 4)
            try:
                register = int(registeritem.text())
                if (self.ui.custom_monitor_table.item(row, 5).checkState() == 0): # 8-bit
                    item = QtGui.QTableWidgetItem(format(self.rig.device.readregister(register)))
                else: # 16-bit
                    item = QtGui.QTableWidgetItem(format(self.rig.read16bit(register)))
            except:
                item = QtGui.QTableWidgetItem("")
            self.ui.custom_monitor_table.setItem(row, 7, item)

# Tab: Misc

    def stability_test_slot(self):
        if self.stability_timer.isActive():
            self.stability_end_test()
        else:
            self.stability_osa = self.ui.stability_osa_check.isChecked()
            self.stability_ilx_external = self.ui.stability_ilx_external_check.isChecked()
            self.stability_ilx_sfp = self.ui.stability_ilx_sfp_check.isChecked()
            self.stability_ilx_tosa = self.ui.stability_ilx_tosa_check.isChecked()
            self.stability_keithleys = self.ui.stability_keithleys_check.isChecked()
            self.stability_filename = self.data_location() + 'stabilitytest' + format(int(time.time())) + '.csv'
            file = open(self.stability_filename, 'w')
            self.datafile_header(file)
            file.write('SOA1,' + format(self.rig.soa1.read_current(), FORMAT_STRING) + '\n')
            file.write('SOA2,' + format(self.rig.soa2.read_current(), FORMAT_STRING) + '\n')
            file.write('Gain,' + format(self.rig.gain.read_current(), FORMAT_STRING) + '\n')
            file.write('Phase1,' + format(self.rig.phase1.read_current(), FORMAT_STRING) + '\n')
            
            self.stability_start = datetime.datetime.now().replace(microsecond=0)
            timedelta = datetime.timedelta(hours=float(self.ui.stability_duration.text()))
            self.stability_end = self.stability_start + timedelta
            
            self.ui.stability_start.setText(str(self.stability_start))
            self.ui.stability_end.setText(str(self.stability_end))
            
            file.write('StartTime,' + str(self.stability_start) + '\n')
            file.write('EndTime,' + str(self.stability_end) + '\n')
            file.write('mirror2_current,mirror1_current,laser_phase_current,mirror1_voltage,laser_phase_voltage,gain_voltage,phase1_voltage,mirror1_voltage,soa1_voltage,soa2_voltage,out_power_voltage,laser_temp,etalon_temp,laser_tec_current,etalon_power,reference_power_adc,uptime')
            if self.stability_osa:
                file.write(',osa_wavelength,osa_power')
            if self.stability_ilx_external:
                file.write(',ilx_external_temp')
            if self.stability_ilx_sfp:
                file.write(',T_SFP')
            if self.stability_ilx_tosa:
                file.write(',T_Tosa')
            if self.stability_keithleys:
                file.write(',sfp_set_voltage,sfp_current,pic_tec_voltage')
            file.write('\n')
            file.close
            
            frequency = int(self.ui.stability_frequency.text())
            self.ui.stability_progress.setMaximum(int(timedelta.seconds / frequency))
            self.ui.stability_progress.setValue(0)
            
            self.stability_timer.start(frequency * 1000)
            self.stability_timer_slot()
            
            self.ui.stability_button.setText("Stop")
    
    def stability_timer_slot(self):
        if datetime.datetime.now() > self.stability_end:
            self.stability_end_test()
            return
        else:
            file = open(self.stability_filename, 'a')
            blockread = testrig.Testrig.LaserBlockRead(self.rig)
            
            output_power_adc = self.rig.read_output_power()
            laser_temp = self.rig.read_laser_temp()
            etalon_temp = self.rig.read_etalon_temp()
            laser_tec_current = self.rig.read_laser_tec_current()
            etalon_power = self.rig.read_etalon_tec_current() * TEC_VOLTAGE_DROP
            reference_power_adc = self.rig.read_ref_power()
            uptime = self.rig.read_uptime()
            
            #Output data to file
            file.write(format(blockread.mirror2.read_current(), FORMAT_STRING) + ',')
            file.write(format(blockread.mirror1.read_current(), FORMAT_STRING) + ',')
            file.write(format(blockread.laser_phase.read_current(), FORMAT_STRING) + ',')
            file.write(format(blockread.mirror1.read_voltage(), FORMAT_STRING) + ',')
            file.write(format(blockread.laser_phase.read_voltage(), FORMAT_STRING) + ',')
            file.write(format(blockread.gain.read_voltage(), FORMAT_STRING) + ',')
            file.write(format(blockread.phase1.read_voltage(), FORMAT_STRING) + ',')
            file.write(format(blockread.mirror2.read_voltage(), FORMAT_STRING) + ',')
            file.write(format(blockread.soa1.read_voltage(), FORMAT_STRING) + ',')
            file.write(format(blockread.soa2.read_voltage(), FORMAT_STRING) + ',')
            file.write(format(output_power_adc, FORMAT_STRING) + ',')
            file.write(format(laser_temp, FORMAT_STRING) + ',')
            file.write(format(etalon_temp, FORMAT_STRING) + ',')
            file.write(format(laser_tec_current, FORMAT_STRING) + ',')
            file.write(format(etalon_power, FORMAT_STRING) + ',')
            file.write(format(reference_power_adc) + ',')
            file.write(format(uptime))
            if self.stability_osa:
                self.add_osa_columns(file)
            if self.stability_ilx_external:
                gpib_ethernet = gpib_ethernet_socket.GPIBEthernet(self.ui.hardware_ip.text(), 1234)
                ilx = LDT5910B.TEC(gpib_ethernet, self.ui.hardware_ilx_external_gpib.text())
                file.write(',' + format(ilx.check_temperature()))
                gpib_ethernet.closesocket()
            if self.stability_ilx_sfp:
                gpib_ethernet = gpib_ethernet_socket.GPIBEthernet(self.ui.hardware_ip.text(), 1234)
                ilx = LDT5910B.TEC(gpib_ethernet, self.ui.hardware_ilx_sfp_gpib.text())
                file.write(',' + format(ilx.check_temperature()))
                gpib_ethernet.closesocket()
            if self.stability_ilx_tosa:
                gpib_ethernet = gpib_ethernet_socket.GPIBEthernet(self.ui.hardware_ip.text(), 1234)
                ilx = LDT5910B.TEC(gpib_ethernet, self.ui.hardware_ilx_tosa_gpib.text())
                file.write(',' + format(ilx.check_temperature()))
                gpib_ethernet.closesocket()
            if self.stability_keithleys:
                gpib_ethernet = gpib_ethernet_socket.GPIBEthernet(self.ui.hardware_ip.text(), 1234)
                power_keithley = K2420.Keithley(gpib_ethernet, self.ui.hardware_sfp_power_gpib.text())
                #power_keithley.set_voltage_source(3.3)
                file.write(',' + format(power_keithley.read_voltage()))
                file.write(',' + format(power_keithley.read_current()))
                pic_tec_keithley = K2420.Keithley(gpib_ethernet, self.ui.hardware_pic_tec_gpib.text())
                #pic_tec_keithley.set_current_source(0)
                file.write(',' + format(pic_tec_keithley.read_voltage()))
                gpib_ethernet.closesocket()
            file.write('\n')
            
            file.close()
            
            self.ui.stability_progress.setValue(self.ui.stability_progress.value() + 1)
    
    def stability_end_test(self):
        self.stability_timer.stop()
        self.ui.stability_progress.setMaximum(10)
        self.ui.stability_progress.setValue(10)
        self.ui.stability_button.setText("Start")
        self.ui.stability_start.setText("---")
        self.ui.stability_end.setText("---")
        
    def add_osa_columns(self, file):
        osa = self.osa_return_osa(self.ui.hardware_ip.text(), 1234, self.ui.osa_gpib.text())
        osa.writesweepstart(1525)
        osa.writesweepstop(1565)
        osa.writeresolution(0.05)
        try:
            osa.startsweep()
            while not osa.checksweepfinished():
                QtGui.QApplication.processEvents()
            peaks = osa.readpeak()
            file.write(',' + format(peaks[0]["wavelength"]) + ',' + format(peaks[0]["power"]))
        except socket.timeout:
            pass # Loop through peak finder again
        osa.closesocket()
        
        
    def iv_curve(self, filename_base, step, laser_section):
        self.zero_laser()
        filename = self.data_location() + filename_base + format(int(time.time())) + '.csv'
        file = open(filename, 'w')
        self.datafile_header(file)
        file.write('current,current_dac,voltage,voltage_adc\n')
        
        min_current = laser_section.validator.bottom()
        max_current = laser_section.validator.top()
        
        num_steps = int((max_current - min_current) / step)
        self.ui.iv_curves_progress.setMaximum(num_steps)
        
        for current_dac in range(laser_section.to_dac(min_current), laser_section.to_dac(max_current), laser_section.to_dac(step)):
            if not(self.iv_running):
                file.close()
                self.ui.iv_curves_progress.setValue(0)
                self.ui.iv_curves_button.setText(self.iv_text)
                return
            self.ui.iv_curves_progress.setValue(self.ui.iv_curves_progress.value() + 1)
            QtGui.QApplication.processEvents()
            laser_section.write_current_dac(current_dac)
            file.write(format(laser_section.from_dac(current_dac), FORMAT_STRING) + ',')
            file.write(format(current_dac) + ',')
            voltage = laser_section.read_voltage_adc()
            file.write(format(self.rig.to_voltage(int(voltage)), FORMAT_STRING) + ',')
            file.write(format(int(voltage)))
            file.write('\n')
            
        file.close()
        self.ui.iv_curves_progress.setValue(0)
        
        # Show plot
        #plt.ion()
        data = np.genfromtxt(filename, skip_header=3, names=("current", "current_dac", "voltage", "voltage_adc"), delimiter=',')
        plt.figure()
        plt.plot(data["voltage"], data["current"])
        plt.title(filename_base)
        self.iv_curve_label_axes()
        
        plt.savefig(filename[:-4] + '.png', bbox_inches='tight')
        
        return filename
        
    def iv_curves_slot(self):
        if not(self.iv_running):
            #Change button
            self.iv_text = self.ui.iv_curves_button.text()
            self.ui.iv_curves_button.setText("Stop IV Curves")
            self.iv_running = True
            
            #Turn on laser
            self.ui.laser_switch.setChecked(True)
            
            #Mirror 1
            if self.ui.iv_mirror1.isChecked() and self.iv_running:
                self.iv_curve('IVMirr1', .5, self.rig.mirror1)
            
            #Laser Phase
            if self.ui.iv_laser_phase.isChecked() and self.iv_running:
                self.iv_curve('IVLaserPhase', .25, self.rig.laser_phase)
            
            #Gain
            if self.ui.iv_gain.isChecked() and self.iv_running:
                self.iv_curve('IVGain', .5, self.rig.gain)
            
            #Phase 1
            if self.ui.iv_phase1.isChecked() and self.iv_running:
                self.iv_curve('IVPhase1', .1, self.rig.phase1)
            
            #Mirror 2
            if self.ui.iv_mirror2.isChecked() and self.iv_running:
                self.iv_curve('IVMirr2', .5, self.rig.mirror2)
            
            #SOA 1
            if self.ui.iv_soa1.isChecked() and self.iv_running:
                self.iv_curve('IVSOA1', .5, self.rig.soa1)
            
            #SOA 2
            if self.ui.iv_soa2.isChecked() and self.iv_running:
                self.iv_curve('IVSOA2', .1, self.rig.soa2)
            
            self.zero_laser()
            
            #plt.ion()
            plt.show()
            
            self.ui.iv_curves_button.setText(self.iv_text)
        else:
            self.iv_running = False
        
    def iv_curve_label_axes(self):
        #pass
        plt.ylabel("Current (mA)")
        plt.xlabel("Voltage (V)")

# Tab: Laser Control

    def control_save_map_slot(self):
        filename = QtGui.QFileDialog.getSaveFileName(self,
                                                     'Open wavelength map file',
                                                     '',
                                                     "Wavelength Map File (*.map)")
        if len(filename) == 0:
            return
        if not filename.endswith('.map'):
            filename += '.map'
            
        self.ui.control_map_progress.setValue(0)
        
        file = open(filename, 'wb')
        for index in range(1, 97): # 96 real wavelength table entries
            self.rig.write_table_index(index)
            self.rig.set_table_read(True)
            file.write(self.rig.read_table_bytes())
            
            self.ui.control_map_progress.setValue(index)
            
        emptybytes = bytearray(32)
        for index in range(32): # Dummy values to pad file
            file.write(emptybytes)
        
        file.close()
    
    def control_load_map_slot(self):
        filename = QtGui.QFileDialog.getOpenFileName(self,
                                                     'Open wavelength map file',
                                                     '',
                                                     "Wavelength Map File (*.map)")
        if len(filename) == 0:
            return
        
        self.ui.control_map_progress.setValue(0)
            
        file = open(filename, 'rb')
        for index in range(1, 97):
            self.rig.write_table_bytes(file.read(32)[2:])
            
            self.rig.write_table_index(index)
            self.rig.set_table_read(False)
            
            self.ui.control_map_progress.setValue(index)
        
        file.close()
        
    def control_offset_slot(self):
        self.rig.write_table_offset(int(self.ui.control_offset_value.text()))
        
    def control_wavelength_set_slot(self):
        self.rig.write_wavelength(int(self.ui.control_wavelength_index.text()))
        
    def control_itu_read_slot(self):
        self.rig.write_table_index(int(self.ui.control_itu_channel_text.text()))
        self.rig.set_table_read(True)
        
        self.ui.control_mirror1_current.setText(format(self.rig.mirror1.read_table_current(), FORMAT_STRING))
        self.control_mirror1_slot()
        self.ui.control_laser_phase_current.setText(format(self.rig.laser_phase.read_table_current(), FORMAT_STRING))
        self.control_laser_phase_slot()
        self.ui.control_gain_current.setText(format(self.rig.gain.read_table_current(), FORMAT_STRING))
        self.control_gain_slot()
        self.ui.control_phase1_current.setText(format(self.rig.phase1.read_table_current(), FORMAT_STRING))
        self.control_phase1_slot()
        self.ui.control_mirror2_current.setText(format(self.rig.mirror2.read_table_current(), FORMAT_STRING))
        self.control_mirror2_slot()
        self.ui.control_soa1_current.setText(format(self.rig.soa1.read_table_current(), FORMAT_STRING))
        self.control_soa1_slot()
        self.ui.control_soa2_current.setText(format(self.rig.soa2.read_table_current(), FORMAT_STRING))
        self.control_soa2_slot()
        
        self.ui.control_mod1_bias_voltage.setText(format(self.rig.read_table_mzm1_bias(), FORMAT_STRING)) # 12-bit voltage negative
        self.ui.control_mod2_bias_voltage.setText(format(self.rig.read_table_mzm2_bias(), FORMAT_STRING))
        self.ui.control_mod_amplitude_voltage.setText(format(self.rig.read_table_mzm1_drive(), FORMAT_STRING))
        self.ui.control_mod_chirp_voltage.setText(format(self.rig.read_table_chirp())) # 16-bit
        self.ui.control_offset_value.setText(format(self.rig.read_table_offset())) # 8-bit
        
        self.ui.control_itu_channel_wavelength.setText(format(testrig.to_wavelength(int(self.ui.control_itu_channel_text.text()))  * (10 ** 9), FORMAT_STRING) + " nm")
    
    def control_itu_write_slot(self):
        self.rig.mirror1.write_table_current(float(self.ui.control_mirror1_current.text()))
        self.rig.laser_phase.write_table_current(float(self.ui.control_laser_phase_current.text()))
        self.rig.gain.write_table_current(float(self.ui.control_gain_current.text()))
        self.rig.phase1.write_table_current(float(self.ui.control_phase1_current.text()))
        self.rig.mirror2.write_table_current(float(self.ui.control_mirror2_current.text()))
        self.rig.soa1.write_table_current(float(self.ui.control_soa1_current.text()))
        self.rig.soa2.write_table_current(float(self.ui.control_soa2_current.text()))
        
        self.rig.write_table_mzm1_bias(float(self.ui.control_mod1_bias_voltage.text()))
        self.rig.write_table_mzm1_drive(float(self.ui.control_mod_amplitude_voltage.text()))
        self.rig.write_table_mzm2_bias(float(self.ui.control_mod2_bias_voltage.text()))
        self.rig.write_table_mzm2_drive(1)
        self.rig.write_table_mzm_delay(0)
        self.rig.write_table_chirp(int(self.ui.control_mod_chirp_voltage.text()))
        self.rig.write_table_offset(int(self.ui.control_offset_value.text()))
        
        self.rig.write_table_index(int(self.ui.control_itu_channel_text.text()))
        self.rig.set_table_read(False)
        
        self.ui.control_itu_channel_wavelength.setText(format(testrig.to_wavelength(int(self.ui.control_itu_channel_text.text()))  * (10 ** 9), FORMAT_STRING) + " nm")
        
    def control_modulator_1_bias_slot(self):
        self.rig.write_mzm1_bias(float(self.ui.control_mod1_bias_voltage.text()))
        
    def control_modulator_2_bias_slot(self):
        self.rig.write_mzm2_bias(float(self.ui.control_mod2_bias_voltage.text()))
        
    def control_modulator_chirp_slot(self):
        self.rig.write_chirp(int(self.ui.control_mod_chirp_voltage.text()))
        
    def control_modulator_amplitude_slot(self):
        self.rig.write_mzm1_drive(float(self.ui.control_mod_amplitude_voltage.text()))
        
    def control_load_currents_slot(self):
        filename = QtGui.QFileDialog.getOpenFileName(self,
                                                     'Open laser config file',
                                                     '',
                                                     "Laser Config File (*.lasercfg)")
        if len(filename) == 0:
            return
            
        file = open(filename, 'r')
        self.ui.control_mirror1_current.setText(file.readline().splitlines()[0])
        self.control_mirror1_slot()
        self.ui.control_laser_phase_current.setText(file.readline().splitlines()[0])
        self.control_laser_phase_slot()
        self.ui.control_gain_current.setText(file.readline().splitlines()[0])
        self.control_gain_slot()
        self.ui.control_phase1_current.setText(file.readline().splitlines()[0])
        self.control_phase1_slot()
        self.ui.control_mirror2_current.setText(file.readline().splitlines()[0])
        self.control_mirror2_slot()
        self.ui.control_soa1_current.setText(file.readline().splitlines()[0])
        self.control_soa1_slot()
        self.ui.control_soa2_current.setText(file.readline().splitlines()[0])
        self.control_soa2_slot()
        self.ui.control_offset_value.setText(file.readline().splitlines()[0])
        self.control_offset_slot()
        
        file.close()
        
    def control_save_currents_slot(self):
        filename = QtGui.QFileDialog.getSaveFileName(self,
                                                     'Open laser config file',
                                                     '',
                                                     "Laser Config File (*.lasercfg)")
        if len(filename) == 0:
            return
        if not filename.endswith('.lasercfg'):
            filename += '.lasercfg'
        #if filename[-9:] != '.lasercfg':
        #    filename += '.lasercfg'
        
        file = open(filename, 'w')
        file.write(self.ui.control_mirror1_current.text() + '\n')
        file.write(self.ui.control_laser_phase_current.text() + '\n')
        file.write(self.ui.control_gain_current.text() + '\n')
        file.write(self.ui.control_phase1_current.text() + '\n')
        file.write(self.ui.control_mirror2_current.text() + '\n')
        file.write(self.ui.control_soa1_current.text() + '\n')
        file.write(self.ui.control_soa2_current.text() + '\n')
        file.write(self.ui.control_offset_value.text() + '\n')
        
        file.close()
    
    def control_zero_laser_slot(self):
        self.ui.control_mirror1_current.setText("0")
        self.control_mirror1_slot()
        
        self.ui.control_laser_phase_current.setText("0")
        self.control_laser_phase_slot()
        
        self.ui.control_gain_current.setText("0")
        self.control_gain_slot()
        
        self.ui.control_phase1_current.setText("0")
        self.control_phase1_slot()
        
        self.ui.control_mirror2_current.setText("0")
        self.control_mirror2_slot()
        
        self.ui.control_soa1_current.setText("0")
        self.control_soa1_slot()
        
        self.ui.control_soa2_current.setText("0")
        self.control_soa2_slot()
        
        self.ui.control_mod1_bias_voltage.setText("0")
        self.control_modulator_1_bias_slot()
        self.ui.control_mod2_bias_voltage.setText("0")
        self.control_modulator_2_bias_slot()
        self.ui.control_mod_chirp_voltage.setText("0")
        self.control_modulator_chirp_slot()
        self.ui.control_mod_amplitude_voltage.setText("1")
        self.control_modulator_amplitude_slot()
        
    def control_mirror1_slider_slot(self):
        self.ui.control_mirror1_current.setText(format(self.ui.control_mirror1_slider.value(), FORMAT_STRING))
        self.control_mirror1()
        
    def control_laser_phase_slider_slot(self):
        self.ui.control_laser_phase_current.setText(format(self.ui.control_laser_phase_slider.value(), FORMAT_STRING))
        self.control_laser_phase()
        
    def control_gain_slider_slot(self):
        self.ui.control_gain_current.setText(format(self.ui.control_gain_slider.value(), FORMAT_STRING))
        self.control_gain()
        
    def control_phase1_slider_slot(self):
        self.ui.control_phase1_current.setText(format(self.ui.control_phase1_slider.value(), FORMAT_STRING))
        self.control_phase1()
        
    def control_mirror2_slider_slot(self):
        self.ui.control_mirror2_current.setText(format(self.ui.control_mirror2_slider.value(), FORMAT_STRING))
        self.control_mirror2()
        
    def control_soa1_slider_slot(self):
        self.ui.control_soa1_current.setText(format(self.ui.control_soa1_slider.value(), FORMAT_STRING))
        self.control_soa1()
        
    def control_soa2_slider_slot(self):
        self.ui.control_soa2_current.setText(format(self.ui.control_soa2_slider.value(), FORMAT_STRING))
        self.control_soa2()
        
    def control_mirror1_slot(self):
        self.control_mirror1()
        self.ui.control_mirror1_slider.setValue(float(self.ui.control_mirror1_current.text()))
    
    def control_laser_phase_slot(self):
        self.control_laser_phase()
        self.ui.control_laser_phase_slider.setValue(float(self.ui.control_laser_phase_current.text()))
    
    def control_gain_slot(self):
        self.control_gain()
        self.ui.control_gain_slider.setValue(float(self.ui.control_gain_current.text()))
        
    def control_phase1_slot(self):
        self.control_phase1()
        self.ui.control_phase1_slider.setValue(float(self.ui.control_phase1_current.text()))
    
    def control_mirror2_slot(self):
        self.control_mirror2()
        self.ui.control_mirror2_slider.setValue(float(self.ui.control_mirror2_current.text()))
    
    def control_soa1_slot(self):
        self.control_soa1()
        self.ui.control_soa1_slider.setValue(float(self.ui.control_soa1_current.text()))
        
    def control_soa2_slot(self):
        self.control_soa2()
        self.ui.control_soa2_slider.setValue(float(self.ui.control_soa2_current.text()))
        
    def control_mirror1(self):
        if not self.validate_text(self.ui.control_mirror1_current):
            return
        self.rig.mirror1.write_current(float(self.ui.control_mirror1_current.text()))
        self.ui.control_mirror1_voltage.setText(format(self.rig.mirror1.read_voltage(), FORMAT_STRING))
    
    def control_laser_phase(self):
        if not self.validate_text(self.ui.control_laser_phase_current):
            return
        self.rig.laser_phase.write_current(float(self.ui.control_laser_phase_current.text()))
        self.ui.control_laser_phase_voltage.setText(format(self.rig.laser_phase.read_voltage(), FORMAT_STRING))
    
    def control_gain(self):
        if not self.validate_text(self.ui.control_gain_current):
            return
        self.rig.gain.write_current(float(self.ui.control_gain_current.text()))
        self.ui.control_gain_voltage.setText(format(self.rig.gain.read_voltage(), FORMAT_STRING))
        
    def control_phase1(self):
        if not self.validate_text(self.ui.control_phase1_current):
            return
        self.rig.phase1.write_current(float(self.ui.control_phase1_current.text()))
        self.ui.control_phase1_voltage.setText(format(self.rig.phase1.read_voltage(), FORMAT_STRING))
    
    def control_mirror2(self):
        if not self.validate_text(self.ui.control_mirror2_current):
            return
        self.rig.mirror2.write_current(float(self.ui.control_mirror2_current.text()))
        self.ui.control_mirror2_voltage.setText(format(self.rig.mirror2.read_voltage(), FORMAT_STRING))
    
    def control_soa1(self):
        if not self.validate_text(self.ui.control_soa1_current):
            return
        self.rig.soa1.write_current(float(self.ui.control_soa1_current.text()))
        self.ui.control_soa1_voltage.setText(format(self.rig.soa1.read_voltage(), FORMAT_STRING))
        
    def control_soa2(self):
        if not self.validate_text(self.ui.control_soa2_current):
            return
        self.rig.soa2.write_current(float(self.ui.control_soa2_current.text()))
        self.ui.control_soa2_voltage.setText(format(self.rig.soa2.read_voltage(), FORMAT_STRING))

# Tab: Averaging

    def averaging_slot(self, index, combobox):
        if combobox.currentIndex() == 8:
            value = 255
        else:
            value = 2 ** (combobox.currentIndex())
        self.rig.write_averaging_amount(index, value)

# Tab: Minima

    def minima_load_data_slot(self):
        filename = QtGui.QFileDialog.getOpenFileName(self,
                                                     'Open sweep data file',
                                                     '',
                                                     '')
        if len(filename) == 0:
            return
        
        self.ui.minima_data_path.setText(filename)
        self.ui.minima_output_path.setText(filename + '.minima')
        
    def minima_output_file_slot(self):
        filename = QtGui.QFileDialog.getSaveFileName(self,
                                                     'Open minima data file',
                                                     '',
                                                     "Minima Data File (*.minima)")
        if len(filename) == 0:
            return
        if not filename.endswith('.minima'):
            filename += '.minima'
            
        self.ui.minima_output_path.setText(filename)
        
    def minima_find_slot(self):
        filename = self.ui.minima_data_path.text()
        if self.ui.minima_GUI_data_type.isChecked():
            sweepdata = np.genfromtxt(filename, skip_header=9, delimiter=",", names=True)
        elif self.ui.minima_keithley_data_type.isChecked():
            sweepdata = np.genfromtxt(filename, skip_header=1, delimiter=",", names=("mirr2_current","mirr1_current","gain_voltage"))
            
        if self.ui.minima_mirror2_square_root_check.isChecked():
            x = np.sqrt(sweepdata["mirr2_current"])
        else:
            x = sweepdata["mirr2_current"]
            
        if self.ui.minima_mirror1_square_root_check.isChecked():
            y = np.sqrt(sweepdata["mirr1_current"])
        else:
            y = sweepdata["mirr1_current"]
        
        z = sweepdata["gain_voltage"]
        
        xi = np.linspace(min(x),max(x), int(self.ui.minima_linspace_x.text()))
        yi = np.linspace(min(y),max(y), int(self.ui.minima_linspace_y.text()))
        zi = ml.griddata(x,y,z,xi,yi)
        
        #Run Gaussian Filters
        
        if self.ui.minima_gauss1_check.isChecked():
            zi = ndimage.gaussian_filter(zi, sigma=float(self.ui.minima_gauss1_sigma.text()), order=0)
            
        if self.ui.minima_gauss2_check.isChecked():
            gauss = ndimage.gaussian_filter(zi, sigma=float(self.ui.minima_gauss2_sigma.text()), order=0)
            zi = np.subtract(zi, gauss)
            
        if self.ui.minima_gauss3_check.isChecked():
            zi = ndimage.gaussian_filter(zi, sigma=float(self.ui.minima_gauss3_sigma.text()), order=0)
            
        #Find Minima
        
        minima_width = int(self.ui.minima_width.text())
        
        # Iterate over each point in the linear space
        array_data = zi
        minima = []
        
        for y in range(int(self.ui.minima_linspace_y.text())):
            for x in range(int(self.ui.minima_linspace_x.text())):
                if type(array_data[x, y]) == np.ma.core.MaskedConstant or np.isnan(array_data[x, y]):
                    continue
                else:
                    # Create a sub-array of values to compare against
                    sub_array = array_data[max(0, y - minima_width ):min(int(self.ui.minima_linspace_y.text()) - 1, y + minima_width) + 1,max(0, x - minima_width ):min(int(self.ui.minima_linspace_x.text()) - 1, x + minima_width) + 1]
                    is_minima = True
                    for point in sub_array.flatten():
                        if type(point) == np.ma.core.MaskedConstant or np.isnan(point):
                            is_minima = False
                            break
                        elif point < array_data[y, x]:
                            is_minima = False
                            break
                    if is_minima:
                        #print(format(xi[x]) + "(" + format(x) + ")," + format(yi[y]) + "(" + format(x) + "):" + format(array_data[y, x]))
                        minima.append([xi[x], yi[y]])
                        
        if self.ui.minima_plot_check.isChecked():
            plt.figure(1)
            plt.pcolormesh(xi, yi, zi, cmap = plt.get_cmap('gray_r'),vmin=np.ma.min(zi),vmax=np.ma.max(zi))
            plt.xlabel("Mirror 2 (mA)")
            plt.ylabel("Mirror 1 (mA)")
            plt.suptitle("Minima Data", fontsize = 20)
            plt.title(filename, fontsize = 12)
            plt.colorbar()
            
            for point in minima:
                plt.plot(point[0],point[1],'o')
                
            plt.show()
                
        else:
            self.msgbox("Minima detection complete")
                
        #Output minima to file
        
        output_path = open(self.ui.minima_output_path.text(), 'w')
        output_path.write("mirr2_current,mirr1_current\n")
        for point in minima:
            if self.ui.minima_mirror2_square_root_check.isChecked():
                point[0] = point[0] ** 2
            if self.ui.minima_mirror1_square_root_check.isChecked():
                point[1] = point[1] ** 2
            output_path.write(format(point[0]) + ',' + format(point[1]) + '\n')
        output_path.close()
        
    def minima_save_config_slot(self):
        filename = QtGui.QFileDialog.getSaveFileName(self,
                                                     'Open minima config file',
                                                     '',
                                                     "Minima Config File (*.minimaconfig)")
        if len(filename) == 0:
            return
        if not filename.endswith('.minimaconfig'):
            filename += '.minimaconfig'
            
        file = open(filename, 'w')
        
        file.write(self.ui.minima_linspace_x.text() + '\n')
        file.write(self.ui.minima_linspace_y.text() + '\n')
        file.write(format(self.ui.minima_mirror2_square_root_check.isChecked()) + '\n')
        file.write(format(self.ui.minima_mirror1_square_root_check.isChecked()) + '\n')
        file.write(format(self.ui.minima_gauss1_check.isChecked()) + '\n')
        file.write(self.ui.minima_gauss1_sigma.text() + '\n')
        file.write(format(self.ui.minima_gauss2_check.isChecked()) + '\n')
        file.write(self.ui.minima_gauss2_sigma.text() + '\n')
        file.write(format(self.ui.minima_gauss3_check.isChecked()) + '\n')
        file.write(self.ui.minima_gauss3_sigma.text() + '\n')
        file.write(self.ui.minima_width.text() + '\n')
        file.write(format(self.ui.minima_plot_check.isChecked()) + '\n')
        
        file.close()
        
    def minima_load_config_slot(self):
        filename = QtGui.QFileDialog.getOpenFileName(self,
                                                     'Open minima config file',
                                                     '',
                                                     "Minima Config File (*.minimaconfig)")
        if len(filename) == 0:
            return
            
        file = open(filename, 'r')
        
        def set_check(checkbox):
            if file.readline().splitlines()[0] == 'True':
                checkbox.setChecked(True)
            else:
                checkbox.setChecked(False)
        
        self.ui.minima_linspace_x.setText(file.readline().splitlines()[0])
        self.ui.minima_linspace_y.setText(file.readline().splitlines()[0])
        set_check(self.ui.minima_mirror2_square_root_check)
        set_check(self.ui.minima_mirror1_square_root_check)
        set_check(self.ui.minima_gauss1_check)
        self.ui.minima_gauss1_sigma.setText(file.readline().splitlines()[0])
        set_check(self.ui.minima_gauss2_check)
        self.ui.minima_gauss2_sigma.setText(file.readline().splitlines()[0])
        set_check(self.ui.minima_gauss3_check)
        self.ui.minima_gauss3_sigma.setText(file.readline().splitlines()[0])
        self.ui.minima_width.setText(file.readline().splitlines()[0])
        set_check(self.ui.minima_plot_check)
        
        file.close()

# Tab: OSA

    def osa_load_data_slot(self):
        filename = QtGui.QFileDialog.getOpenFileName(self,
                                                     'Open minima file',
                                                     '',
                                                     "Minima Data File (*.minima)")
        if len(filename) == 0:
            return
        
        self.ui.osa_data_path.setText(filename)
        self.ui.osa_output_path.setText(filename[0:-7] + '.wavelength')
        
    def osa_output_file_slot(self):
        filename = QtGui.QFileDialog.getSaveFileName(self,
                                                     'Open wavelength data file',
                                                     '',
                                                     "Wavelength Data File (*.wavelength)")
        if len(filename) == 0:
            return
        if not filename.endswith('.wavelength'):
            filename += '.wavelength'
            
        self.ui.osa_output_path.setText(filename)
        
    def osa_return_osa(self, ip, port, gpib):
        if self.ui.osa_AQ6331_radio.isChecked():
            return AQ6331.OSA(self.ui.hardware_ip.text(), 1234, self.ui.osa_gpib.text())
        elif self.ui.osa_86120B_radio.isChecked():
            return HP86120B.OSA(self.ui.hardware_ip.text(), 1234, self.ui.osa_gpib.text())
        else:
            raise(Warning("No valid OSA selected"))
    
    def osa_find_wavelengths_slot(self):
        def stop_scan():
            osa.closesocket()
            output_path.close()
            self.ui.osa_progress.setValue(0)
            self.ui.osa_find_wavelengths_button.setText("Find Wavelengths")
            self.osa_running = False
            
        if  not(self.osa_running):
            self.ui.osa_find_wavelengths_button.setText("Stop Scan")
            self.osa_running = True
            
            minima_data = np.genfromtxt(self.ui.osa_data_path.text(), skip_header=1, delimiter=",", names=True)
            self.ui.osa_progress.setMaximum(len(minima_data))
            self.ui.osa_progress.setValue(0)
            
            osa = self.osa_return_osa(self.ui.hardware_ip.text(), 1234, self.ui.osa_gpib.text())
            osa.writesweepstart(1525)
            osa.writesweepstop(1565)
            osa.writeresolution(0.05)
            
            output_path = open(self.ui.osa_output_path.text(), 'w')
            output_path.write("mirr2_current,mirr1_current,wavelength1,power1,wavelength2,power2\n")
            #output_path.close()
            
            #wavelengths = []
            
            for minima in minima_data:
                peakfound = False
                while not peakfound:
                    try:
                        self.rig.mirror2.write_current(minima["mirr2_current"])
                        self.rig.mirror1.write_current(minima["mirr1_current"])
                        osa.startsweep()
                        QtGui.QApplication.processEvents()
                        while not osa.checksweepfinished():
                            QtGui.QApplication.processEvents()
                        #osa.startprimarypeaksearch()
                        peaks = osa.readpeak()
                        output_path.write(format(minima["mirr2_current"]) + ',' + format(minima["mirr1_current"]) + ',' + format(peaks[0]["wavelength"]) + ',' + format(peaks[0]["power"]) + ',')
                        if len(peaks) > 1:
                            output_path.write(format(peaks[1]["wavelength"]) + ',' + format(peaks[1]["power"]) + '\n')
                        else:
                            output_path.write('0,0\n')
                        
                        self.ui.osa_progress.setValue(self.ui.osa_progress.value() + 1)
                        QtGui.QApplication.processEvents()
                        peakfound = True
                        
                        if not(self.osa_running):
                            stop_scan()
                            return
                    except socket.timeout:
                        pass # Loop through peak finder again
                
            stop_scan()
            
        else:
            self.osa_running = False

# Tab: PROM

    def write_memmap_init_file(self):
        filename = QtGui.QFileDialog.getSaveFileName(self,
                                                     'Open binary file',
                                                     '',
                                                     '')
        if len(filename) == 0:
            return
        
        file = open(filename, 'w')
        
        self.ui.flash_progress.setMaximum(1023)
        self.ui.flash_progress.setValue(0)
        for i in range(1024):
            orig_int = self.rig.device.readregister(i)     
            as_str =  '{:02x}'.format(orig_int)
            file.write(as_str);
            if(i<1023):
                file.write(" ");
            self.ui.flash_progress.setValue(i)
            QtGui.QApplication.processEvents()
                
        file.close()
        return

    def load_lambda_init_file(self):
        filename = QtGui.QFileDialog.getOpenFileName(self,
                                                     'Open binary file',
                                                     '',
                                                     '')
        if len(filename) == 0:
            return
            
        wave_inserter = LambdaInserter.LambdaInserter(filename)
        
        #Now get the Lambda Init string.  It is parsed from a CSV input of TOSA wave tables
        lamdba_init_str = wave_inserter.execute_parse()
        lambda_bytes = lamdba_init_str.split(" ")
        #print(lambda_bytes)
        #print("Length Of Lmabdas in Bytes", len(lambda_bytes))
        
        #now write the lambdas to the PROM
        while self.rig.flash_check_busy():
            QtGui.QApplication.processEvents()
        self.rig.flash_enable_direct_control(True)
        self.rig.flash_write_address(462848)
        
        self.ui.flash_progress.setMaximum(3106)
        self.ui.flash_progress.setValue(0)
        for i in range(3107): #there will always be 1024 bytes read in, no more, no less
            self.ui.flash_progress.setValue(i)
            byte = int(lambda_bytes[i], 16)
            self.rig.flash_write_byte(byte)
            QtGui.QApplication.processEvents()
        
        self.rig.flash_set_read(False)
        self.rig.flash_trigger_readwrite(True)
        while self.rig.flash_check_busy():
            QtGui.QApplication.processEvents()
        self.rig.flash_enable_direct_control(False)
        
    def flash_read_file_slot(self):
        filename = QtGui.QFileDialog.getSaveFileName(self,
                                                     'Open binary file',
                                                     '',
                                                     '')
        if len(filename) == 0:
            return
        
        file = open(filename, 'wb')
            
        while self.rig.flash_check_busy():
            QtGui.QApplication.processEvents()
        self.rig.flash_enable_direct_control(True)
        self.rig.flash_write_address(int(self.ui.flash_address.text()))
        self.rig.flash_set_read(True)
        self.rig.flash_trigger_readwrite(True)
        while self.rig.flash_check_busy():
            QtGui.QApplication.processEvents()
        self.ui.flash_progress.setMaximum(int(self.ui.flash_length.text()) - 1)
        self.ui.flash_progress.setValue(0)
        for i in range(int(self.ui.flash_length.text())):
            file.write(bytes([self.rig.flash_read_byte()]))
            self.ui.flash_progress.setValue(i)
            QtGui.QApplication.processEvents()
        self.rig.flash_enable_direct_control(False)
        
        file.close()
    
    def flash_write_file_slot(self):
        filename = QtGui.QFileDialog.getOpenFileName(self,
                                                     'Open binary file',
                                                     '',
                                                     '')
        if len(filename) == 0:
            return
        
        file = open(filename, 'rb')
            
        while self.rig.flash_check_busy():
            QtGui.QApplication.processEvents()
        self.rig.flash_enable_direct_control(True)
        self.rig.flash_write_address(int(self.ui.flash_address.text()))
#         self.rig.flash_write(file.read())
        filesize = os.path.getsize(filename)
        self.ui.flash_progress.setMaximum(filesize - 1)
        self.ui.flash_progress.setValue(0)
        for i in range(filesize):
            self.rig.flash_write_byte(int.from_bytes(file.read(1), 'big'))
            self.ui.flash_progress.setValue(i)
            QtGui.QApplication.processEvents()
        self.rig.flash_set_read(False)
        self.rig.flash_trigger_readwrite(True)
        while self.rig.flash_check_busy():
            QtGui.QApplication.processEvents()
        self.rig.flash_enable_direct_control(False)
        
        file.close()
        
    def flash_read_slot(self):
        while self.rig.flash_check_busy():
            QtGui.QApplication.processEvents()
        self.rig.flash_enable_direct_control(True)
        self.rig.flash_write_address(int(self.ui.flash_address.text()))
        self.rig.flash_set_read(True)
        self.rig.flash_trigger_readwrite(True)
        while self.rig.flash_check_busy():
            QtGui.QApplication.processEvents()
        value_array = self.rig.flash_read(int(self.ui.flash_length.text()))
        displaystring = ""
        for value in value_array:
            displaystring = displaystring + "{:02x}".format(value) + " "
        self.ui.flash_values.setText(displaystring)
        self.rig.flash_enable_direct_control(False)
    
    def flash_write_slot(self):
        value_array = []
        for number in self.ui.flash_values.text().strip().split(" "):
            value_array.append(int(number,16))
            
        while self.rig.flash_check_busy():
            QtGui.QApplication.processEvents()
        self.rig.flash_enable_direct_control(True)
        self.rig.flash_write_address(int(self.ui.flash_address.text()))
        self.rig.flash_set_read(False)
        self.rig.flash_write(value_array)
        self.rig.flash_set_read(False)
        self.rig.flash_trigger_readwrite(True)
        while self.rig.flash_check_busy():
            QtGui.QApplication.processEvents()
        self.rig.flash_enable_direct_control(False)
        
    def reload_wavelength_slot(self):
        self.rig.reload_wavelength()
        
    def reload_i2c_slot(self):
        self.rig.reload_i2c_registers()
        
    def soft_reset_slot(self):
        self.rig.soft_reset()

# Misc
        
    def set_validators(self):
        def set_validator(widget, validator):
            widget.setValidator(validator)
            
            if len(widget.text()) > 0:
                if float(widget.text()) > validator.top():
                    widget.setText(format(validator.top(), FORMAT_STRING))
                    
                if float(widget.text()) < validator.bottom():
                    widget.setText(format(validator.bottom(), FORMAT_STRING))
        
        set_validator(self.ui.control_mirror1_current, self.rig.mirror1.validator)
        self.ui.control_mirror1_slider.setMaximum(int(self.rig.mirror1.validator.top()))
        self.ui.control_mirror1_max.setText(format(int(self.rig.mirror1.validator.top())))
        
        set_validator(self.ui.control_laser_phase_current, self.rig.laser_phase.validator)
        self.ui.control_laser_phase_slider.setMaximum(int(self.rig.laser_phase.validator.top()))
        self.ui.control_laser_phase_max.setText(format(int(self.rig.laser_phase.validator.top())))
        
        set_validator(self.ui.control_gain_current, self.rig.gain.validator)
        self.ui.control_gain_slider.setMaximum(int(self.rig.gain.validator.top()))
        self.ui.control_gain_max.setText(format(int(self.rig.gain.validator.top())))
        
        set_validator(self.ui.control_phase1_current, self.rig.phase1.validator)
        self.ui.control_phase1_slider.setMaximum(int(self.rig.phase1.validator.top()))
        self.ui.control_phase1_max.setText(format(int(self.rig.phase1.validator.top())))
        
        set_validator(self.ui.control_mirror2_current, self.rig.mirror2.validator)
        self.ui.control_mirror2_slider.setMaximum(int(self.rig.mirror2.validator.top()))
        self.ui.control_mirror2_max.setText(format(int(self.rig.mirror2.validator.top())))
        
        set_validator(self.ui.control_soa1_current, self.rig.soa1.validator)
        self.ui.control_soa1_slider.setMaximum(int(self.rig.soa1.validator.top()))
        self.ui.control_soa1_max.setText(format(int(self.rig.soa1.validator.top())))
        
        set_validator(self.ui.control_soa2_current, self.rig.soa2.validator)
        self.ui.control_soa2_slider.setMaximum(int(self.rig.soa2.validator.top()))
        self.ui.control_soa2_max.setText(format(int(self.rig.soa2.validator.top())))
        
    def data_location(self):
        datapath = self.data_location_text
        if not(os.path.exists(os.path.dirname(datapath))):
            os.makedirs(os.path.dirname(datapath))
        return self.data_location_text
    
    def closeEvent(self, event):
        
        laserOK = True
        if not self.rig is None:
            if self.rig.mirror1.read_current_dac() > 0:
                laserOK = False
            if self.rig.laser_phase.read_current_dac() > 0:
                laserOK = False
            if self.rig.gain.read_current_dac() > 0:
                laserOK = False
            if self.rig.phase1.read_current_dac() > 0:
                laserOK = False
            if self.rig.mirror2.read_current_dac() > 0:
                laserOK = False
            if self.rig.soa1.read_current_dac() > 0:
                laserOK = False
            if self.rig.soa2.read_current_dac() > 0:
                laserOK = False
#             if self.rig.read_modulator_1_bias() > 0:
#                 laserOK = False
#             if self.rig.read_modulator_2_bias() > 0:
#                 laserOK = False
#             if self.rig.read_modulator_chirp() > 0:
#                 laserOK = False
#             if self.rig.read_modulator_amplitude() > 0:
#                 laserOK = False

        self.rig.close()

        if not laserOK:
            quit_msg = "Laser is still running! Are you sure you want to exit program?"
            reply = QtGui.QMessageBox.question(self, 'Message',
                                               quit_msg, QtGui.QMessageBox.Yes,
                                               QtGui.QMessageBox.No)
        
            if reply == QtGui.QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        
        else:
            event.accept()
            
    def exit_slot(self):
        sys.exit()
        
    def currents_from_laser(self):
        self.ui.control_mirror1_current.setText(format(int(self.rig.mirror1.read_current()), FORMAT_STRING))
        self.control_mirror1_slot()
        
        self.ui.control_laser_phase_current.setText(format(int(self.rig.laser_phase.read_current()), FORMAT_STRING))
        self.control_laser_phase_slot()
        
        self.ui.control_gain_current.setText(format(int(self.rig.gain.read_current()), FORMAT_STRING))
        self.control_gain_slot()
        
        self.ui.control_phase1_current.setText(format(int(self.rig.phase1.read_current()), FORMAT_STRING))
        self.control_phase1_slot()
        
        self.ui.control_mirror2_current.setText(format(int(self.rig.mirror2.read_current()), FORMAT_STRING))
        self.control_mirror2_slot()
        
        self.ui.control_soa1_current.setText(format(int(self.rig.soa1.read_current()), FORMAT_STRING))
        self.control_soa2_slot()
        
        self.ui.control_soa2_current.setText(format(int(self.rig.soa2.read_current()), FORMAT_STRING))
        self.control_soa2_slot()
        
        # Pull averaging values from laser once it is actually implemented
        def averaging_index(index):
            averaging_amount = self.rig.read_averaging_amount(index)
            if averaging_amount == 0: #This is actually an invalid data point
                print ("ADC " + format(index) + " has a zero averaging parameter")
                return 0
            else:
                return math.ceil(math.log(self.rig.read_averaging_amount(index),2))
        
        self.ui.averaging_combo_1.setCurrentIndex(averaging_index(1))
        self.ui.averaging_combo_2.setCurrentIndex(averaging_index(2))
        self.ui.averaging_combo_3.setCurrentIndex(averaging_index(3))
        self.ui.averaging_combo_4.setCurrentIndex(averaging_index(4))
        self.ui.averaging_combo_5.setCurrentIndex(averaging_index(5))
        self.ui.averaging_combo_6.setCurrentIndex(averaging_index(6))
        self.ui.averaging_combo_7.setCurrentIndex(averaging_index(7))
        self.ui.averaging_combo_8.setCurrentIndex(averaging_index(8))
        self.ui.averaging_combo_9.setCurrentIndex(averaging_index(9))
        self.ui.averaging_combo_10.setCurrentIndex(averaging_index(10))
        self.ui.averaging_combo_11.setCurrentIndex(averaging_index(11))
        self.ui.averaging_combo_12.setCurrentIndex(averaging_index(12))
        self.ui.averaging_combo_13.setCurrentIndex(averaging_index(13))
        self.ui.averaging_combo_14.setCurrentIndex(averaging_index(14))
        self.ui.averaging_combo_15.setCurrentIndex(averaging_index(15))
        self.ui.averaging_combo_16.setCurrentIndex(averaging_index(16))
        
        self.ui.laser_switch.setChecked(self.rig.read_laser_on())
        self.ui.laser_tec_switch.setChecked(self.rig.read_laser_tec_on())
        self.ui.etalon_tec_switch.setChecked(self.rig.read_etalon_tec_on())
        self.ui.apc_switch.setChecked(self.rig.read_apc_on())
        self.ui.locker_switch.setChecked(self.rig.read_locker_on())
        
    def datafile_header(self, file):
        file.write('Computer Name: ' + socket.gethostname() + '\n')
        file.write('Device ID: ' + self.device_id + '\n')
        
    def zero_laser(self):
        self.rig.mirror1.write_current_dac(0)
        self.rig.laser_phase.write_current_dac(0)
        self.rig.gain.write_current_dac(0)
        self.rig.phase1.write_current_dac(0)
        self.rig.mirror2.write_current_dac(0)
        self.rig.soa1.write_current_dac(0)
        self.rig.soa2.write_current_dac(0)
        
    def validate_text(self, widget):  # Not really neccesary
        if widget.hasAcceptableInput():
            palette = widget.palette()
            palette.setColor(QPalette.Base, QtCore.Qt.white)
            widget.setPalette(palette)
            return True
        else:
            palette = widget.palette()
            palette.setColor(QPalette.Base, QtCore.Qt.yellow)
            widget.setPalette(palette)
            return False
        
    def float_validator(self, min_, max_):
        validator = QtGui.QDoubleValidator()
        validator.setBottom(min_)
        validator.setTop(max_)
        validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        return validator
    
    def msgbox(self, message):
        msgbox = QtGui.QMessageBox()
        msgbox.setText(message)
        msgbox.exec_()
        
    class WavelengthMapError(Exception):  # Just so we can handle this specific exception
        pass
    
class SweepParameter():
    def __init__(self, name, minimum, maximum, step, input_func, output_func, column_name, init_func=None, close_func=None):
        self.name = name
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
        self.input_func = input_func
        self.output_func = output_func #This should take a BlockLaserSection as the only parameter
        self.column_name = column_name
        self.input_value = minimum
        self.init_func = init_func
        self.close_func = close_func
        
    def add_row(self, table):
        row = table.rowCount()
        table.setRowCount(row + 1)
        
        item = QtGui.QTableWidgetItem(self.name)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        table.setItem(row, 0, item)
        
        item = QtGui.QTableWidgetItem(format(self.minimum, FORMAT_STRING))
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
        table.setItem(row, 1, item)
        
        item = QtGui.QTableWidgetItem(format(self.maximum, FORMAT_STRING))
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
        table.setItem(row, 2, item)
        
        item = QtGui.QTableWidgetItem(format(self.step, FORMAT_STRING))
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
        table.setItem(row, 3, item)
        
        item = QtGui.QTableWidgetItem(format(self.minimum, FORMAT_STRING))
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        table.setItem(row, 4, item)
        
        item = QtGui.QTableWidgetItem(format(0, FORMAT_STRING))
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        table.setItem(row, 5, item)
        
        item = QtGui.QTableWidgetItem("Remove")
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        table.setItem(row, 6, item)
        
    def iterations(self):
        return int((self.maximum - self.minimum) / self.step) + 1


def main():
    
    app = QtGui.QApplication(sys.argv)
    spam = SweepTest()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
