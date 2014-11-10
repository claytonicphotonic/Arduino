'''
Created on Jan 22, 2014

@author: bay
'''

from time import sleep, time
from . import gpib_ethernet


class OSA(gpib_ethernet.GPIBEthernet):
    def writesweepstart(self, wavelength):
        pass #Ignored
        
    def writesweepstop(self, wavelength):
        pass #Ignored
        
    def startsweep(self):
        pass
        
    def checksweepfinished(self):
        return True
        
    def readpeak(self, delay = 0.5):
        self.send("init:cont off")
        self.send("init:imm")
        sleep(1.1)
        power_array = self.ask("fetc:arr:pow?", delay=delay).split(',')
        wavelength_array = self.ask("fetc:arr:pow:wav?").split(',')

        output = []
        
        for i in range(int(wavelength_array[0])):
            peak = {}
            peak["wavelength"] = float(wavelength_array[i + 1]) * 10**9
            peak["power"] = float(power_array[i + 1])
            output.append(peak)
        
        return output
        
    def centeronpeak(self):
        pass
        
    def writeresolution(self, resolution):  # resolution in nm
        pass