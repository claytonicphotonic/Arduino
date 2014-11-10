'''
Created on May 12, 2014

@author: bay
'''

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QMainWindow

import os
from PyQt4 import QtGui, QtCore

import traceback
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from . ui_dc_debug import Ui_MainWindow
from . strictdoublevalidator import StrictDoubleValidator

from testsuite.instruments import PM100USB, HP86120B, MS9740

from testsuite.instruments import test_stations
from testsuite.instruments import electrodes

OUTPUT_FORMAT = '.2f'

CONNECT_STRING = "Connect"
DISCONNECT_STRING = "Disconnect"

LASER_SECTIONS_KEITHLEYS = 0
LASER_SECTIONS_NI_BOX_TOSA = 1
LASER_SECTIONS_NI_BOX_COC = 2
LASER_SECTIONS_SFP = 3
LASER_SECTIONS_DUMMY = 4

GPIB_VISA = 0
GPIB_PROLOGIX_ETHERNET = 1
GPIB_PROLOGIX_USB = 2
GPIB_DUMMY = 3

SLIDER_CROSSOVER = 30

VOLTAGE_UNIT_STRING = "V"
CURRENT_UNIT_STRING = "mA"

# CURRENT_MAX = {'mirror1':50, 
#                'mirror2':50, 
#                'gain':150, 
#                'phase1':15, 
#                'soa1':80, 
#                'soa2':80, 
#                'laspha':10, 
#                'mod1':15, 
#                'mod2':15, 
#                'detector':10}
# 
# VOLTAGE_MAX = {'mirror1':-4, 
#                'mirror2':-4, 
#                'gain':-4, 
#                'phase1':-4, 
#                'soa1':-4, 
#                'soa2':-4, 
#                'laspha':-2, 
#                'mod1':-6, 
#                'mod2':-6, 
#                'detector':-3}

OSA_VBW = [10, 100, 200, 1000, 2000, 10000, 100000, 1000000]
OSA_RESOLUTION = [0.03, 0.05, 0.07, 0.1, 0.2, 0.5, 1.0]
OSA_SAMPLING = [51, 101, 251, 501, 1001, 2001, 5001, 10001, 20001, 50001]

class MplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass
    
class ElectrodeGUI(object):
    def __init__(self, 
                 electrode, 
                 layout_widget):
        self.electrode = electrode
        
        self.widget = QtGui.QWidget()
        self.widget.setMinimumHeight(75)
        
        hlayout = QtGui.QHBoxLayout()
        self.widget.setLayout(hlayout)
        
        self.output_on = QtGui.QCheckBox()
        self.output_on.setChecked(electrode.initial_on)
        hlayout.addWidget(self.output_on)
        
        title = QtGui.QLabel(electrode.long_name)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        title.setFont(font)
        title.setMinimumWidth(100)
        title.setMaximumWidth(100)
        hlayout.addWidget(title)
        
        box = QtGui.QGroupBox("Source Output")
        box_layout = QtGui.QVBoxLayout()
        box_layout.setSpacing(0)
        box_layout.setContentsMargins(5, 0, 0, 0)
        box.setLayout(box_layout)
        self.current_option = QtGui.QRadioButton("Current")
        box_layout.addWidget(self.current_option)
        self.voltage_option = QtGui.QRadioButton("Voltage")
        box_layout.addWidget(self.voltage_option)
        hlayout.addWidget(box)
        
        self.input_text = QtGui.QLineEdit()
        self.input_text.setText("0.0")
        self.input_text.setMaximumWidth(59)
        hlayout.addWidget(self.input_text)
        
        self.input_button = QtGui.QPushButton("Set Value")
        hlayout.addWidget(self.input_button)
        
        self.min_input = QtGui.QLabel("0")
        hlayout.addWidget(self.min_input)
        
        self.input_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        hlayout.addWidget(self.input_slider)
        
        self.max_input = QtGui.QLabel("100")
        hlayout.addWidget(self.max_input)
        
        hlayout.addSpacing(10)
        
        self.output_text = QtGui.QLabel("0.0")
        hlayout.addWidget(self.output_text)
        
        self.output_units = QtGui.QLabel("V")
        hlayout.addWidget(self.output_units)
        
        layout_widget.addWidget(self.widget)
        
        self.input_button.clicked.connect(self.input_slot)
        self.input_text.returnPressed.connect(self.input_slot)
        self.input_slider.valueChanged.connect(self.slider_slot)
        self.current_option.clicked.connect(self.source_type_slot)
        self.voltage_option.clicked.connect(self.source_type_slot)
        self.output_on.stateChanged.connect(self.output_on_slot)

    def __del__(self):
        self.widget.setParent(None)
        del(self.widget)
        
    def slider_factor(self):
        MIN_STEPS = 10
        
        if self.current_option.isChecked():
            delta = abs(self.electrode.current_limit_max - self.electrode.current_limit_min)
        elif self.voltage_option.isChecked():
            delta = abs(self.electrode.voltage_limit_max - self.electrode.voltage_limit_min)
            
        factor = 1
        while delta < MIN_STEPS:
            factor = factor * 10
            delta = delta * 10
            
        return factor
    
    def output_on_slot(self):
        self.electrode.set_output_on(self.output_on.isChecked())
        
    def slider_slot(self):
        input_value = float(self.input_slider.value()) / self.slider_factor()
        
