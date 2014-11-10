'''
Created on May 5, 2014

@author: bay
'''
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QMainWindow

import os
from datetime import datetime
from PyQt4 import QtGui, QtCore

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib

from . ui_iv_curves import Ui_MainWindow
from testsuite.tests import tosa_tests
from testsuite.instruments import test_stations

LASER_SECTIONS_KEITHLEYS = 0
LASER_SECTIONS_NI_BOX_TOSA = 1
LASER_SECTIONS_NI_BOX_COC = 2
LASER_SECTIONS_SFP = 3
LASER_SECTIONS_DUMMY = 4

START_BUTTON_TEXT = "RUN"
STOP_BUTTON_TEXT = "STOP"

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
    
class IV_Curves(QMainWindow):
    def __init__(self):
        QWidget.__init__(self)
        
        # Set up the user interface from Designer.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.show()
        self.ui.run_button.clicked.connect(self.run_slot)
        self.ui.save_settings_button.clicked.connect(self.save_settings_slot)
        self.ui.load_settings_button.clicked.connect(self.load_settings_slot)
        
        self.load_settings(os.getcwd() + os.sep + 'testsuite' + os.sep + 'iv_curves_gui' + os.sep + 'DEFAULT.cfg') #This should not be hardcoded, I should be able to get this programmatically
        
        matplotlib.rcParams.update({'font.size': 6})
        
        self.ui.mirror1_plot = MplCanvas()
        self.ui.mirror1_plot_layout.addWidget(self.ui.mirror1_plot)
        self.ui.mirror2_plot = MplCanvas()
        self.ui.mirror2_plot_layout.addWidget(self.ui.mirror2_plot)
        self.ui.gain_plot = MplCanvas()
        self.ui.gain_plot_layout.addWidget(self.ui.gain_plot)
        self.ui.soa1_plot = MplCanvas()
        self.ui.soa1_plot_layout.addWidget(self.ui.soa1_plot)
        self.ui.soa2_plot = MplCanvas()
        self.ui.soa2_plot_layout.addWidget(self.ui.soa2_plot)
        self.ui.laspha_plot = MplCanvas()
        self.ui.laspha_plot_layout.addWidget(self.ui.laspha_plot)
        self.ui.phase1_plot = MplCanvas()
        self.ui.phase1_plot_layout.addWidget(self.ui.phase1_plot)
        self.ui.mod1_plot = MplCanvas()
        self.ui.mod1_plot_layout.addWidget(self.ui.mod1_plot)
        self.ui.mod2_plot = MplCanvas()
        self.ui.mod2_plot_layout.addWidget(self.ui.mod2_plot)
        self.ui.detector_plot = MplCanvas()
        self.ui.detector_plot_layout.addWidget(self.ui.detector_plot)
        
        self.enabled_checks = [self.ui.mirror1_check, self.ui.mirror2_check, self.ui.gain_check, self.ui.soa1_check, self.ui.soa2_check, self.ui.laspha_check, self.ui.phase1_check, self.ui.mod1_check, self.ui.mod2_check, self.ui.detector_check]
