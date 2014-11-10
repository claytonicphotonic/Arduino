# GPD3303S Power Supply
class PS(): #************************************************************
    def __init__(self, portname):
        self.serialport = serial.serial_for_url(portname, do_not_open=True)
        self.serialport.close()  # In case port is already open
        self.serialport.open()
        self.successread = 0
        self.failread = 0
        
    # Write commands ************
    def setcurrent(self, channel, current):
        self.serialport.write("ISET " + "format(channel):" + "format(current)\n".encode()) # Set channel output current limit (A)
    def setvoltage(self, channel, voltage):
        self.serialport.write("VSET " + "format(channel):" + "format(voltage)\n".encode()) # Set channel output voltage (V)
    def enableoutput(self):
        self.serialport.write("OUT 1\n".encode()) # Turn on the output
    def disableoutput(self):
        self.serialport.write("OUT 0\n".encode()) # Turn off the output

    # Read commands ************        
    def readsetcurrent(self, channel):
        self.serialport.write("ISET " + "format(channel)?\n".encode()) # Query channel output current limit (A)
        current = self.serialport.read()
        return current
    def readsetvoltage(self, channel):
        self.serialport.write("VSET " + "format(channel)?\n".encode()) # Returns the output voltage setting (V)
        voltage = self.serialport.read()
        return voltage
    def actualcurrent(self, channel):
        self.serialport.write("IOUT " + "format(channel)?\n".encode()) # Returns the actual output current (A)
        meascurrent = self.serialport.read()
        return meascurrent
    def actualvoltage(self, channel):
        self.serialport.write("VOUT " + "format(channel)?\n".encode()) # Returns the actual output voltage (V)
        measvoltage = self.serialport.read()
        return measvoltage
