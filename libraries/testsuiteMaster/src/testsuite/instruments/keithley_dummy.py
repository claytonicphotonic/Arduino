'''
Created on Mar 25, 2014

@author: bay
'''

from testsuite.instruments import gpib_ethernet_dummy
import random

class Keithley(gpib_ethernet_dummy.GPIBEthernet):
    
    def __init__(self, gpib_ethernet_socket, gpib_addr):
        pass
        
    def set_output_on(self, state):
        pass
            
    def read_output_on(self):
        return True
            
    def set_current_source(self, current):
        pass
    
    def read_current_source(self):
        return random.randrange(20, 50)
    
    def set_voltage_source(self, voltage):
        pass
    
    def read_voltage_source(self):
        return random.randrange(0, 5)
    
    def read_current(self):
        return random.randrange(20, 50)
    
    def read_voltage(self):
        return random.randrange(0, 5)