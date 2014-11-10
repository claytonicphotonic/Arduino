'''
Created on Nov 17, 2013

@author: bay
'''
from socket import socket, AF_INET, SOCK_STREAM, IPPROTO_TCP, timeout
from time import sleep
from . import gpib_ethernet


class OSA(gpib_ethernet.GPIBEthernet):
        
    def writesweepstart(self, wavelength):
        self.sock.send(("STAWL" + format(wavelength, '07.2f') + "\n").encode())
        
    def writesweepstop(self, wavelength):
        self.sock.send(("STPWL" + format(wavelength, '07.2f') + "\n").encode())
        
    def writespan(self, wavelength):
        self.sock.send(("SPAN" + format(wavelength, '06.1f') + "\n").encode())
        
    def writecenter(self, wavelength):
        self.sock.send(("CTRWL" + format(wavelength, '07.2f') + "\n").encode())
        
    def startsweep(self):
        self.sock.send("SGL\n".encode())
        
    def checksweepfinished(self):
        self.sock.send("SWEEP?\n".encode())
        return (int(self.read()) == 0)
        
#     def startprimarypeaksearch(self):
#         self.sock.send("PKSR\n".encode())
        
#     def startnextpeakright(self):
#         self.sock.send("NSRR\n".encode())
#         
#     def startnextpeakleft(self):
#         self.sock.send("NSRL\n".encode())
        
#    def checkpeakfinished(self):
#        self.serialport.flushInput()
#        self.serialport.write("ESR2?\n".encode()) #Looks like 4 bytes returned
#        bytearray = self.serialport.read(4)
#        return (bytearray[0] & 2**0)>0 #Bit 0 is check bit for peak search
        
    def readpeak(self):
        self.sock.send("SMSR1\n".encode())
        self.sock.send("MKR1\n".encode())
        
        output = []
        
        while True:
            self.sock.send("MKR?\n".encode())
            stringarray = self.read().split(",")  # Always 22 bits?
            if len(stringarray) == 2:
                break
        peak = {}
        peak["wavelength"] = float(stringarray[0])
        peak["power"] = float(stringarray[1])
        output.append(peak)
        
        while True:
            self.sock.send("MKR?2\n".encode())
            stringarray = self.read().split(",")  # Always 22 bits?
            if len(stringarray) == 2:
                break
        peak = {}
        peak["wavelength"] = float(stringarray[0])
        peak["power"] = float(stringarray[1])
        output.append(peak)
        
        return output
        
    def centeronpeak(self):
        self.sock.send("CTR=P\n".encode())
        
    def writeresolution(self, resolution):  # resolution in nm
        self.sock.send(("RESLN" + format(resolution, '04.2f') + "\n").encode())
        
    def closesocket(self):
        self.sock.close()
        






        
    def set_video_bandwidth(self, vbw):
        raise NotImplementedError
        
    def read_video_bandwidth(self):
        raise NotImplementedError
        
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
    
    def search_peak(self):
        peak = self.instrument.ask('SSI; *WAI ; PKS PEAK; TMK?\n').split(',')  #starts single sweep, searches for peak, and returns peak
        return float(peak[0])
    
    def read_smsr(self):
        self.instrument.write('ANA SMSR,2NDPEAK\n')
        data = self.instrument.ask('ANAR?').split(',')
        return float(data[1])
