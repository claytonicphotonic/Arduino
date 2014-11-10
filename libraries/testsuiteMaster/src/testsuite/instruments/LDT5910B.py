'''
Created on Feb 14, 2014

@author: bay
'''
from . import gpib_ethernet

class TEC(gpib_ethernet.GPIBEthernet):
    shutoff_temperature_delta = 5
    
    def check_output_on(self):
        return(self.ask(":OUTPut?")[0] == '1')
    
    def check_temperature(self):
        return(float(self.ask(":T?")))
    
    def check_setpoint_temperature(self):
        return(float(self.ask(":SET:T?")))
    
    def write_setpoint_temperature(self, value):
        self.send(":T " + format(value, '.2f'))
    
    def check_cutoff(self):
        """Return True if temperature runoff is detected, IMMEDIATELY shut off laser"""
        if not self.check_output_on():
            return True
        elif abs(self.check_temperature() - self.check_setpoint_temperature()) > self.shutoff_temperature_delta:
            return True
        else:
            return False