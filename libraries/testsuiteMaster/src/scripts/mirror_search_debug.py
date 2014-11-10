'''
Created on Jun 20, 2014

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

#fname = 378
#BUILD = 5
#Build_string = 'TOSA'

path_base = 'G:\\10G TOSA Product\\PIC Development\\PIC_Measurement_Data\\UID' + format(fname) + '\\DC_Raw_Data\\' + Build_string + '\\'

#gpib_ethernet_socket = gpib_ethernet_socket.GPIBEthernet("192.168.1.89", 1234)

#tec = LDT5910B.TEC(gpib_ethernet_socket, "5")
dcrf = raw_input('dc or rf? : ')
#dcrf = 'dc'

if (dcrf == 'dc'):
    test_station = test_stations.TestStationDC()
    #laser_sections = laser_sections_TOSA_keithleys.LaserSections(nplc=0.4)
    osa = MS9740.OSA("192.168.1.121")
else:
    test_station = test_stations.TestStationRF_TOSA()
    #laser_sections = laser_sections_ni_box.LaserSections(nplc=0.4)
    osa = MS9740.OSA("192.168.1.121")
    #osa = AQ6331.OSA("192.168.1.33", 1234, "5")    

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


try:
    # OSA only should be connected at start
    
    is_saved = int(raw_input('Mirror search saved? 1 = yes 0 = no :'))   
    
    raw_input('Connect fiber to OSA')    
    
    print("Mirror Search " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    mirror_sweep_filename = path_base + 'GV\\Mirror_Search_' + timestamp + '.csv'
    tosa_tests.mirror_search(path_b1 = path_base, 
                               test_station=test_station, 
                               saved_data = is_saved,
                               output_filename=mirror_sweep_filename, 
                               full_osa=osa, 
                               debug_data_filename=mirror_sweep_filename + "_debug.csv")
    
    print("Mirror Search Debug" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    mirror_sweep_debug_filename = path_base + 'GV\\Mirror_Search_Debug_' + timestamp + '.csv'
    tosa_tests.mirror_search_debug(test_station=test_station, 
                        input_filename=mirror_sweep_filename, 
                        output_filename=mirror_sweep_debug_filename, 
                        osa=osa)

    print("Finish " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    
except:
    print("ERROR")
    traceback.print_exc()
finally:
    test_station.close()