#         type_combos = [self.ui.mirror1_type_combo, self.ui.mirror2_type_combo, self.ui.gain_type_combo, self.ui.soa1_type_combo, self.ui.soa2_type_combo, self.ui.laspha_type_combo, self.ui.phase1_type_combo, self.ui.mod1_type_combo, self.ui.mod2_type_combo, self.ui.detector_type_combo]
#         start_text_boxes = [self.ui.mirror1_start_text, self.ui.mirror2_start_text, self.ui.gain_start_text, self.ui.soa1_start_text, self.ui.soa2_start_text, self.ui.laspha_start_text, self.ui.phase1_start_text, self.ui.mod1_start_text, self.ui.mod2_start_text, self.ui.detector_start_text]
#         stop_text_boxes = [self.ui.mirror1_stop_text, self.ui.mirror2_stop_text, self.ui.gain_stop_text, self.ui.soa1_stop_text, self.ui.soa2_stop_text, self.ui.laspha_stop_text, self.ui.phase1_stop_text, self.ui.mod1_stop_text, self.ui.mod2_stop_text, self.ui.detector_stop_text]
#         step_text_boxes = [self.ui.mirror1_step_text, self.ui.mirror2_step_text, self.ui.gain_step_text, self.ui.soa1_step_text, self.ui.soa2_step_text, self.ui.laspha_step_text, self.ui.phase1_step_text, self.ui.mod1_step_text, self.ui.mod2_step_text, self.ui.detector_step_text]
#         plots = [self.ui.mirror1_plot, self.ui.mirror2_plot, self.ui.gain_plot, self.ui.soa1_plot, self.ui.soa2_plot, self.ui.laspha_plot, self.ui.phase1_plot, self.ui.mod1_plot, self.ui.mod2_plot, self.ui.detector_plot]

        self.curves_running = False
        
    def run_slot(self):
#         x = arange(0, 10 * random.random(), 0.1)
#         y = sin(x)
#         
#         self.ui.plt_window.axes.plot(x, y)
#         self.ui.plt_window.draw()
        if self.curves_running:
            self.curves_running = False
        else:
            self.curves_running = True
            self.ui.run_button.setText(STOP_BUTTON_TEXT)
            total_curves = 0
            for checkbox in self.enabled_checks:
                if checkbox.isChecked():
                    total_curves += 1
                    
            self.ui.major_progress.setMaximum(total_curves)
            self.ui.major_progress.setValue(0)
            
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.ui.timestamp_label.setText(timestamp)
            
            def iv_curve_callback(progress_value, progress_max):
                self.ui.minor_progress.setMaximum(progress_max)
                self.ui.minor_progress.setValue(progress_value)
                QtGui.QApplication.processEvents()
                if self.curves_running == False:
                    raise tosa_tests.StopButtonException
    
            try:
                if self.ui.laser_sections_combo.currentIndex() == LASER_SECTIONS_KEITHLEYS:
#                     from testsuite.instruments import laser_sections_TOSA_keithleys
#                     laser_sections = laser_sections_TOSA_keithleys.LaserSections()
                    station = test_stations.TestStationDC(output_on_all=False)
                elif self.ui.laser_sections_combo.currentIndex() == LASER_SECTIONS_NI_BOX_TOSA:
#                     from testsuite.instruments import laser_sections_ni_box
#                     laser_sections = laser_sections_ni_box.LaserSections()
                    station = test_stations.TestStationRF_TOSA(output_on_all=False)
                elif self.ui.laser_sections_combo.currentIndex() == LASER_SECTIONS_NI_BOX_COC:
#                     from testsuite.instruments import laser_sections_ni_box
#                     laser_sections = laser_sections_ni_box.LaserSections()
                    station = test_stations.TestStationRF_COC(output_on_all=False)
                elif self.ui.laser_sections_combo.currentIndex() == LASER_SECTIONS_SFP:
#                     from testsuite.instruments import laser_sections_sfp
                    raise IOError("SFP is not implemented yet, need to add ability to select serial port")
                elif self.ui.laser_sections_combo.currentIndex() == LASER_SECTIONS_DUMMY:
