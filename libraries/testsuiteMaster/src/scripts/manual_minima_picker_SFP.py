'''
Created on May 30, 2014

@author: bay
'''

import sys, os
from datetime import datetime

sys.path.insert(0, os.path.abspath('../'))

import testsuite.tests.tosa_tests
#from testsuite.instruments import laser_sections_sfp
from testsuite.instruments import test_stations
import traceback
import time

fname = input('Enter the Device UID: ')
serial_port = input('Enter Serial Port Connections String: ')
    
Build_string = 'SFP'
    
path_base = 'C:\\Users\\tcicchi\\Documents\\GitHub\\testsuite\\data\\UID' + format(fname) + '\\DC_Raw_Data\\' + Build_string + '\\'

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

print(path_base + 'GV\\Gain_Voltage_Map_Data' + timestamp)

try:
    
    crude_itu_grid_fitter_filename = path_base + 'GV\\ITU_Crude' + timestamp + '.csv'
    # index list format index_list=[10,40,60,90]
    testsuite.tests.tosa_tests.generate_blank_itu(output_filename=crude_itu_grid_fitter_filename)
    
    test_station = test_stations.TestStationSFP(serial_port)
    
    print("GV Test " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    gain_voltage_map_filename = path_base + 'GV\\LasPhaseLOCKED\\Gain_Voltage_Map_Data' + timestamp + '.csv'
    def locker_callback():
        test_station.set_locker_on(False)
        test_station.set_locker_on(True)
        # laser phase time constant is read below as milliseconds; locker takes 1/5 second
        # when time constant is 100 us
        time.sleep(.21 * test_station.read_laser_phase_time_constant() * 10) 
        return test_station.laser_phase.read_set_current()
    def progress_callback(progress, max_progress):
        if progress % 10 == 0:
            print(format(progress) + '/' + format(max_progress) + ": " + format((float(progress) / max_progress) * 100, '.2f') + '%')
    testsuite.tests.tosa_tests.gain_voltage_map(gain_voltage_map_filename, 
                                                path_base + 'GV\\LasPhaseLOCKED\\Gain_Voltage_Map_Data' + timestamp, 
                                                test_station, 
                                                min_current=0.0, 
                                                max_current=40.0, 
                                                num_current_steps=40,
                                                locker_callback=locker_callback, 
                                                progress_callback = progress_callback, 
                                                record_photocurrents=False)
    
    #Gain 1
    print("Manual Minima Finder Gain" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    minima_finder_filename = path_base + 'GV\\LasPhaseLOCKED\\Manual_Minima_Data_Gain' + timestamp + '.csv'
    testsuite.tests.tosa_tests.manual_minima_finder(gain_voltage_map_filename, 
                  minima_finder_filename, 
                  output_img_filename=path_base + 'GV\\LasPhaseLOCKED\\Manual_Minima_Data_Gain' + timestamp + '.png', 
                  magnitude_section=testsuite.tests.tosa_tests.GAIN1)
                  
#         print("Wavelength Finder Gain" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
#         wavelength_finder_filename = path_base + 'GV\\LasPhase' + format(laser_phase) + '\\Wavelength_Data_Gain' + timestamp + '.csv'
#         testsuite.tests.tosa_tests.wavelength_finder(input_filename=minima_finder_filename,
#                           output_filename=wavelength_finder_filename, 
#                           osa=wavemeter, 
#                           laser_sections=laser_sections)
#     
#         print("Crude ITU Gain" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
#         testsuite.tests.tosa_tests.crude_itu_grid_fitter(input_filename=wavelength_finder_filename, 
#                               output_filename=crude_itu_grid_fitter_filename, 
#                               output_power_minimum=-25.0)
                         
    print("Finish " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
except:
    print("ERROR")
    traceback.print_exc()
finally:
    test_station.close()