# Anritsu MP1764A
class EA(): #************************************************************
    def __init__(self, portname):
        self.serialport = serial.serial_for_url(portname, do_not_open=True)
        self.serialport.close()  # In case port is already open
        self.serialport.open()
        self.serialport.write("++addr 2\n".encode())
        self.successread = 0
        self.failread = 0
        
    # Write commands ************
    def pattern(self, pattern):
        self.serialport.write("PTN " + "format(pattern)\n".encode()) # Set EA Pattern default 9 - 2^31-1
        
    def measmode(self, measmode):
        self.serialport.write("MOD " + "format(measmode)\n".encode()) # Set EA measurement mode default 2 - Untimed BER measurement mode
        
    def start(self):
        self.serialport.write("STA\n".encode()) # BER Measurement restart
        
    def stop(self):
        self.serialport.write("STO\n".encode()) # BER Measurement stop
        
    def errortrigger(self):
        self.serialport.write("EAT 1\n".encode()) # Error Analysis Trigger reset  
        
    def errordata(self, bitpage):
        self.serialport.write("EAP " + "format(bitpage)\n".encode()) # Set Error Analysis Page 1-16  
        
    def tol(self, tolerance):
        self.serialport.write("TOL " + "format(tolerance)\n".encode()) # Set EA tolerance for BER default 0.000000001
        
    # Read commands *****************************************    
    def ber(self):                
        self.serialport.write("ER?\n".encode()) # Measure BER
        BER = self.serialport.read()
        return BER
 
    def synch(self):       
        self.serialport.write("SLI?\n".encode()) # Synchronization status 0 - Synch good, 1 - Loss of synch
        SLI = self.serialport.read()
        return synchstatus

    def datathreshold(self):
        self.serialport.write("DTH?\n".encode()) # Data input threshold voltage
        DTH = self.serialport.read()
        return DTH
        
    def clockphase(self):
        self.serialport.write("CPA?\n".encode()) # Clock input phase delay
        CPA = self.serialport.read()
        return CPA

    def errordata(self):
        self.serialport.write("EAB?\n".encode()) # Error Analysis Data
        EAB = self.serialport.read()
        return EAB
        
    def errorpage(self):
        self.serialport.write("EAP?\n".encode()) # Error analysis pattern page
        EAP = self.serialport.read()
        return EAP