#                     from testsuite.instruments import laser_sections_dummy
#                     laser_sections = laser_sections_dummy.LaserSections()
                    station = test_stations.TestStationDummy()
                
                base_filepath = format(self.ui.filepath_base.text() + 'UID' + self.ui.uid_text.text() + os.sep + 'DC_Raw_Data' + os.sep + self.ui.laser_stage_combo.currentText() + os.sep + 'IV' + os.sep)
                
                if self.ui.mirror1_check.isChecked():
                    station.zero_all()
                    station.set_output_on_all(False)
                    station.mirror1.set_output_on(True)
                    tosa_tests.IV_curve(output_filename=base_filepath + timestamp + 'mirror1.csv',
                                        input_function=station.mirror1.write_current, 
                                        input_title='mirror1_current', 
                                        output_function=station.mirror1.read_voltage, 
                                        output_title='mirror1_voltage', 
                                        input_min=float(self.ui.mirror1_start_text.text()), 
                                        input_max=float(self.ui.mirror1_stop_text.text()), 
                                        input_step=float(self.ui.mirror1_step_text.text()), 
                                        output_img_filename=base_filepath + timestamp + 'mirror1.png', 
                                        progress_callback=iv_curve_callback, 
                                        plot_widget=self.ui.mirror1_plot)
                    self.ui.major_progress.setValue(self.ui.major_progress.value() + 1)
                if self.ui.mirror2_check.isChecked():
                    station.zero_all()
                    station.set_output_on_all(False)
                    station.mirror2.set_output_on(True)
                    tosa_tests.IV_curve(output_filename=base_filepath + timestamp + 'mirror2.csv',
                                        input_function=station.mirror2.write_current, 
                                        input_title='mirror2_current', 
                                        output_function=station.mirror2.read_voltage, 
                                        output_title='mirror2_voltage', 
                                        input_min=float(self.ui.mirror2_start_text.text()), 
                                        input_max=float(self.ui.mirror2_stop_text.text()), 
                                        input_step=float(self.ui.mirror2_step_text.text()), 
                                        output_img_filename=base_filepath + timestamp + 'mirror2.png', 
                                        progress_callback=iv_curve_callback, 
                                        plot_widget=self.ui.mirror2_plot)
                    self.ui.major_progress.setValue(self.ui.major_progress.value() + 1)
                if self.ui.gain_check.isChecked():
                    station.zero_all()
                    station.set_output_on_all(False)
                    station.gain1.set_output_on(True)
                    tosa_tests.IV_curve(output_filename=base_filepath + timestamp + 'gain.csv',
                                        input_function=station.gain1.write_current, 
                                        input_title='gain_current', 
                                        output_function=station.gain1.read_voltage, 
                                        output_title='gain_voltage', 
                                        input_min=float(self.ui.gain_start_text.text()), 
                                        input_max=float(self.ui.gain_stop_text.text()), 
                                        input_step=float(self.ui.gain_step_text.text()), 
                                        output_img_filename=base_filepath + timestamp + 'gain.png', 
                                        progress_callback=iv_curve_callback, 
                                        plot_widget=self.ui.gain_plot)
                    self.ui.major_progress.setValue(self.ui.major_progress.value() + 1)
                if self.ui.soa1_check.isChecked():
                    station.zero_all()
                    station.set_output_on_all(False)
                    station.soa1.set_output_on(True)
                    tosa_tests.IV_curve(output_filename=base_filepath + timestamp + 'soa1.csv',
                                        input_function=station.soa1.write_current, 
                                        input_title='soa1_current', 
                                        output_function=station.soa1.read_voltage, 
                                        output_title='soa1_voltage', 
                                        input_min=float(self.ui.soa1_start_text.text()), 
                                        input_max=float(self.ui.soa1_stop_text.text()), 
                                        input_step=float(self.ui.soa1_step_text.text()), 
                                        output_img_filename=base_filepath + timestamp + 'soa1.png', 
                                        progress_callback=iv_curve_callback, 
                                        plot_widget=self.ui.soa1_plot)
                    self.ui.major_progress.setValue(self.ui.major_progress.value() + 1)
                if self.ui.soa2_check.isChecked():
                    station.zero_all()
                    station.set_output_on_all(False)
                    station.soa2.set_output_on(True)
                    tosa_tests.IV_curve(output_filename=base_filepath + timestamp + 'soa2.csv',
                                        input_function=station.soa2.write_current, 
                                        input_title='soa2_current', 
                                        output_function=station.soa2.read_voltage, 
                                        output_title='soa2_voltage', 
                                        input_min=float(self.ui.soa2_start_text.text()), 
                                        input_max=float(self.ui.soa2_stop_text.text()), 
                                        input_step=float(self.ui.soa2_step_text.text()), 
                                        output_img_filename=base_filepath + timestamp + 'soa2.png', 
                                        progress_callback=iv_curve_callback, 
                                        plot_widget=self.ui.soa2_plot)
                    self.ui.major_progress.setValue(self.ui.major_progress.value() + 1)
                if self.ui.laspha_check.isChecked():
                    station.zero_all()
                    station.set_output_on_all(False)
                    station.laser_phase.set_output_on(True)
                    tosa_tests.IV_curve(output_filename=base_filepath + timestamp + 'laspha.csv',
                                        input_function=station.laser_phase.write_current, 
                                        input_title='laspha_current', 
                                        output_function=station.laser_phase.read_voltage, 
                                        output_title='laspha_voltage', 
                                        input_min=float(self.ui.laspha_start_text.text()), 
                                        input_max=float(self.ui.laspha_stop_text.text()), 
                                        input_step=float(self.ui.laspha_step_text.text()), 
                                        output_img_filename=base_filepath + timestamp + 'laspha.png', 
                                        progress_callback=iv_curve_callback, 
                                        plot_widget=self.ui.laspha_plot)
                    self.ui.major_progress.setValue(self.ui.major_progress.value() + 1)
                if self.ui.phase1_check.isChecked():
                    station.zero_all()
                    station.set_output_on_all(False)
                    station.phase1.set_output_on(True)
                    tosa_tests.IV_curve(output_filename=base_filepath + timestamp + 'phase1.csv',
                                        input_function=station.phase1.write_current, 
                                        input_title='phase1_current', 
                                        output_function=station.phase1.read_voltage, 
                                        output_title='phase1_voltage', 
                                        input_min=float(self.ui.phase1_start_text.text()), 
                                        input_max=float(self.ui.phase1_stop_text.text()), 
                                        input_step=float(self.ui.phase1_step_text.text()), 
                                        output_img_filename=base_filepath + timestamp + 'phase1.png', 
                                        progress_callback=iv_curve_callback, 
                                        plot_widget=self.ui.phase1_plot)
                    self.ui.major_progress.setValue(self.ui.major_progress.value() + 1)
                if self.ui.mod1_check.isChecked():
                    station.zero_all()
                    station.set_output_on_all(False)
                    station.modulator1.set_output_on(True)
                    tosa_tests.IV_curve(output_filename=base_filepath + timestamp + 'mod1.csv',
                                        input_function=station.modulator1.write_voltage, 
                                        input_title='mod1_voltage', 
                                        output_function=station.modulator1.read_current, 
                                        output_title='mod1_current', 
                                        input_min=float(self.ui.mod1_start_text.text()), 
                                        input_max=float(self.ui.mod1_stop_text.text()), 
                                        input_step=float(self.ui.mod1_step_text.text()), 
                                        output_img_filename=base_filepath + timestamp + 'mod1.png', 
                                        progress_callback=iv_curve_callback, 
                                        plot_widget=self.ui.mod1_plot)
                    self.ui.major_progress.setValue(self.ui.major_progress.value() + 1)
                if self.ui.mod2_check.isChecked():
                    station.zero_all()
                    station.set_output_on_all(False)
                    station.modulator2.set_output_on(True)
                    tosa_tests.IV_curve(output_filename=base_filepath + timestamp + 'mod2.csv',
                                        input_function=station.modulator2.write_voltage, 
                                        input_title='mod2_voltage', 
                                        output_function=station.modulator2.read_current, 
                                        output_title='mod2_current', 
                                        input_min=float(self.ui.mod2_start_text.text()), 
                                        input_max=float(self.ui.mod2_stop_text.text()), 
                                        input_step=float(self.ui.mod2_step_text.text()), 
                                        output_img_filename=base_filepath + timestamp + 'mod2.png', 
                                        progress_callback=iv_curve_callback, 
                                        plot_widget=self.ui.mod2_plot)
                    self.ui.major_progress.setValue(self.ui.major_progress.value() + 1)
                if self.ui.detector_check.isChecked():
                    station.zero_all()
                    station.set_output_on_all(False)
                    station.detector.set_output_on(True)
                    tosa_tests.IV_curve(output_filename=base_filepath + timestamp + 'detector.csv',
                                        input_function=station.detector.write_voltage, 
                                        input_title='detector_voltage', 
                                        output_function=station.detector.read_current, 
                                        output_title='detector_current', 
                                        input_min=float(self.ui.detector_start_text.text()), 
                                        input_max=float(self.ui.detector_stop_text.text()), 
                                        input_step=float(self.ui.detector_step_text.text()), 
                                        output_img_filename=base_filepath + timestamp + 'detector.png', 
                                        progress_callback=iv_curve_callback, 
                                        plot_widget=self.ui.detector_plot)
                    self.ui.major_progress.setValue(self.ui.major_progress.value() + 1)
            except(tosa_tests.StopButtonException):
                pass
            finally:
                station.close()
                self.curves_running = False
                self.ui.run_button.setText(START_BUTTON_TEXT)
            
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
        file.write(format(self.ui.laser_sections_combo.currentIndex()) + '\n')
        file.write(self.ui.uid_text.text() + '\n')
        file.write(format(self.ui.laser_stage_combo.currentIndex()) + '\n')
        file.write(self.ui.filepath_base.text() + '\n')
        
        file.write(format(self.ui.mirror1_check.isChecked()) + '\n')
        file.write(self.ui.mirror1_start_text.text() + '\n')
        file.write(self.ui.mirror1_stop_text.text() + '\n')
        file.write(self.ui.mirror1_step_text.text() + '\n')
        
        file.write(format(self.ui.mirror2_check.isChecked()) + '\n')
        file.write(self.ui.mirror2_start_text.text() + '\n')
        file.write(self.ui.mirror2_stop_text.text() + '\n')
        file.write(self.ui.mirror2_step_text.text() + '\n')
        
        file.write(format(self.ui.gain_check.isChecked()) + '\n')
        file.write(self.ui.gain_start_text.text() + '\n')
        file.write(self.ui.gain_stop_text.text() + '\n')
        file.write(self.ui.gain_step_text.text() + '\n')
        
        file.write(format(self.ui.soa1_check.isChecked()) + '\n')
        file.write(self.ui.soa1_start_text.text() + '\n')
        file.write(self.ui.soa1_stop_text.text() + '\n')
        file.write(self.ui.soa1_step_text.text() + '\n')
        
        file.write(format(self.ui.soa2_check.isChecked()) + '\n')
        file.write(self.ui.soa2_start_text.text() + '\n')
        file.write(self.ui.soa2_stop_text.text() + '\n')
        file.write(self.ui.soa2_step_text.text() + '\n')
        
        file.write(format(self.ui.laspha_check.isChecked()) + '\n')
        file.write(self.ui.laspha_start_text.text() + '\n')
        file.write(self.ui.laspha_stop_text.text() + '\n')
        file.write(self.ui.laspha_step_text.text() + '\n')
        
        file.write(format(self.ui.phase1_check.isChecked()) + '\n')
        file.write(self.ui.phase1_start_text.text() + '\n')
        file.write(self.ui.phase1_stop_text.text() + '\n')
        file.write(self.ui.phase1_step_text.text() + '\n')
        
        file.write(format(self.ui.mod1_check.isChecked()) + '\n')
        file.write(self.ui.mod1_start_text.text() + '\n')
        file.write(self.ui.mod1_stop_text.text() + '\n')
        file.write(self.ui.mod1_step_text.text() + '\n')
        
        file.write(format(self.ui.mod2_check.isChecked()) + '\n')
        file.write(self.ui.mod2_start_text.text() + '\n')
        file.write(self.ui.mod2_stop_text.text() + '\n')
        file.write(self.ui.mod2_step_text.text() + '\n')
        
        file.write(format(self.ui.detector_check.isChecked()) + '\n')
        file.write(self.ui.detector_start_text.text() + '\n')
        file.write(self.ui.detector_stop_text.text() + '\n')
        file.write(self.ui.detector_step_text.text() + '\n')
        
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
        self.ui.laser_sections_combo.setCurrentIndex(int(file.readline().splitlines()[0]))
        self.ui.uid_text.setText(file.readline().splitlines()[0])
        self.ui.laser_stage_combo.setCurrentIndex(int(file.readline().splitlines()[0]))
        self.ui.filepath_base.setText(file.readline().splitlines()[0])
        
        self.ui.mirror1_check.setChecked(bool(file.readline().splitlines()[0]))
        self.ui.mirror1_start_text.setText(file.readline().splitlines()[0])
        self.ui.mirror1_stop_text.setText(file.readline().splitlines()[0])
        self.ui.mirror1_step_text.setText(file.readline().splitlines()[0])
        
        self.ui.mirror2_check.setChecked(bool(file.readline().splitlines()[0]))
        self.ui.mirror2_start_text.setText(file.readline().splitlines()[0])
        self.ui.mirror2_stop_text.setText(file.readline().splitlines()[0])
        self.ui.mirror2_step_text.setText(file.readline().splitlines()[0])
        
        self.ui.gain_check.setChecked(bool(file.readline().splitlines()[0]))
        self.ui.gain_start_text.setText(file.readline().splitlines()[0])
        self.ui.gain_stop_text.setText(file.readline().splitlines()[0])
        self.ui.gain_step_text.setText(file.readline().splitlines()[0])
        
        self.ui.soa1_check.setChecked(bool(file.readline().splitlines()[0]))
        self.ui.soa1_start_text.setText(file.readline().splitlines()[0])
        self.ui.soa1_stop_text.setText(file.readline().splitlines()[0])
        self.ui.soa1_step_text.setText(file.readline().splitlines()[0])
        
        self.ui.soa2_check.setChecked(bool(file.readline().splitlines()[0]))
        self.ui.soa2_start_text.setText(file.readline().splitlines()[0])
        self.ui.soa2_stop_text.setText(file.readline().splitlines()[0])
        self.ui.soa2_step_text.setText(file.readline().splitlines()[0])
        
        self.ui.laspha_check.setChecked(bool(file.readline().splitlines()[0]))
        self.ui.laspha_start_text.setText(file.readline().splitlines()[0])
        self.ui.laspha_stop_text.setText(file.readline().splitlines()[0])
        self.ui.laspha_step_text.setText(file.readline().splitlines()[0])
        
        self.ui.phase1_check.setChecked(bool(file.readline().splitlines()[0]))
        self.ui.phase1_start_text.setText(file.readline().splitlines()[0])
        self.ui.phase1_stop_text.setText(file.readline().splitlines()[0])
        self.ui.phase1_step_text.setText(file.readline().splitlines()[0])
        
        self.ui.mod1_check.setChecked(bool(file.readline().splitlines()[0]))
        self.ui.mod1_start_text.setText(file.readline().splitlines()[0])
        self.ui.mod1_stop_text.setText(file.readline().splitlines()[0])
        self.ui.mod1_step_text.setText(file.readline().splitlines()[0])
        
        self.ui.mod2_check.setChecked(bool(file.readline().splitlines()[0]))
        self.ui.mod2_start_text.setText(file.readline().splitlines()[0])
        self.ui.mod2_stop_text.setText(file.readline().splitlines()[0])
        self.ui.mod2_step_text.setText(file.readline().splitlines()[0])
        
        self.ui.detector_check.setChecked(bool(file.readline().splitlines()[0]))
        self.ui.detector_start_text.setText(file.readline().splitlines()[0])
        self.ui.detector_stop_text.setText(file.readline().splitlines()[0])
        self.ui.detector_step_text.setText(file.readline().splitlines()[0])
        
        file.close()