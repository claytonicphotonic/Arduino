# Teraxion CS-TDCMB

import scipy.constants

def to_ieee754(value):
    hexlist = list(struct.pack('f', value))
    hexlist.reverse()
    output_string = ''
    for hex_value in hexlist:
        output_string = output_string + format(hex_value, '02X')
    return output_string

class TDCU(): #************************************************************
    BLUE_WAVELENGTH = 1528.77
    CENTER_WAVELENGTH = 1546.52
    RED_WAVELENGTH = 1565.49
    
    def __init__(self, portname):
        self.serialport = serial.serial_for_url(portname, do_not_open=True)
        self.serialport.close()  # In case port is already open
        self.serialport.open()
        
    # Read commands **************************************************
    def status(self):
        self.serialport.write("S6000P\n".encode()) # Module ready query
        STAT = self.serialport.read()
        return STAT
        
    # Write commands **************************************************
    def poweron(self):
        self.serialport.write("S601EP\n".encode()) # Enable output
        
    def poweroff(self):
        self.serialport.write("S601FP\n".encode()) # Disable output
    
    def set_frequency(self, wavelength):
        frequency = scipy.constants.c / wavelength #Giga- cancels nano-
        self.serialport.write(("S602E" + to_ieee754(frequency) + "P\n").encode())
        
    def set_dispersion(self, dispersion):
        self.serialport.write(("S6030" + to_ieee754(dispersion) + "P\n").encode())
        
    def close(self):
        self.serialport.close()
