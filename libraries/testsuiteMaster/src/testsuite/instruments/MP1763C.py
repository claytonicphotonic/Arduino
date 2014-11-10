# Anritsu MP1763C

from . import gpib_ethernet

class PG(gpib_ethernet.GPIBEthernet): #***************************************************************
    
    # Write commands ****************    
    def set_clockamplitude(self, clkamp):
        self.send("CAP " + format(clkamp)) # Set clock amplitude 0.25 to 2V
        
    def set_resolution(self, res):
        self.send("RES " + format(res)) # Set clock resolution 0 - kHz, 1 - MHz
        
    def set_frequency(self, frequency):
        self.send("FRQ " + format(frequency)) # Set PG frequency
        
    def set_logic(self, logic):
        self.send("LGC " + format(logic)) # Set Pattern Logic 0 - Positive, 1 - Negative
        
    def set_patternselection(self, patternselection):
        self.send("PTS " + format(patternselection)) # Set Pattern Selection Default is 3; 0 - Alternate, 1 - Data, 2 - Zero subst, 3 - PRBS
        
    def set_pattern(self, pattern):
        self.send("PTN " + format(pattern)) # Set Pattern 2 - 2^7-1, 3 - 2^9-1, 5 - 2^11-1, 6 - 2^15-1, 7 - 2^20-1, 8 - 2^23-1, 9 - 2^31-1
        
    def set_errorinsertion(self, error):
        self.send("EAD " + format(error)) # Set Error insertion default 0 is off
        
    def set_negoutputamp(self, databaroutput):
        self.send("DAP " + format(databaroutput)) # Set positive data voltage -0.25 to -2.0V
        
    def set_posoutputamp(self, posdataoutput):
        self.send("NAP " + format(posdataoutput)) # Set negative data voltage 0.25 to 2.0V  
        
    def set_dataoutputoffset(self, dataoutputoffset):
        self.send("DOS " + format(dataoutputoffset)) # Set negative data voltage -2.0 to 2.0V 
         
#     def set_dataoutputoffset(self, databaroutputoffset):
#         self.send("NOS " + format(dataoutputoffset)) # Set negative data voltage -2.0 to 2.0V
