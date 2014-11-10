'''
Created on Jul 13, 2014

@author: bay
'''
import sys, os
from datetime import datetime

sys.path.insert(0, os.path.abspath('../'))

from testsuite.tests import tosa_tests
#from testsuite.instruments import LaserSections_c
# from testsuite.instruments import laser_sections_TOSA_keithleys
# from testsuite.instruments import laser_sections_ni_box
from testsuite.instruments import test_stations
from testsuite.instruments import HP86120B
from testsuite.instruments import AQ6331
#from testsuite.instruments import gpib_ethernet_socket
from testsuite.instruments import gpib_visa_interface
from testsuite.instruments import MS9740
from testsuite.instruments import PM100USB
from testsuite.instruments import oscilloscopes
import traceback

fname = input('Enter the Device UID: ')
Build_string = 'TOSA'
# BUILD = int(input('Enter number for build status: 1=BAR, 2=DIE, 3=COC, 4=FOC, 5=TOSA, 6=SFP, 7=dummy_data :'))
# if BUILD == 1:
#     Build_string = 'BAR'
# elif BUILD == 2:
#     Build_string = 'DIE'
# elif BUILD == 3:
#     Build_string = 'COC'
# elif BUILD== 4:
#     Build_string = 'FOC'
# elif BUILD == 5:
#     Build_string = 'TOSA'
# elif BUILD== 6:
#     Build_string = 'SFP'
# elif BUILD== 7:
#     Build_string = 'DUMMY'

path_base = 'G:\\10G TOSA Product\\PIC Development\\PIC_Measurement_Data\\UID' + format(fname) + '\\DC_Raw_Data\\' + Build_string + '\\'

#gpib_ethernet_socket = gpib_ethernet_socket.GPIBEthernet("192.168.1.89", 1234)

#tec = LDT5910B.TEC(gpib_ethernet_socket, "5")
# dcrf = raw_input('dc or rf? : ')
dcrf = 'rf'

if (dcrf == 'dc'):
    test_station = test_stations.TestStationDC()
    osa = MS9740.OSA("192.168.1.121")
    wavemeter_interface = gpib_visa_interface.Interface(11)
else:
    test_station = test_stations.TestStationRF_TOSA()
    osa = MS9740.OSA("192.168.1.121")
    wavemeter_interface = gpib_visa_interface.Interface(11, gpib_board=1)
    
wavemeter = HP86120B.OSA(wavemeter_interface, "11")

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


try:
    
#     is_saved = int(raw_input('Mirror search saved? 1 = yes 0 = no :'))   
    is_saved = 0
    
    raw_input('Connect fiber to splitter to OSA and wavemeter')
    
    print("Mirror Search " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    mirror_sweep_filename = path_base + 'GV\\Mirror_Search_' + timestamp + '.csv'
    tosa_tests.mirror_search(path_b1 = path_base, 
                               test_station=test_station, 
                               saved_data = is_saved,
                               output_filename=mirror_sweep_filename, 
                               full_osa=osa, 
                               debug_data_filename=mirror_sweep_filename + "_debug.csv")
    
#     print("Verify Mirror Search " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
#     verify_mirror_search_filename = path_base + 'GV\\Verify_Mirror_Search_' + timestamp + '.csv'
#     tosa_tests.verify_mirror_sweep_table(input_filename=mirror_sweep_filename, 
#                               output_filename=verify_mirror_search_filename, 
#                               test_station=test_station, 
#                               full_osa=osa, 
#                               wavemeter=wavemeter)
    
    print("SOA Balancing " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    balance_SOAs_filename = path_base + 'GV\\ITU_SOA_Balanced' + timestamp + '.csv'
    tosa_tests.balance_SOAs(input_filename=mirror_sweep_filename, 
                 output_filename=balance_SOAs_filename, 
                 test_station=test_station)
    
    print("Verify ITU Table " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    verify_itu_table_filename = path_base + 'GV\\ITU_SOA_Balanced' + timestamp + '.csv'
    tosa_tests.verify_wavetable(input_filename=balance_SOAs_filename, 
                test_station=test_station, 
                full_osa=osa, 
                wavemeter=wavemeter, 
                output_filename=verify_itu_table_filename)
        
    raw_input('Switch to Integrating Sphere and press enter')
    
    print("1d Mod Phase Sweep " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    power_monitor = PM100USB.PowerMonitor()
    sweep_1d_phase_ITU_filename = path_base + 'GV\\ITU_Mod_phase' + timestamp + '.csv'
    tosa_tests.sweep_1d_phase_ITU(input_filename=balance_SOAs_filename, 
                       output_filename=sweep_1d_phase_ITU_filename, 
                       test_station=test_station, 
                       Phase1_current_start=0.0, 
                       Phase1_current_end=10.0,
                       Phase1_step=0.1, 
                       power_monitor=power_monitor, 
                       sweep_data_folder=path_base + 'GV\\ITU_Mod_phase_data_' + timestamp + '\\', 
                       sweep_img_folder=path_base + 'GV\\ITU_Mod_phase_data_' + timestamp + '\\')
                    
#     print("2d MZM Sweep " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
#     mzm_2d_path = path_base + 'GV\\MZM_2d_' + timestamp
#     tosa_tests.MZM_2d_ITU(input_filename=sweep_1d_phase_ITU_filename, 
#                output_data_path=mzm_2d_path, 
#                test_station=test_station, 
#                power_monitor=power_monitor, 
#                mzm_voltage_min=0.0, 
#                mzm_voltage_max=-6.0, 
#                mzm_voltage_step=-0.1)
    
    raw_input('Switch to Scope and press enter')
    
    print("Scope Parameters " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    scope_interface = gpib_visa_interface.Interface(10, gpib_board=1)
    scope = oscilloscopes.A86100D(scope_interface, 10)
    scope_filename = path_base + 'GV\\Scope_Parameters' + timestamp + '.csv'
    tosa_tests.measure_eye_parameters(input_filename=sweep_1d_phase_ITU_filename, 
                           output_filename=scope_filename, 
                           scope_img_path=path_base + 'GV\\EyeImages' + timestamp + '\\', #This one is a path to the SCOPE computer
                           scope=scope, 
                           test_station=test_station, 
                           mod_voltage=1.5, 
                           pause_current_set=True)

    print("Finish " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    
except:
    print("ERROR")
    traceback.print_exc()
finally:
    test_station.close()
    scope_interface.closesocket()
    wavemeter_interface.closesocket()