'''
Created on May 29, 2014

@author: bay
'''

import sys, os
from datetime import datetime
import numpy as np

sys.path.insert(0, os.path.abspath('../'))

from testsuite.tests import tosa_tests
#from testsuite.instruments import laser_sections_TOSA_keithleys
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
elif BUILD == 4:
    Build_string = 'FOC'
elif BUILD == 5:
    Build_string = 'TOSA'
elif BUILD == 6:
    Build_string = 'SFP'
elif BUILD == 7:
    Build_string = 'DUMMY'
    
path_base = 'G:\\10G TOSA Product\\PIC Development\\PIC_Measurement_Data\\UID' + format(fname) + '\\DC_Raw_Data\\' + Build_string + '\\'

wavemeter_interface = gpib_visa_interface.Interface(11)

# Comment out instrument lines you do not need as well as their close commands
#tec = LDT5910B.TEC(gpib_ethernet_socket, "5")
wavemeter = HP86120B.OSA(wavemeter_interface, "11")
osa = MS9740.OSA("192.168.1.121")
test_station = test_stations.TestStationDC()
power_monitor = PM100USB.PowerMonitor()

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

try:
    sample_filename = path_base + 'GV\\SampleFilename' + timestamp + '.csv'
                         
    print("Finish " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
except:
    print("ERROR")
    traceback.print_exc()
finally:
    test_station.close()
    wavemeter_interface.closesocket()
    osa.close()
    power_monitor.close()