#         if self.current_option.isChecked() and self.electrode.current_limit_max > SLIDER_CROSSOVER:
#             input_value = float(self.input_slider.value())
#         elif self.current_option.isChecked():
#             input_value = float(self.input_slider.value()) / 10
#         elif self.voltage_option.isChecked():
#             input_value = float(self.input_slider.value()) / 10
            
        self.input_text.setText(format(input_value))
        self.input(input_value)
        
    def input_slot(self):
        self.update_slider()
            
        self.input(float(self.input_text.text()))
        
    def update_slider(self):
        self.input_slider.valueChanged.disconnect()
        #self.input_slider.setEnabled(False)
        self.input_slider.setValue(float(self.input_text.text()) * self.slider_factor())
        
#         if self.current_option.isChecked() and self.electrode.current_limit_max > SLIDER_CROSSOVER:
#             self.input_slider.setValue(float(self.input_text.text()))
#         elif self.current_option.isChecked():
#             self.input_slider.setValue(float(self.input_text.text()) * 10)
#         elif self.voltage_option.isChecked():
#             self.input_slider.setValue(float(self.input_text.text()) * 10)
            
        #self.input_slider.setEnabled(True)
        self.input_slider.valueChanged.connect(self.slider_slot)
        
    def input(self, value):
        if self.current_option.isChecked():
            self.electrode.write_current(value)
        elif self.voltage_option.isChecked():
            self.electrode.write_voltage(value)
            
        self.output()
            
    def output(self):
        if self.current_option.isChecked():
            output_value = self.electrode.read_voltage()
        elif self.voltage_option.isChecked():
            output_value = self.electrode.read_current()
            
        self.output_text.setText(format(output_value, OUTPUT_FORMAT))
    
    def source_type_slot(self):
        validator = StrictDoubleValidator()
        if self.current_option.isChecked():
            input_max = self.electrode.current_limit_max
            input_min = self.electrode.current_limit_min
            slider_max = self.electrode.current_limit_max * self.slider_factor()
            slider_min = self.electrode.current_limit_min * self.slider_factor()
