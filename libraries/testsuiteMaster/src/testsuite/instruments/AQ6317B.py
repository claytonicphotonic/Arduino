# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 15:28:38 2013

@author: bay
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
        self.serialport.write(("START WL" + format(wavelength, '07.2f') + "nm\n").encode())
        
    def writesweepstop(self, wavelength):
        self.serialport.write(("STOP WL" + format(wavelength, '07.2f') + "nm\n").encode())
        
    def writespan(self, wavelength):
        self.serialport.write(("SPAN" + format(wavelength, '06.1f') + "nm\n").encode())
        
    def writecenter(self, wavelength):
        self.serialport.write(("CENTER" + format(wavelength, '07.2f') + "nm\n").encode())
        
    def startsweep(self):
        self.serialport.write("SGL\n".encode())
        
    def checksweepfinished(self):  # TODO Don't think this is working, use SRQ?
        self.serialport.flushInput()
        self.serialport.write("SWEEP?\n".encode())
        bytearray = self.serialport.read(1)  # Maybe
        return (bytearray[0] == 0)
        
    def startprimarypeaksearch(self):
        self.serialport.write("PKSR\n".encode())
        
    def startsecondpeaksearch(self):  # Must be run after primary peak search
        self.serialport.write("NSR\n".encode())
        
#    def checkpeakfinished(self):
#        self.serialport.flushInput()
#        self.serialport.write("ESR2?\n".encode()) #Looks like 4 bytes returned
#        bytearray = self.serialport.read(4)
#        return (bytearray[0] & 2**0)>0 #Bit 0 is check bit for peak search
        
    def readpeak(self):  # TODO Convert to new codes for new OSA, MKR?
        self.serialport.flushInput()
        self.serialport.write("TMK?\n".encode())
        stringarray = self.serialport.read(22).decode("utf-8").split(",")  # Always 22 bits?
        output = {}
        output["wavelength"] = stringarray[0]
        output["power"] = stringarray[1][0:-3]
        return output
        
    def centeronpeak(self):
        self.serialport.write("CTR=P\n".encode())
        
#    def writevideobandwidth(self, freqstring): #should put a collection with acceptable values
#        self.serialport.write(("VBW " + freqstring + "\n").encode())
        
    def writeresolution(self, resolution):  # resolution in nm
        self.serialport.write(("RESOLN" + format(resolution, '04.2f') + "nm\n").encode())
