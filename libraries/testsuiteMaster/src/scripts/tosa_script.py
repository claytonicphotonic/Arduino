'''
Created on Mar 4, 2014

@author: bay
'''

import sys, os
from datetime import datetime
import numpy as np

sys.path.insert(0, os.path.abspath('../'))

from testsuite.tests import tosa_tests
from testsuite.instruments import test_stations
from testsuite.instruments import HP86120B
#from testsuite.instruments import gpib_ethernet_socket
from testsuite.instruments import gpib_visa_interface
from testsuite.instruments import PM100USB
from testsuite.instruments import MS9740
import traceback

fname = input('Enter the Device UID: ')
BUILD = input('Enter number for build status: 1=BAR, 2=DIE, 3=COC, 4=FOC, 5=TOSA, 6=SFP, 7=dummy_data :')
if BUILD == 1:
    Build_string = 'BAR'
elif BUILD == 2:
    Build_string = 'DIE'
elif BUILD == 3:
    Build_string = 'COC'
elif BUILD== 4:
    Build_string = 'FOC'
elif BUILD == 5:
    Build_string = 'TOSA'
elif BUILD== 6:
    Build_string = 'SFP'
elif BUILD== 7:
    Build_string = 'DUMMY'
    
dcrf = raw_input('dc or rf? : ')
if (dcrf == 'dc'):
    test_station = test_stations.TestStationDC(nplc=0.2)
    #wavemeter_interface = gpib_visa_interface.Interface(11)
else:
    test_station = test_stations.TestStationRF_TOSA()
    wavemeter_interface = gpib_visa_interface.Interface(11, gpib_board=1)
    
path_base = 'G:\\10G TOSA Product\\PIC Development\\PIC_Measurement_Data\\UID' + format(fname) + '\\DC_Raw_Data\\' + Build_string + '\\'

#gpib_ethernet_socket = gpib_ethernet_socket.GPIBEthernet("192.168.1.89", 1234, timeout=2000000, ip_timeout=2)

#tec = LDT5910B.TEC(gpib_ethernet_socket, "5")
#wavemeter = HP86120B.OSA(wavemeter_interface, "11")

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

print(path_base + 'GV\\Gain_Voltage_Map_Data' + timestamp)