#             if self.electrode.current_limit_max > SLIDER_CROSSOVER:
#                 slider_max = self.electrode.current_limit_max
#                 slider_min = self.electrode.current_limit_min
#             else:
#                 slider_max = self.electrode.current_limit_max * 10
#                 slider_min = self.electrode.current_limit_min * 10
            self.output_units.setText(VOLTAGE_UNIT_STRING)
            validator.setBottom(self.electrode.current_limit_min)
            validator.setTop(self.electrode.current_limit_max)
        elif self.voltage_option.isChecked():
            input_max = self.electrode.voltage_limit_max
            input_min = self.electrode.voltage_limit_min
            slider_max = self.electrode.voltage_limit_max * self.slider_factor()
            slider_min = self.electrode.voltage_limit_min * self.slider_factor()
            self.output_units.setText(CURRENT_UNIT_STRING)
            validator.setBottom(self.electrode.voltage_limit_min)
            validator.setTop(self.electrode.voltage_limit_max)
            
        self.min_input.setText(format(input_min))
        self.max_input.setText(format(input_max))
        self.input_slider.setMinimum(slider_min)
        self.input_slider.setMaximum(slider_max)
        self.input_text.setValidator(validator)
        self.zero_section()
            
    def zero_section(self):
        self.input_text.setText(format(self.electrode.zero()))
        self.update_slider()
            
    def enable_gui(self):
        if self.electrode.output_type == electrodes.CURRENT_SOURCE:
            self.current_option.setChecked(True)
        elif self.electrode.output_type == electrodes.VOLTAGE_SOURCE:
            self.voltage_option.setChecked(True)
        self.source_type_slot()
        
    def disable_gui(self):
        pass
        
    def write_settings(self, file):
        file.write(format(self.current_option.isChecked()) + '\n')
        file.write(format(self.voltage_option.isChecked()) + '\n')
        file.write(self.input_text.text() + '\n')
        
    def read_settings(self, file):
        self.current_option.setChecked(file.readline().splitlines()[0] == "True")
        self.voltage_option.setChecked(file.readline().splitlines()[0] == "True")
        self.input_text.setText(file.readline().splitlines()[0])
        self.source_type_slot()
    
class DC_Debug(QMainWindow):
    def __init__(self):
        QWidget.__init__(self)
        
        # Set up the user interface from Designer.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.show()
        
        self.ui.osa_trace_plot = MplCanvas()
        self.ui.osa_trace_layout.addWidget(self.ui.osa_trace_plot)
        
        self.ui.is_get_value.setEnabled(False)
        self.ui.wm_get_values.setEnabled(False)
        self.osa_disable_gui()
        
        self.ui.laser_sections_connect.clicked.connect(self.laser_sections_connect_slot)
        self.ui.save_settings_button.clicked.connect(self.save_settings_slot)
        self.ui.load_settings_button.clicked.connect(self.load_settings_slot)
        
        self.ui.is_connect.clicked.connect(self.is_connect_slot)
        self.ui.is_get_value.clicked.connect(self.is_get_value_slot)
        
        self.ui.wavemeter_connect.clicked.connect(self.wm_connect_slot)
        self.ui.wm_get_values.clicked.connect(self.wm_get_values_slot)
        
        self.ui.zero_laser.clicked.connect(self.zero_laser_slot)
        self.ui.refresh_check.stateChanged.connect(self.refresh_slot)
        
        self.ui.osa_connect.clicked.connect(self.osa_connect_slot)
        self.ui.osa_vbw.currentIndexChanged.connect(self.osa_vbw_slot)
        self.ui.osa_resolution.currentIndexChanged.connect(self.osa_resolution_slot)
        self.ui.osa_sampling.currentIndexChanged.connect(self.osa_sampling_slot)
        self.ui.osa_start_stop_save.clicked.connect(self.osa_start_stop_slot)
        self.ui.osa_center_span_save.clicked.connect(self.osa_center_span_slot)
        self.ui.osa_sweep.clicked.connect(self.osa_sweep_slot)
        
        self.electrode_GUI_list = []
        self.station = None
        self.integrating_sphere = None
        self.gpib_interface = None
        self.wavemeter = None
        self.osa = None
        self.refresh_timer = QtCore.QTimer()
        self.refresh_timer.timeout.connect(self.refresh_timer_slot)
        #self.load_settings(os.getcwd() + os.sep + 'testsuite' + os.sep + 'dc_debug_gui' + os.sep + 'DEFAULT.cfg') #This should not be hardcoded, I should be able to get this programmatically
        
        self.disable_laser_control()
        
    def disable_laser_control(self):
        if self.ui.refresh_check.isChecked():
            self.ui.refresh_check.setChecked(False)
        self.ui.refresh_check.setEnabled(False)
        for electrodeGUI in self.electrode_GUI_list:
            electrodeGUI.disable_gui()
            
#         self.ui.current_compliance.setEnabled(True)
#         self.ui.voltage_compliance.setEnabled(True)
        
    def laser_sections_connect_slot(self):
        if self.station is not None:
            self.station.close()
            self.station = None
            self.ui.laser_sections_connect.setText(CONNECT_STRING)
            self.disable_laser_control()
            self.electrode_GUI_list = []
