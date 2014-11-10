'''
Created on Jun 19, 2014

@author: bay
'''
from . import gpib_ethernet

class A86100A(gpib_ethernet.GPIBEthernet):
        
    # Write commands*******************************************************    
    def cleardisplay(self):
        self.send("CDISPLAY") # Clear display screen
        
    def select_channelon(self, channel):
        self.send("CHANNEL" + format(channel) + ":DISPLAY ON") # DISPLAY CHANNEL ON
   
    def select_channeloff(self, channel):
        self.send("CHANNEL" + format(channel) + ":DISPLAY OFF") # DISPLAY CHANNEL OFF
      
    def autoscale(self):                
        self.send("AUTOSCALE") # RUN AUTOSCALE
        
    def select_eyemode(self):
        self.send("SYSTEM:MODE EYE") # SET FOR EYE MODE
        
    def single_acquisition(self):
        self.send("SINGle")
        self.send("*WAI")
    
    # Read commands **************************************************************    
    # Make sure all commands return numerically, may need to strip out units, etc. from inst output
    def read_risetime(self):
        return float(self.ask("MEASURE:RISETIME?")) # MEASURE RISE TIME
        
    def read_falltime(self):
        return float(self.ask("MEASURE:FALLTIME?")) # MEASURE FALL TIME
        
    def read_jitter(self):
        return float(self.ask("MEASURE:CGRADE:JITTER? RMS")) # MEASURE JITTER RMS
        
    def read_snr(self):       
        return float(self.ask("MEASURE:CGRADE:ESN?")) # Measure EYE SIGNAL TO NOISE RATIO
        
    def read_er(self):
        return float(self.ask("MEASURE:CGRADE:ERATIO? DECIBEL")) # Measure EXTINCTION RATIO
            
    def read_eyecrossing(self):
        return float(self.ask("MEASURE:CGRADE:CROSSING?")) # Measure EYE CROSSING
                    
    def read_modulation_depth(self):
        return float(self.ask("MEASURE:CGRADE:EHEIGHT?")) # Measure MODULATION DEPTH
    
    def read_poptavg(self):
        return float(self.ask(":MEASure:APOWer? WATT")) # Measure Average Optical Power

    def read_ptp(self):
        return float(self.ask(":MEASure:CGRade:AMPLitude?")) # Measure optical eye peak to peak
    
    def save_eye_image(self, filename): #This filename is relative to the SCOPE's filesystem! Must be jpg format
        self.send("DISK:SIMAGE \"" + filename + "\", SCReen, INVert")
    
class A86100D(A86100A):
    def read_rin(self):
        return float(self.ask(":AMPLitude:RINoise?")) # Measure RIN