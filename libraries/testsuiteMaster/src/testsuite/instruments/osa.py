# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 15:28:38 2013

@author: bay

SO VERY, VERY DEPRECATED
"""
import serial


class OSA():
    def __init__(self, portname):
        self.serialport = serial.serial_for_url(portname, do_not_open=True)
        self.serialport.close()  # In case port is already open
        self.serialport.open()
        self.serialport.write("++addr 8\n".encode())
        self.successread = 0
        self.failread = 0
        
    def writesweepstart(self, wavelength):
        self.serialport.write(("STA " + format(int(wavelength)) + "\n").encode())
        
    def writesweepstop(self, wavelength):
        self.serialport.write(("STO " + format(int(wavelength)) + "\n").encode())
        
    def startsweep(self):
        self.serialport.write("SSI\n".encode())
        
    def checksweepfinished(self):
        self.serialport.flushInput()
        self.serialport.write("ESR2?\n".encode())  # Looks like 4 bytes returned
        bytearray = self.serialport.read(4)
        return (bytearray[0] & (2 ** 1)) > 0  # Bit 1 is check bt for sweep
        
    def startprimarypeaksearch(self):
        self.serialport.write("PKS PEAK\n".encode())
        
    def startsecondpeaksearch(self):  # Must be run after primary peak search
        self.serialport.write("PKS NEXT\n".encode())
        
    def checkpeakfinished(self):
        self.serialport.flushInput()
        self.serialport.write("ESR2?\n".encode())  # Looks like 4 bytes returned
        bytearray = self.serialport.read(4)
        return (bytearray[0] & (2 ** 0)) > 0  # Bit 0 is check bit for peak search
        
    def readpeak(self):
        self.serialport.flushInput()
        self.serialport.write("TMK?\n".encode())
        stringarray = self.serialport.read(22).decode("utf-8").split(",")  # Always 22 bits?
        output = {}
        output["wavelength"] = stringarray[0]
        output["power"] = stringarray[1][0:-3]
        return output
        
    def centeronpeak(self):
        self.serialport.write("PKC\n".encode())
        self.serialport.write("PKL\n".encode())
        
    def writevideobandwidth(self, freqstring):  # Should put a collection with acceptable values
        self.serialport.write(("VBW " + freqstring + "\n").encode())
        
    def writespan(self, span):  # Span amount in nm
        self.serialport.write(("SPN " + format(span) + "\n").encode())
        
    def writeresolution(self, resolution):  # Resolution in nm
        self.serialport.write(("RES " + resolution + "\n").encode())