#             for electrodeGUI in self.electrode_GUI_list:
#                 del(electrodeGUI)
        else:
            try:
                if self.ui.laser_sections.currentIndex() == LASER_SECTIONS_KEITHLEYS:
                    self.station = test_stations.TestStationDC()
                elif self.ui.laser_sections.currentIndex() == LASER_SECTIONS_NI_BOX_TOSA:
                    self.station = test_stations.TestStationRF_TOSA()
                elif self.ui.laser_sections.currentIndex() == LASER_SECTIONS_NI_BOX_COC:
                    self.station = test_stations.TestStationRF_COC()
                elif self.ui.laser_sections.currentIndex() == LASER_SECTIONS_SFP:
                    #from testsuite.instruments import laser_sections_sfp
                    raise IOError("SFP is not implemented yet, need to add ability to select serial port")
                elif self.ui.laser_sections.currentIndex() == LASER_SECTIONS_DUMMY:
                    self.station = test_stations.TestStationDummy()
                    
                self.electrode_GUI_list = []
                for electrode in self.station.full_list:
                    self.electrode_GUI_list.append(ElectrodeGUI(electrode, self.ui.electrode_layout))
                    
                self.ui.laser_sections_connect.setText(DISCONNECT_STRING)
                self.ui.refresh_check.setEnabled(True)
                
                for electrodeGUI in self.electrode_GUI_list:
                    electrodeGUI.enable_gui()
                    electrodeGUI.input_slot()
            except:
                msgbox("Connection Error")
                traceback.print_exc()
        
    def save_settings_slot(self):
        filename = format(QtGui.QFileDialog.getSaveFileName(self,
                                                     'Open config file',
                                                     '',
                                                     "Config File (*.cfg)"))
        if len(filename) == 0:
            return
        if not filename.endswith('.cfg'):
            filename += '.cfg'
        
        file = open(filename, 'w')
        file.write(format(self.ui.laser_sections.currentIndex()) + '\n')
#         file.write(self.ui.voltage_compliance.text() + '\n')
#         file.write(self.ui.current_compliance.text() + '\n')
        file.write(format(self.ui.gpib_connection.currentIndex()) + '\n')
        file.write(self.ui.gpib_connection_text.text() + '\n')
        file.write(self.ui.refresh_seconds.text() + '\n')
        file.write(self.ui.wavemeter_gpib.text() + '\n')
        file.write(self.ui.osa_ip.text() + '\n')
        
        for laser_section in self.laser_section_list:
            laser_section.write_settings(file)
        
        file.close()
        
    def load_settings_slot(self):
        filename = QtGui.QFileDialog.getOpenFileName(self,
                                                     'Open config file',
                                                     '',
                                                     "Config File (*.cfg)")
        if len(filename) == 0:
            return
        
        self.load_settings(filename)
        
    def load_settings(self, filename):
        file = open(filename, 'r')
        #self.ui.laser_sections_combo.setCurrentIndex(int(file.readline().splitlines()[0]))
        self.ui.laser_sections.setCurrentIndex(int(file.readline().splitlines()[0]))
