'''
Created on May 7, 2014

@author: bay
'''

import serial
import time

class Interface():
    SERIAL_BAUD = 115200
    SERIAL_TIMEOUT = .500
    
    def __init__(self, portname):
        self.serialport = serial.serial_for_url(portname, do_not_open=True)
        self.serialport.close()  # In case port is already open
        self.serialport.baudrate = self.SERIAL_BAUD
        self.serialport.timeout = self.SERIAL_TIMEOUT
        self.serialport.writeTimeout = self.SERIAL_TIMEOUT
        self.serialport.open()
        
    def read(self, gpib_addr):
        return(self.serialport.readline()) #This does not set the gpib address again!
        
    def send(self, string, gpib_addr):
        self.serialport.write(("++addr " + format(gpib_addr) + "\n").encode())
        self.serialport.write((string + "\n").encode())
        
    def ask(self, string, gpib_addr, delay=None):
        self.send(string, gpib_addr)
        if delay is not None:
            time.sleep(delay)
        return(self.read(gpib_addr))
    
    def closesocket(self):
        self.serialport.close()