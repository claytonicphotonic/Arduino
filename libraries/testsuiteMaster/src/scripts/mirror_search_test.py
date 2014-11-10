'''
Created on Apr 25, 2014

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
from testsuite.instruments import WS6
from testsuite.instruments import PM100USB
from testsuite.instruments import oscilloscopes
import traceback

fname = input('Enter the Device UID: ')
BUILD = int(input('Enter number for build status: 1=BAR, 2=DIE, 3=COC, 4=FOC, 5=TOSA, 6=SFP, 7=dummy_data :'))
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

#fname = 747
#BUILD = 5
#Build_string = 'TOSA'

path_base = 'G:\\10G TOSA Product\\PIC Development\\PIC_Measurement_Data\\UID' + format(fname) + '\\DC_Raw_Data\\' + Build_string + '\\'

#gpib_ethernet_socket = gpib_ethernet_socket.GPIBEthernet("192.168.1.89", 1234)

#tec = LDT5910B.TEC(gpib_ethernet_socket, "5")


#dcrf = 'dc'
osa_or_wm = 'nothing yet' #declaration
dcrf = 'nothing yet' #declaration
while (osa_or_wm != 'osa' and osa_or_wm != 'wm'):
    osa_or_wm = raw_input('osa or wm? :')
    if (osa_or_wm == 'osa'):
        osa = MS9740.OSA("192.168.1.121")
        #osa = AQ6331.OSA("192.168.1.33", 1234, "5")  
    elif (osa_or_wm == 'wm'):
        osa = WS6.OSA()
    else:
        print('You didn\'t enter osa or wm')

while (dcrf != 'dc' and dcrf != 'rf'):
    dcrf = raw_input('dc or rf? : ')
    if (dcrf == 'dc'):
        test_station = test_stations.TestStationDC()
    elif (dcrf == 'rf'):
        test_station = test_stations.TestStationRF_TOSA()
        #laser_sections = laser_sections_ni_box.LaserSections(nplc=0.4)
    else:
        print('You didn\'t enter dc or rf')

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

continue_measurements = 0

try:
    # OSA only should be connected at start
    
    is_saved = int(raw_input('Mirror search saved? 1 = yes 0 = no :'))   
    
    raw_input('Connect fiber to OSA')    
    
    print("Mirror Search " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    mirror_sweep_filename = path_base + 'GV\\Mirror_Search_' + timestamp + '.csv'
    continue_measurements = tosa_tests.mirror_search(path_b1 = path_base, 
                               test_station=test_station, 
                               saved_data = is_saved,
                               output_filename=mirror_sweep_filename, 
                               full_osa=osa, 
                               debug_data_filename=mirror_sweep_filename + "_debug.csv")
    
    continue_measurements = raw_input('continue measurements now? (1=yes  0=no) :') 
    if (continue_measurements == '1') :
        raw_input('Switch to Integrating Sphere and press enter')
        print("SOA Balancing " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        balance_SOAs_filename = path_base + 'GV\\ITU_SOA_Balanced' + timestamp + '.csv'
        tosa_tests.balance_SOAs(input_filename=mirror_sweep_filename, 
                     output_filename=balance_SOAs_filename, 
                     test_station=test_station)
        
    
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
                        
        print("2d MZM Sweep " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        mzm_2d_path = path_base + 'GV\\MZM_2d_' + timestamp
        tosa_tests.MZM_2d_ITU(input_filename=sweep_1d_phase_ITU_filename, 
                   output_data_path=mzm_2d_path, 
                   test_station=test_station, 
                   power_monitor=power_monitor, 
                   mzm_voltage_min=0.0, 
                   mzm_voltage_max=-6.0, 
                   mzm_voltage_step=-0.1)
        
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
                               mod_voltage=1.5)
        scope_interface.closesocket()
    print("Finish " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    
except:
    print("ERROR")
    traceback.print_exc()
finally:
    test_station.close()
    