#         self.ui.voltage_compliance.setText(file.readline().splitlines()[0])
#         self.ui.current_compliance.setText(file.readline().splitlines()[0])
        self.ui.gpib_connection.setCurrentIndex(int(file.readline().splitlines()[0]))
        self.ui.gpib_connection_text.setText(file.readline().splitlines()[0])
        self.ui.refresh_seconds.setText(file.readline().splitlines()[0])
        self.ui.wavemeter_gpib.setText(file.readline().splitlines()[0])
        self.ui.osa_ip.setText(file.readline().splitlines()[0])
        
        for laser_section in self.laser_section_list:
            laser_section.read_settings(file)
            #laser_section.source_type_slot()
            if self.station is not None:
                laser_section.input_slot()
        
        file.close()
        
    def is_connect_slot(self):
        if self.integrating_sphere is not None:
            self.integrating_sphere.close()
            self.integrating_sphere = None
            self.ui.is_connect.setText(CONNECT_STRING)
            self.ui.is_get_value.setEnabled(False)
        else:
            self.integrating_sphere = PM100USB.PowerMonitor()
            self.ui.is_connect.setText(DISCONNECT_STRING)
            self.ui.is_get_value.setEnabled(True)
    
    def is_get_value_slot(self):
        self.ui.is_value.setText(format((self.integrating_sphere.read_value() * 1000), OUTPUT_FORMAT))
        
    def wm_connect_slot(self):
        if self.wavemeter is not None:
            #self.wavemeter.closesocket()
            self.wavemeter = None
            self.ui.wavemeter_connect.setText(CONNECT_STRING)
            self.ui.wm_get_values.setEnabled(False)
        else:
            if self.gpib_interface is None:
                if self.ui.gpib_connection.currentIndex() == GPIB_VISA:
                    from testsuite.instruments import gpib_visa_interface
                    self.gpib_interface = gpib_visa_interface.Interface(int(self.ui.gpib_connection_text.text()), gpib_board=int(self.ui.gpib_connection_bus.text()))
                if self.ui.gpib_connection.currentIndex() == GPIB_PROLOGIX_ETHERNET:
                    from testsuite.instruments import gpib_ethernet_socket
                    self.gpib_interface = gpib_ethernet_socket.GPIBEthernet(self.ui.gpib_connection_text.text())
                if self.ui.gpib_connection.currentIndex() == GPIB_PROLOGIX_USB:
                    from testsuite.instruments import gpib_usb_proligix
                    self.gpib_interface = gpib_usb_proligix.Interface(self.ui.gpib_connection_text.text())
                if self.ui.gpib_connection.currentIndex() == GPIB_DUMMY:
                    from testsuite.instruments import gpib_ethernet_socket_dummy
                    self.gpib_interface = gpib_ethernet_socket_dummy.GPIBEthernet()
                    print("interface")
                    
            self.wavemeter = HP86120B.OSA(self.gpib_interface, int(self.ui.wavemeter_gpib.text()))
            self.ui.wavemeter_connect.setText(DISCONNECT_STRING)
            self.ui.wm_get_values.setEnabled(True)
    def wm_get_values_slot(self):
        peaks = self.wavemeter.readpeak()
        self.ui.wm_peak1_wavelength.setText('---')
        self.ui.wm_peak2_wavelength.setText('---')
        self.ui.wm_peak1_power.setText('---')
        self.ui.wm_peak2_power.setText('---')
        
        if len(peaks) > 0:
            self.ui.wm_peak1_wavelength.setText(format(peaks[0]["wavelength"]))
            self.ui.wm_peak1_power.setText(format(peaks[0]["power"]))
        if len(peaks) > 1:
            self.ui.wm_peak2_wavelength.setText(format(peaks[1]["wavelength"]))
            self.ui.wm_peak2_power.setText(format(peaks[1]["power"]))
            
    def osa_disable_gui(self):
        self.ui.osa_vbw.setEnabled(False)
        self.ui.osa_resolution.setEnabled(False)
        self.ui.osa_sampling.setEnabled(False)
        self.ui.osa_start_stop_save.setEnabled(False)
        self.ui.osa_center_span_save.setEnabled(False)
        self.ui.osa_sweep.setEnabled(False)

    def osa_connect_slot(self):
        if self.osa is not None:
            self.osa.close()
            self.osa = None
            self.ui.osa_connect.setText(CONNECT_STRING)
            self.osa_disable_gui()
        else:
            self.osa = MS9740.OSA(format(self.ui.osa_ip.text()))
            self.ui.osa_connect.setText(DISCONNECT_STRING)
            
            #Pull values from OSA
            self.ui.osa_vbw.setCurrentIndex(OSA_VBW.index(self.osa.read_video_bandwidth()))
            self.ui.osa_resolution.setCurrentIndex(OSA_RESOLUTION.index(self.osa.read_resolution()))
            self.ui.osa_sampling.setCurrentIndex(OSA_SAMPLING.index(self.osa.read_sampling_points()))
            
            self.ui.osa_start.setText(format(self.osa.read_start_wavelength()))
            self.ui.osa_stop.setText(format(self.osa.read_stop_wavelength()))
            self.ui.osa_center.setText(format(self.osa.read_center_wavelength()))
            self.ui.osa_span.setText(format(self.osa.read_span()))
            
            self.ui.osa_vbw.setEnabled(True)
            self.ui.osa_resolution.setEnabled(True)
            self.ui.osa_sampling.setEnabled(True)
            self.ui.osa_start_stop_save.setEnabled(True)
            self.ui.osa_center_span_save.setEnabled(True)
            self.ui.osa_sweep.setEnabled(True)
            
    def osa_vbw_slot(self):
        if self.ui.osa_vbw.isEnabled():
            self.osa.set_video_bandwidth(OSA_VBW[self.ui.osa_vbw.currentIndex()])
            
    def osa_resolution_slot(self):
        if self.ui.osa_resolution.isEnabled():
            self.osa.set_resolution(OSA_RESOLUTION[self.ui.osa_resolution.currentIndex()])
            self.ui.osa_sampling.setCurrentIndex(OSA_SAMPLING.index(self.osa.read_sampling_points()))
            
    def osa_sampling_slot(self):
        if self.ui.osa_sampling.isEnabled():
            self.osa.set_sampling_points(OSA_SAMPLING[self.ui.osa_sampling.currentIndex()])
            self.ui.osa_resolution.setCurrentIndex(OSA_RESOLUTION.index(self.osa.read_resolution()))
            
    def osa_start_stop_slot(self):
        self.osa.set_start_wavelength(float(self.ui.osa_start.text()))
        self.osa.set_stop_wavelength(float(self.ui.osa_stop.text()))
        
        self.ui.osa_center.setText(format(self.osa.read_center_wavelength()))
        self.ui.osa_span.setText(format(self.osa.read_span()))
        
    def osa_center_span_slot(self):
        self.osa.set_center_wavelength(float(self.ui.osa_center.text()))
        self.osa.set_span(float(self.ui.osa_span.text()))
        
        self.ui.osa_start.setText(format(self.osa.read_start_wavelength()))
        self.ui.osa_stop.setText(format(self.osa.read_stop_wavelength()))
        
    def osa_sweep_slot(self):
        self.ui.osa_progress.setMaximum(0)
        QtGui.QApplication.processEvents()
        self.osa.sweep_single()
        def osa_callback():
            QtGui.QApplication.processEvents()
        self.osa.wait_for_sweepcomplete(callback=osa_callback)
        self.ui.osa_smsr.setText(format(self.osa.read_smsr()))
        
        peaks = self.osa.readpeak()
        self.ui.osa_peak1_wavelength.setText('---')
        self.ui.osa_peak2_wavelength.setText('---')
        self.ui.osa_peak1_power.setText('---')
        self.ui.osa_peak2_power.setText('---')
        if len(peaks) > 0:
            self.ui.osa_peak1_wavelength.setText(format(peaks[0]["wavelength"]))
            self.ui.osa_peak1_power.setText(format(peaks[0]["power"]))
        if len(peaks) > 1:
            self.ui.osa_peak2_wavelength.setText(format(peaks[1]["wavelength"]))
            self.ui.osa_peak2_power.setText(format(peaks[1]["power"]))
         
        trace_data = self.osa.read_trace_memory_A()
        self.ui.osa_trace_plot.axes.plot(list(zip(*trace_data))[0], list(zip(*trace_data))[1])
        self.ui.osa_trace_plot.draw()
        self.ui.osa_progress.setMaximum(100)
        
    def zero_laser_slot(self):
        for electrodeGUI in self.electrode_GUI_list:
            electrodeGUI.zero_section()
            
    def refresh_slot(self):
        if self.ui.refresh_check.isChecked():
            self.refresh_timer_slot()
            self.refresh_timer.start(float(self.ui.refresh_seconds.text()) * 1000)
        else:
            self.refresh_timer.stop()
            
    def refresh_timer_slot(self):
        for electrodeGUI in self.electrode_GUI_list:
            electrodeGUI.output()
        
    def closeEvent(self, event):
        if self.station is not None:
            self.station.close()
        if self.integrating_sphere is not None:
            self.integrating_sphere.close()
        if self.gpib_interface is not None:
            self.gpib_interface.closesocket()
        if self.osa is not None:
            self.osa.close()
        event.accept()
                
def msgbox(message):
    msgbox = QtGui.QMessageBox()
    msgbox.setText(message)
    msgbox.exec_()