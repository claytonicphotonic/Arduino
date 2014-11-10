'''
Created on Mar 24, 2014

@author: bay
'''
import random

class TEC():
    setpoint_temp = 50
    
    def __init__(self, gpib_ethernet_socket, gpib_addr):
        pass
    
    def check_output_on(self):
        return True
    
    def check_temperature(self):
        return random.randrange(25,75)
    
    def check_setpoint_temperature(self):
        return self.setpoint_temp
    
    def write_setpoint_temperature(self, value):
        self.setpoint_temp = value
    
    def check_cutoff(self):
        return False
    
    def closesocket(self):
        pass