try:
    LASER_PHASE_MIN = 0.0
    LASER_PHASE_MAX = 0.1 #Non-inclusive
    LASER_PHASE_STEP = 2.0
    
    crude_itu_grid_fitter_filename = path_base + 'GV\\ITU_Crude' + timestamp + '.csv'
    # index list format index_list=[10,40,60,90]
    tosa_tests.generate_blank_itu(output_filename=crude_itu_grid_fitter_filename, index_list=None)
    
    for laser_phase in np.arange(LASER_PHASE_MIN, LASER_PHASE_MAX, LASER_PHASE_STEP):
        print("GV Test " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        gain_voltage_map_filename = path_base + 'GV\\LasPhase' + format(laser_phase) + '\\Gain_Voltage_Map_Data' + timestamp + '.csv'
        tosa_tests.gain_voltage_map(gain_voltage_map_filename, 
                                                    path_base + 'GV\\LasPhase' + format(laser_phase) + '\\Gain_Voltage_Map_Data' + timestamp, 
                                                    test_station, 
                                                    min_current=0.0, 
                                                    max_current=50.0, 
                                                    num_current_steps=50, 
                                                    laser_phase_current=laser_phase)
        
        #Gain 1
        print("Minima Finder Gain" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        minima_finder_filename = path_base + 'GV\\LasPhase' + format(laser_phase) + '\\Minima_Data_Gain' + timestamp + '.csv'
        tosa_tests.minima_finder(gain_voltage_map_filename, 
                      minima_finder_filename, 
                      output_img_filename=path_base + 'GV\\LasPhase' + format(laser_phase) + '\\Minima_Data_Gain' + timestamp + '.png', 
                      magnitude_section=tosa_tests.GAIN1)
                      
#        print("Wavelength Finder Gain" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
#        wavelength_finder_filename = path_base + 'GV\\LasPhase' + format(laser_phase) + '\\Wavelength_Data_Gain' + timestamp + '.csv'
#        tosa_tests.wavelength_finder(input_filename=minima_finder_filename,
#                          output_filename=wavelength_finder_filename, 
#                          wavemeter=wavemeter, 
#                          test_station=test_station)
#    
#        print("Crude ITU Gain" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
#        tosa_tests.crude_itu_grid_fitter(input_filename=wavelength_finder_filename, 
#                              output_filename=crude_itu_grid_fitter_filename, 
#                              output_power_minimum=-50.0)
                                                            
#        #SOA1
#        print("Minima Finder SOA1" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
#        minima_finder_filename = path_base + 'GV\\LasPhase' + format(laser_phase) + '\\Minima_Data_SOA1' + timestamp + '.csv'
#        testsuite.tests.tosa_tests.minima_finder(gain_voltage_map_filename, 
#                      minima_finder_filename, 
#                      output_img_filename=path_base + 'GV\\LasPhase' + format(laser_phase) + '\\Minima_Data_SOA1' + timestamp + '.png', 
#                      magnitude_section=testsuite.tests.tosa_tests.SOA1)
#                      
#        print("Wavelength Finder SOA1" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
#        wavelength_finder_filename = path_base + 'GV\\LasPhase' + format(laser_phase) + '\\Wavelength_Data_SOA1' + timestamp + '.csv'
#        testsuite.tests.tosa_tests.wavelength_finder(input_filename=minima_finder_filename,
#                          output_filename=wavelength_finder_filename, 
#                          osa=wavemeter, 
#                          laser_sections=laser_sections)
#    
#        print("Crude ITU SOA1" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
#        testsuite.tests.tosa_tests.crude_itu_grid_fitter(input_filename=wavelength_finder_filename, 
#                              output_filename=crude_itu_grid_fitter_filename, 
#                              output_power_minimum=-25.0)
#                              
#                              
#        #SOA2
#        print("Minima Finder SOA2" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
#        minima_finder_filename = path_base + 'GV\\LasPhase' + format(laser_phase) + '\\Minima_Data_SOA2' + timestamp + '.csv'
#        testsuite.tests.tosa_tests.minima_finder(gain_voltage_map_filename, 
#                      minima_finder_filename, 
#                      output_img_filename=path_base + 'GV\\LasPhase' + format(laser_phase) + '\\Minima_Data_SOA2' + timestamp + '.png', 
#                      magnitude_section=testsuite.tests.tosa_tests.SOA2)
#                      
#        print("Wavelength Finder SOA2" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
#        wavelength_finder_filename = path_base + 'GV\\LasPhase' + format(laser_phase) + '\\Wavelength_Data_SOA2' + timestamp + '.csv'
#        testsuite.tests.tosa_tests.wavelength_finder(input_filename=minima_finder_filename,
#                          output_filename=wavelength_finder_filename, 
#                          osa=wavemeter, 
#                          laser_sections=laser_sections)
#    
#        print("Crude ITU SOA2" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
#        testsuite.tests.tosa_tests.crude_itu_grid_fitter(input_filename=wavelength_finder_filename, 
#                              output_filename=crude_itu_grid_fitter_filename, 
#                              output_power_minimum=-25.0)

#    if (dcrf == 'dc'):
#        test_station.close()
#        test_station = test_stations.TestStationDC(nlpc=0.2)
#    
#    print("Fine ITU " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
#    fine_itu_grid_fitter_filename = path_base + 'GV\\ITU_Fine' + timestamp + '.csv'
#    fine_itu_grid_fitter_debug_filename = path_base + 'GV\\ITU_Fine_debug' + timestamp + '.csv'
#    tosa_tests.fine_itu_grid_fitter(input_filename=crude_itu_grid_fitter_filename, 
#                         output_filename=fine_itu_grid_fitter_filename, 
#                         test_station=test_station, 
#                         wavemeter=wavemeter, 
#                         laser_phase_step=.2, 
#                         laser_phase_max_delta=1.6, #Non-inclusive
#                         debug_filename=fine_itu_grid_fitter_debug_filename)
#    
#    print("SOA Balancing " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
#    balance_SOAs_filename = path_base + 'GV\\ITU_SOA_Balanced' + timestamp + '.csv'
#    tosa_tests.balance_SOAs(input_filename=fine_itu_grid_fitter_filename, 
#                 output_filename=balance_SOAs_filename, 
#                 test_station=test_station)
#    
#    print("1d Mod Phase Sweep " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
#    power_monitor = PM100USB.PowerMonitor()
#    sweep_1d_phase_ITU_filename = path_base + 'GV\\ITU_Mod_phase' + timestamp + '.csv'
#    tosa_tests.sweep_1d_phase_ITU(input_filename=balance_SOAs_filename, 
#                       output_filename=sweep_1d_phase_ITU_filename, 
#                       test_station=test_station, 
#                       Phase1_current_start=0.0, 
#                       Phase1_current_end=10.0,
#                       Phase1_step=0.1, 
#                       power_monitor=power_monitor, 
#                       sweep_data_folder=path_base + 'GV\\ITU_Mod_phase_data_' + timestamp + '\\', 
#                       sweep_img_folder=path_base + 'GV\\ITU_Mod_phase_data_' + timestamp + '\\')
#                    
#    print("2d MZM Sweep " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
#    mzm_2d_path = path_base + 'GV\\MZM_2d_' + timestamp
#    tosa_tests.MZM_2d_ITU(input_filename=sweep_1d_phase_ITU_filename, 
#               output_data_path=mzm_2d_path, 
#               test_station=test_station, 
#               power_monitor=power_monitor, 
#               mzm_voltage_min=0.0, 
#               mzm_voltage_max=-6.0, 
#               mzm_voltage_step=-0.1)
    
#    while True:
#        prompt = input("Switch bench to use splitter to OSA & wavemeter, then type 123: ")
#        if prompt == 123:
#            break
#        
#    osa = MS9740.OSA("192.168.1.121")
#    
#    print("Exit Criteria Test " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
#    verify_filename = path_base + 'GV\\WavetableVerification' + timestamp + '.csv'
#    tosa_tests.verify_wavetable(input_filename=sweep_1d_phase_ITU_filename, 
#                     test_station=test_station, 
#                     full_osa=osa, 
#                     wavemeter=wavemeter, 
#                     output_filename=verify_filename, 
#                     minimum_power=-50.0, 
#                     minimum_smsr=10.0, 
#                     maximum_itu_delta=.1)
                         
    print("Finish " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
except:
    print("ERROR")
    traceback.print_exc()
finally:
    test_station.close()
    #wavemeter_interface.closesocket()