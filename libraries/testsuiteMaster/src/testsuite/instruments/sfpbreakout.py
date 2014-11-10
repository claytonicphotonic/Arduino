# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 11:44:33 2013

@author: bay
"""

import serial


class SFP():
    SERIAL_BAUD = 230400
    
    def __init__(self, portname):
        self.serialport = serial.serial_for_url(portname, do_not_open=True)
        self.serialport.close()  # In case port is already open
        self.serialport.baudrate = self.SERIAL_BAUD
        self.serialport.timeout = .5
        self.serialport.open()
        self.successread = 0
        self.failread = 0
        
    def close(self):
        self.serialport.close()
        
    def printdebug(self):
        print('Successful reads: ' + format(self.successread))
        print('Failed read: ' + format(self.failread))
        
    def readregistermulti(self, register, length):
        if register > 1023:
            raise self.SerialPortError
        elif register >= 768:
            device_addr = 'A6'
        elif register >= 512:
            device_addr = 'A4'
        elif register >= 256:
            device_addr = 'A2'
        elif register >= 0:
            device_addr = 'A0'
        else:
            raise self.SerialPortError("Register not in valid range")

        register = register % 256
            
        self.serialport.flushInput()
        
        self.serialport.write(('twifdmp 0x' + device_addr + ' ' + format(register) + ' ' + format(length - 1) + '\n').encode())
        
        read_size = length * 11 + 24
        
        buffer = self.serialport.read(read_size)
        outputarray = buffer.split(b'\r\n')[1:-2]
        result = []
        somethingread = 0
        for bytestring in outputarray:
            result.append(int((bytestring.split(b' '))[1], 0))
            somethingread += 1
            
        self.successread += 1
        return result
        
    def readregister(self, register):
        return self.readregistermulti(register, 1)[0]
        
    def writeregister(self, register, value):
        if register > 1023:
            raise self.SerialPortError
        elif register >= 768:
            device_addr = 'A6'
        elif register >= 512:
            device_addr = 'A4'
        elif register >= 256:
            device_addr = 'A2'
        elif register >= 0:
            device_addr = 'A0'
        else:
            raise self.SerialPortError("Register not in valid range")
        register = register % 256
        writestring = 'twifwr 0x' + device_addr + ' ' + format(register) + ' ' + format(value)
        #print (writestring)
        self.serialport.flushInput()
        self.serialport.write((writestring + '\n').encode())
        self.serialport.read(len(writestring) + 7)
        
    def writeregistermulti(self, register, values):
        length = len(values)
        for index in range(length):
            self.writeregister(register + index, values[index])
            
    def verify_connection(self):
        checkstring = 'Packet Photonics'
        readstring = self.readregistermulti(20, 16)
        for i in range(16):
            if chr(readstring[i]) != checkstring[i]:
                return False
        return True
            
    class SerialPortError(Exception):  # Just so we can handle this specific exception
        pass
