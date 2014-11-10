# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 13:28:28 2013

@author: bay
"""

import random


class DummyBox():
    def __init__(self, portname):
        self.successread = 0
        self.failread = 0
        
    def close(self):
        pass
        
    def printdebug(self):
        print('Successful reads: ' + format(self.successread))
        print('Failed read: ' + format(self.failread))
        
    def readregister(self, register):
        self.successread += 1
        if register == 0:
            return 3 # SFP Identifier
        elif 20 <= register <= 35:
            return ord("B") # Vendor Name
        elif 40 <= register <= 55:
            return ord("C") # Vendor PN
        elif 56 <= register <= 59:
            return ord("D") # Vendor Rev
        elif register == 602: # Laser Temp MSB
            return 1
        elif register == 604: # Etalon Temp MSB
            return 1
        elif 640 <= register <= 655: # Averaging values
            return 16
#         elif register == 585: # Laser Tec Alarm
#             return 1
        return random.randint(0, 255)
        
    def writeregister(self, register, value):
        pass
        
    def readregistermulti(self, register, length):
        readvalue = []
        for i in range(length):
            readvalue.append(self.readregister(register + i))
            
        self.successread += 1
        return readvalue
    
    def writeregistermulti(self, register, values):
        pass
        
    def verify_connection(self):
        return True
        
    class SerialPortError(Exception):  # Just so we can handle this specific exception
        pass
