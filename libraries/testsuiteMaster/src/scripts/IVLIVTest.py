'''
Created on Jun 17, 2014

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
    
dcrf = raw_input('dc or rftosa or rfcoc? : ')
if (dcrf == 'dc'):
    test_station = test_stations.TestStationDC()
elif (dcrf == 'rfcoc'):
    test_station = test_stations.TestStationRF_COC()
else:
    test_station = test_stations.TestStationRF_TOSA()
    
path_base = 'G:\\10G TOSA Product\\PIC Development\\PIC_Measurement_Data\\UID' + format(fname) + '\\DC_Raw_Data\\' + Build_string + '\\'

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

print(path_base + 'GV\\Gain_Voltage_Map_Data' + timestamp)

try:
    print("IV Tests" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    iv_path = path_base + 'IV\\'
    tosa_tests.IV_all_sections(output_folder=iv_path, 
                               test_station=test_station, 
                               filename_suffix=timestamp)
    
    print("LIV IS" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    power_monitor = PM100USB.PowerMonitor()
    liv_is_filename_base = path_base + 'LIV\\liv_is' + timestamp
    tosa_tests.LIV_IS(output_filename=liv_is_filename_base + '.csv', 
                      test_station=test_station, 
                      power_monitor=power_monitor, 
                      output_img_filename=liv_is_filename_base + '.png')
    
    print("LIV SOA" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    liv_soa_filename_base = path_base + 'LIV\\liv_soa' + timestamp
    tosa_tests.LIV_SOA(output_filename=liv_soa_filename_base + '.csv', 
                      test_station=test_station, 
                      output_img_filename=liv_soa_filename_base + '.png')
except:
    print("ERROR")
    traceback.print_exc()
finally:
    test_station.close()
    power_monitor.close()