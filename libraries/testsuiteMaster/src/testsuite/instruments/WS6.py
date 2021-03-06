'''
Created on Mar 26, 2014

@author: bay
'''

import visa
from time import sleep
import numpy
import ctypes

class OSA():
    def __init__(self):
        self.hifinesse = ctypes.cdll.LoadLibrary("C:\\Windows\\System32\\wlmData.dll")
        proto = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long)
        func = proto(("ControlWLM",self.hifinesse))
        error_code = func(ctypes.c_long(1),ctypes.c_long(0),ctypes.c_long(0))
        
        proto = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_bool)
        func = proto(("SetExposureMode",self.hifinesse))
        error_code = func(ctypes.c_bool(1))
#        conn_str = "TCPIP0::" + ip_addr + "::INSTR"
#        self.instrument = visa.instrument(conn_str)
    
    def identity(self):
        return ('WS6')        
        
    def set_video_bandwidth(self, vbw):
        pass
#        if vbw >= 1000000:
#            self.instrument.write( 'VBW '+ str(vbw/1000000) + 'MHZ\n' )
#        elif vbw >= 1000:
#            self.instrument.write( 'VBW '+ str(vbw/1000) + 'KHZ\n' )
#        else:
#            self.instrument.write( 'VBW '+ str(vbw) + 'HZ\n' )
        
    def read_video_bandwidth(self):
        pass
#        vbw_string = self.instrument.ask('VBW?\n')
#        if vbw_string.endswith("MHZ"):
#            return float(vbw_string[:-3]) * 1e6
#        elif vbw_string.endswith("KHZ"):
#            return float(vbw_string[:-3]) * 1e3
#        elif vbw_string.endswith("HZ"):
#            return float(vbw_string[:-2])
#        else:
#            raise IOError
        
    def sweep_stop(self):
        pass
#        self.instrument.write('SST\n')
    
    def sweep_single(self):
        pass
#        self.instrument.write('SSI\n')
    
    def sweep_continuous(self):
        pass
#        self.instrument.write('SRT\n')
        
    def wait_for_sweepcomplete(self, callback=None):
        pass
#        sweep_complete = False
#        while sweep_complete == False:
#            answer_string = str(self.instrument.ask('ESR2?\n'))
#            if answer_string[:1] != '0':
#                sweep_complete = True
#            sleep(0.01)
#            if callback is not None:
#                callback()
        
    def set_start_wavelength(self, wavelength):
        pass
#        self.instrument.write('STA ' + str(wavelength) + '\n')  # SET START WAVELENGTH
        
    def read_start_wavelength(self):
        pass
#        start_wl = self.instrument.ask('STA?\n')  # READ START WAVELENGTH
#        return float(start_wl)
            
    def set_stop_wavelength(self, wavelength):
        pass
#        self.instrument.write('STO ' + str(wavelength) + '\n')  # SET STOP WAVELENGTH
        
    def read_stop_wavelength(self):
        pass
#        stop_wl = self.instrument.ask('STO?\n')  # READ STOP WAVELENGTH
#        return float(stop_wl)
        
    def set_center_wavelength(self, wavelength):
        pass
#        self.instrument.write('CNT ' + str(wavelength) + '\n')  # SET CENTER WAVELENGTH
        
    def read_center_wavelength(self):
        pass
#        center_wl = self.instrument.ask('CNT?\n')  # READ CENTER WAVELENGTH
#        return (center_wl)
        
    def set_span(self, wavelength):
        pass
#        self.instrument.write('SPN ' + str(wavelength) + '\n')  # SET SPAN
        
    def read_span(self):
        pass
#        span = self.instrument.ask('SPN?\n')  # READ SPAN
#        return float(span)
        
    def set_sampling_points(self, num_points):
        pass
#        self.instrument.write('MPT ' + str(num_points) + '\n')  # SET SAMPLING POINTS
        
    def read_sampling_points(self):
        pass
#        smppts = self.instrument.ask('MPT?\n')  # READ SAMPLING POINTS
#        return float(smppts)
        
    def set_resolution(self, resolution):
        pass
