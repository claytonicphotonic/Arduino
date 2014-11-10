'''
Created on Mar 20, 2014

@author: bay
'''
from . import gpib_ethernet

UNSET_SOURCE = 0
CURRENT_SOURCE = 1
VOLTAGE_SOURCE = 2

class Keithley(gpib_ethernet.GPIBEthernet):
    
    def __init__(self, gpib_ethernet_socket, gpib_addr):
        self.source = UNSET_SOURCE
        gpib_ethernet.GPIBEthernet.__init__(self, gpib_ethernet_socket, gpib_addr)
        
    def set_output_on(self, state):
        if state:
            self.send(":OUTP:STAT ON")
        else:
            self.send(":OUTP:STAT OFF")
            
    def read_output_on(self):
        return(self.ask(":OUTP:STAT?")[0] == '1')
            
    def set_current_source(self, current):
        self.send(":SOUR:CURR:LEV:IMM:AMP " + format(current / 1000, '.1f'))
        self.source = CURRENT_SOURCE
    
    def read_current_source(self):
        return float(self.ask(":SOUR:CURR?")) * 1000
    
    def set_voltage_source(self, voltage):
        self.send(":SOUR:VOLT:LEV:IMM:AMP " + format(voltage, '.1f'))
        self.source = CURRENT_SOURCE
    
    def read_voltage_source(self):
        return float(self.ask(":SOUR:VOLT?"))
    
    def read_current(self):
        return float(self.ask(":MEAS:CURR?").split(',')[1]) * 1000
    
    def read_voltage(self):
        return float(self.ask(":MEAS:VOLT?").split(',')[0])