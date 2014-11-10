# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 17:31:28 2013

@author: bay
"""
import serial


class DebugBox():
    SERIAL_BAUD = 115200
    SERIAL_TIMEOUT = .500
    COMMAND_READ = 144
    COMMAND_WRITE = 160
    
    def __init__(self, portname):
        self.serialport = serial.serial_for_url(portname, do_not_open=True)
        self.serialport.close()  # In case port is already open
        self.serialport.baudrate = self.SERIAL_BAUD
        self.serialport.timeout = self.SERIAL_TIMEOUT
        self.serialport.writeTimeout = self.SERIAL_TIMEOUT
        self.serialport.open()
        self.successread = 0
        self.failread = 0
        
    def close(self):
        self.serialport.close()
        
    def printdebug(self):
        print('Successful reads: ' + format(self.successread))
        print('Failed read: ' + format(self.failread))
        
    def readregister(self, register):
        writevalue = bytearray()
        writevalue.append(self.COMMAND_READ)
        writevalue.append((register >> 8) & 255)
        writevalue.append(register & 255)
        
        for i in range(100000):  # TODO Get Henrik to fix this in FPGA code
            self.successfulread = False
            self.serialport.flushInput()
            
            self.serialport.write(writevalue)
            
            readvalue = self.serialport.read(4)
            
            if len(readvalue) != (4):
                self.failread += 1
                continue
            
            if writevalue[0:3] != readvalue[0:3]:
                self.failread += 1
                continue
            
            self.successfulread = True
            break
        
        if not(self.successfulread):
            raise IOError("Serial port read failure")
            
        self.successread += 1
        
        return readvalue[3]
        
    def writeregister(self, register, value):
        writevalue = bytearray()
        writevalue.append(self.COMMAND_WRITE)
        writevalue.append((register >> 8) & 255)
        writevalue.append(register & 255)
        writevalue.append(value)
            
        self.serialport.flushInput()
        
        self.serialport.write(writevalue)
        
    def readregistermulti(self, register, length):
        readvalue = []
        for i in range(length):
            readvalue.append(self.readregister(register + i))
            
        return readvalue
    
    def writeregistermulti(self, register, values):
        length = len(values)
        for i in range(length):
            self.writeregister(register + i, values[i])
        
    def verify_connection(self):
        checkstring = 'Packet Photonics'
        readstring = self.readregistermulti(20, 16)
        for i in range(16):
            if chr(readstring[i]) != checkstring[i]:
                return False
        return True
        
    class SerialPortError(Exception):  # Just so we can handle this specific exception
        pass