#        self.instrument.write('RES ' + str(resolution) + '\n')  # SET RESOLUTION
        
    def read_resolution(self):
        pass
#        res = self.instrument.ask('RES?\n')  # READ RESOLUTION
#        return float(res)
        
    def read_trace_memory(self):
        pass
#        self.wait_for_sweepcomplete()
#        start_wl = float(self.read_start_wavelength())   # reads start wavelength from OSA
#        sleep(0.005)
#        stop_wl = float(self.read_stop_wavelength())    # reads stop wavelength from OSA
#        sleep(0.005)
#        sp_pts = float(self.read_sampling_points())    # reads sampling points from OSA
#        sleep(0.005)
#        pow_data_str = self.instrument.ask('DMA?')     # reads trace data from OSA
#        wav_data = numpy.linspace( start_wl, stop_wl, sp_pts)
#        data = []
#        counter = 0
#        for pow_val in pow_data_str.split( "\n" ):     # convert string data from OSA to numeric array
#            data.append([wav_data[counter], float( pow_val )])
#            counter += 1
#        return data
    
    def read_trace_memory_A(self):
        pass
        #DEPRECATED
#        return self.read_trace_memory()
    
    def search_peak(self):
        #sleep(0.3)
        proto = ctypes.WINFUNCTYPE(ctypes.c_double, ctypes.c_double)
        func = proto(("GetWavelength",self.hifinesse))
        peak = func(ctypes.c_double(0))
        peak2 = func(ctypes.c_double(0))
        if abs(peak-peak2)>0.01: peak = -1
        
        proto = ctypes.WINFUNCTYPE(ctypes.c_ushort, ctypes.c_ushort)
        func = proto(("GetExposure", self.hifinesse))
        exposure = func(ctypes.c_ushort(0))
#        print("exposure = " + str(exposure))        
        
        proto = ctypes.WINFUNCTYPE(ctypes.c_double, ctypes.c_long,  ctypes.c_double)
        func = proto(("GetPowerNum", self.hifinesse))
        power = func(ctypes.c_long(1), ctypes.c_double(0))
        
        return(peak, power)
#        peak_string = self.instrument.ask('SSI; *WAI ; PKS PEAK; TMK?\n')  #starts single sweep, searches for peak, and returns peak
#        try:
#            peak = float(peak_string.split(',')[0])
#            peak_power = float(peak_string.split(',')[1][:-3])
#        except: 
#            print("ERROR: peak not found")
#            print(peak_string.split(',')[1][:])
#            peak = -1
#            peak_power = -70        
#        return(peak,peak_power)
    
    def read_smsr(self):
        pass
#        self.instrument.write('ANA SMSR,2NDPEAK\n')
#        data = self.instrument.ask('ANAR?').split(',')
#        return float(data[1])
    
    def readpeak(self):
        pass
#        self.sweep_single()
#        self.wait_for_sweepcomplete()
#    
#        output = []
#        self.instrument.write('PKS PEAK')
#        peak_string = self.instrument.ask('TMK?')
#        peak = {}
#        try: 
#            peak["power"] = float(peak_string.split(',')[1][:-3])
#            peak["wavelength"] = float(peak_string.split(',')[0])
#        except: 
#            print("ERROR: peak not found")
#            print(peak_string.split(',')[1][:])
#            print(peak_string.split(',')[0])
#            peak["power"] = -1
#            peak["wavelength"] = -1
#        output.append(peak)
#        self.instrument.write('PKS NEXT')
#        peak_string = self.instrument.ask('TMK?')
#        peak = {}
#        try: 
#            peak["power"] = float(peak_string.split(',')[1][:-3])
#            peak["wavelength"] = float(peak_string.split(',')[0])
#        except: 
#            print("ERROR: peak not found")
#            peak["power"] = -1
#            peak["wavelength"] = -1
#        output.append(peak)
#        
#        return output
    
    def close(self):
        pass
#        self.instrument.close()