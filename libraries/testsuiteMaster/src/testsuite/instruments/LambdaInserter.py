# -*- coding: utf-8 -*-
  #For each Lambda that is good:
    #write 0x30 to Byte 0
    #write itu_index to byte 1
    #write LasPha to bytes 2-3
    #write Mirr2 to bytes 4-5
    #write Gain 1 to bytes 6-7
    #write Gain 2 to bytes 8-9
    #write Mirr1 to bytes 10-11
    #write SOA1 to bytes 12-13
    #write SOA1 to bytes 14-15
    #write 16 bytes of 00

import numpy
import struct

class LambdaInserter():
    def __init__(self, input_file):
        print("Working on Inserting Lambda")
        self.input_file = input_file
        self.itu_index=[]
        self.itu_wavelength=[]
        self.mirr1_current=[]
        self.mirr2_current=[]
        self.LasPha_current=[]
        self.SOA1_current=[]
        self.SOA2_current=[]
    
    def execute_parse(self):
        #********************************
        #Perhaps these will need to be Dynamic
        #Read each of the values from the device
        mirr1_max = 90
        mirr2_max = 90
        phase_max = 20
        gain1_max = 180
        gain2_max = 15
        soa1_max = 300
        soa2_max = 100
        
        gain1_current = 150
        gain2_current = 0
        #********************************
        
        fi = open(self.input_file, "r")
        fi.seek(0, 2);
        file_len = fi.tell()
        fi.seek(0, 0);
        str = fi.read(file_len)
        column_length = len(str.splitlines()[0].split(","))
        data = str.replace("\n",",").split(",")
        data_len = len(data)  
        
        begin_pos = 0
        while(data[begin_pos] != "itu_index"):
            begin_pos += 1
        
        fo = ""
        
        i = begin_pos + column_length
        while(i < data_len-1):
            self.itu_index.append(int(data[i]))
            i+=1
            self.itu_wavelength.append(data[i])
            i+=1
            self.mirr2_current.append(int(float(data[i])/mirr2_max * 16383))
            i+=1
            self.mirr1_current.append(int(float(data[i])/mirr1_max * 16383))
            i+=1
            self.LasPha_current.append(int(float(data[i])/phase_max * 16383))
            i+=1
            self.SOA1_current.append(int(float(data[i])/soa1_max * 16383))
            i+=1
            soa2_curr = ((numpy.exp((float(data[i])-45)/27)-0.121)/0.9)
            self.SOA2_current.append(int(soa2_curr/soa2_max * 16383))
            i+=1
            if(column_length > 7):
                i+=(column_length-7) 
          
        highest_ndx = self.itu_index[-1] #get the last element in the ITU_index list
        
        j=0
        for j in range(32):
            fo+=("00 ")
        
        f = 0
        for q in range(1,highest_ndx):
            i = q-1
            if(self.mirr1_current[i] < 0):
                # this lambda is  unavailable
                #write 32 bytes of 00  
                j=0
                for j in range(32):
                    fo+=("00 ")
            else:
                #this lambda is available
                fo+=("30 ")
                as_s = "{:02x} ".format(self.itu_index[i])
                fo+=(as_s)
                f+=1
                
                bytes = struct.pack('!H', self.LasPha_current[i])
                as_s0 = "{:02x}".format(bytes[0])
                fo+=(as_s0)
                fo+=(" ")
                as_s1 = "{:02x} ".format(bytes[1])
                fo+=(as_s1)
                f+=2
                
                bytes = struct.pack('!H', self.mirr2_current[i])
                as_s0 = "{:02x} ".format(bytes[0])
                fo+=(as_s0)
                as_s1 = "{:02x} ".format(bytes[1])
                fo+=(as_s1)
                f+=2
                
                bytes = struct.pack('!H', int(gain1_current/gain1_max*16383))
                as_s0 = "{:02x} ".format(bytes[0])
                fo+=(as_s0)
                as_s1 = "{:02x} ".format(bytes[1])
                fo+=(as_s1)
                f+=2
                
                bytes = struct.pack('!H', 0)
                as_s0 = "{:02x} ".format(bytes[0])
                fo+=(as_s0)
                as_s1 = "{:02x} ".format(bytes[1])
                fo+=(as_s1)
                f+=2    
                
                bytes = struct.pack('!H', self.mirr1_current[i])
                as_s0 = "{:02x} ".format(bytes[0])
                fo+=(as_s0)
                as_s1 = "{:02x} ".format(bytes[1])
                fo+=(as_s1)
                f+=2
                
                bytes = struct.pack('!H', self.SOA1_current[i])
                as_s0 = "{:02x} ".format(bytes[0])
                fo+=(as_s0)
                as_s1 = "{:02x} ".format(bytes[1])
                fo+=(as_s1)
                f+=2
                
                bytes = struct.pack('!H', self.SOA2_current[i])
                as_s0 = "{:02x} ".format(bytes[0])
                fo+=(as_s0)
                as_s1 = "{:02x} ".format(bytes[1])
                fo+=(as_s1)
                f+=2
                
                # MZM
                as_s0 = "{:02x} ".format(0)
                fo+=(as_s0)
                as_s1 = "{:02x} ".format(8)
                fo+=(as_s1)
                f+=2
                
                # MZM
                as_s0 = "{:02x} ".format(0)
                fo+=(as_s0)
                as_s1 = "{:02x} ".format(8)
                fo+=(as_s1)
                f+=2
                
                j=0
                for j in range(12):
                    #This is where 00 gets written to the PROM
                    fo+=("00 ")
                    f+=1
    
        fi.close()
        return fo