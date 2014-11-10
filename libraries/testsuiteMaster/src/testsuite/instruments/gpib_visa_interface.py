'''
Created on Apr 14, 2014

@author: bay
'''
import time
import socket
import visa

class Interface():
    def __init__(self, gpib_address, gpib_board=0, timeout=None, command_delay=None):
        self.visa_instrument = visa.GpibInstrument(int(gpib_address), int(gpib_board))
        if timeout is not None:
            self.visa_instrument.timeout = timeout
        if command_delay is not None:
            self.visa_instrument.delay = command_delay
        
    def read(self, gpib_addr=None):
        return(self.visa_instrument.read())
        
    def send(self, string, gpib_addr=None):
        self.visa_instrument.write(string)
        
    def ask(self, string, gpib_addr=None, delay=None):
        if delay is not None:
            visa_delay = self.visa_instrument.delay
            self.visa_instrument.delay = delay
        output = self.visa_instrument.ask(string)
        if delay is not None:
            self.visa_instrument.delay = visa_delay
        return(output)
    
    def closesocket(self):
        self.visa_instrument.close()