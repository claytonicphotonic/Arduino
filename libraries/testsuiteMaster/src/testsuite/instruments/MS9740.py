'''
Created on Mar 26, 2014

@author: bay
'''

import visa
from time import sleep
import numpy

class OSA():
    def __init__(self, ip_addr):
        conn_str = "TCPIP0::" + ip_addr + "::INSTR"
        self.instrument = visa.instrument(conn_str)
     
    def identity(self):
        return 'MS9740'
     
    def set_video_bandwidth(self, vbw):
        if vbw >= 1000000:
            self.instrument.write( 'VBW '+ str(vbw/1000000) + 'MHZ\n' )
        elif vbw >= 1000:
            self.instrument.write( 'VBW '+ str(vbw/1000) + 'KHZ\n' )
        else:
            self.instrument.write( 'VBW '+ str(vbw) + 'HZ\n' )
        
    def read_video_bandwidth(self):
        vbw_string = self.instrument.ask('VBW?\n')
        if vbw_string.endswith("MHZ"):
            return float(vbw_string[:-3]) * 1e6
        elif vbw_string.endswith("KHZ"):
            return float(vbw_string[:-3]) * 1e3
        elif vbw_string.endswith("HZ"):
            return float(vbw_string[:-2])
        else:
            raise IOError
        
    def sweep_stop(self):
        self.instrument.write('SST\n')
    
    def sweep_single(self):
        self.instrument.write('SSI\n')
    
    def sweep_continuous(self):
        self.instrument.write('SRT\n')
        
    def wait_for_sweepcomplete(self, callback=None):
        sweep_complete = False
        while sweep_complete == False:
            answer_string = str(self.instrument.ask('ESR2?\n'))
            if answer_string[:1] != '0':
                sweep_complete = True
            sleep(0.01)
            if callback is not None:
                callback()
        
    def set_start_wavelength(self, wavelength):
        self.instrument.write('STA ' + str(wavelength) + '\n')  # SET START WAVELENGTH
        
    def read_start_wavelength(self):
        start_wl = self.instrument.ask('STA?\n')  # READ START WAVELENGTH
        return float(start_wl)
            
    def set_stop_wavelength(self, wavelength):
        self.instrument.write('STO ' + str(wavelength) + '\n')  # SET STOP WAVELENGTH
        
    def read_stop_wavelength(self):
        stop_wl = self.instrument.ask('STO?\n')  # READ STOP WAVELENGTH
        return float(stop_wl)
        
    def set_center_wavelength(self, wavelength):
        self.instrument.write('CNT ' + str(wavelength) + '\n')  # SET CENTER WAVELENGTH
        
    def read_center_wavelength(self):
        center_wl = self.instrument.ask('CNT?\n')  # READ CENTER WAVELENGTH
        return (center_wl)
        
    def set_span(self, wavelength):
        self.instrument.write('SPN ' + str(wavelength) + '\n')  # SET SPAN
        
    def read_span(self):
        span = self.instrument.ask('SPN?\n')  # READ SPAN
        return float(span)
        
    def set_sampling_points(self, num_points):
        self.instrument.write('MPT ' + str(num_points) + '\n')  # SET SAMPLING POINTS
        
    def read_sampling_points(self):
        smppts = self.instrument.ask('MPT?\n')  # READ SAMPLING POINTS
        return float(smppts)
        
    def set_resolution(self, resolution):
        self.instrument.write('RES ' + str(resolution) + '\n')  # SET RESOLUTION
        
    def read_resolution(self):
        res = self.instrument.ask('RES?\n')  # READ RESOLUTION
        return float(res)
        
    def read_trace_memory(self):
        self.wait_for_sweepcomplete()
        start_wl = float(self.read_start_wavelength())   # reads start wavelength from OSA
        sleep(0.005)
        stop_wl = float(self.read_stop_wavelength())    # reads stop wavelength from OSA
        sleep(0.005)
        sp_pts = float(self.read_sampling_points())    # reads sampling points from OSA
        sleep(0.005)
        pow_data_str = self.instrument.ask('DMA?')     # reads trace data from OSA
        wav_data = numpy.linspace( start_wl, stop_wl, sp_pts)
        data = []
        counter = 0
        for pow_val in pow_data_str.split( "\n" ):     # convert string data from OSA to numeric array
            data.append([wav_data[counter], float( pow_val )])
            counter += 1
        return data
    
    def read_trace_memory_A(self):
        #DEPRECATED
        return self.read_trace_memory()
    
    def search_peak(self):
        peak_string = self.instrument.ask('SSI; *WAI ; PKS PEAK; TMK?\n')  #starts single sweep, searches for peak, and returns peak
        try:
            peak = float(peak_string.split(',')[0])
            peak_power = float(peak_string.split(',')[1][:-3])
        except: 
            print("ERROR: peak not found")
            print(peak_string.split(',')[1][:])
            peak = -1
            peak_power = -70        
        return(peak,peak_power)
    
    def read_smsr(self):
        self.instrument.write('ANA SMSR,2NDPEAK\n')
        data = self.instrument.ask('ANAR?').split(',')
        return float(data[1])
    
    def readpeak(self):
        self.sweep_single()
        self.wait_for_sweepcomplete()
    
        output = []
        self.instrument.write('PKS PEAK')
        peak_string = self.instrument.ask('TMK?')
        peak = {}
        try: 
            peak["power"] = float(peak_string.split(',')[1][:-3])
            peak["wavelength"] = float(peak_string.split(',')[0])
        except: 
            print("ERROR: peak not found")
            print(peak_string.split(',')[1][:])
            print(peak_string.split(',')[0])
            peak["power"] = -1
            peak["wavelength"] = -1
        output.append(peak)
        self.instrument.write('PKS NEXT')
        peak_string = self.instrument.ask('TMK?')
        peak = {}
        try: 
            peak["power"] = float(peak_string.split(',')[1][:-3])
            peak["wavelength"] = float(peak_string.split(',')[0])
        except: 
            print("ERROR: peak not found")
            peak["power"] = -1
            peak["wavelength"] = -1
        output.append(peak)
        
        return output
    
    def close(self):
        self.instrument.close()