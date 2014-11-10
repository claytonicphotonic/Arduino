# TED8020 TEC Controller Card, ±2 A, 16 W, Thermistor/IC-Sensor
import serial
class TED(): #*************************************************************
    def __init__(self, portname):
        self.serialport = serial.serial_for_url(portname, do_not_open=True)
        self.serialport.close()  # In case port is already open
        self.serialport.open()
        self.serialport.write("++addr 10\n".encode())
        self.successread = 0
        self.failread = 0
        
    # Write commands*******************************************************    
    def tedslot(self, slot):
        self.serialport.write((":SLOT " + format(slot)+"\n").encode()) # Selects a slot for further programming 1-8

    def tedport(self, port):
        self.serialport.write((":PORT " + format(port)+ "\n").encode()) # Selects port for further 1-2
        
    def tedon(self):
        self.serialport.write((":TEC ON\n").encode()) # Switching the TEC output on

    def tedoff(self):
        self.serialport.write(":TEC OFF\n".encode()) # Switching the TEC output off
                
    # Read commands **************************************************************    
    def tedreadslot(self):
        self.serialport.write(":SLOT?\n".encode()) # Queries the selected slot
        tedslotid = self.serialport.read()
        return tedslotid
        
    def tedreadport(self):
        self.serialport.write(":PORT?\n".encode()) # Queries the selected port
        tedportid = self.serialport.read()
        return tedportid
        
    def tedread(self):
        self.serialport.write(":TEC?\n".encode()) # Reads status of the output
        tedstatus = self.serialport.read()
        return tedstatus
        
    def tedreadset(self):
        self.serialport.write(":TEMP:SET?\n".encode()) # Reads the set temperature
        tedtemp = self.serialport.read()
        return tedtemp

    def tedtemp(self):
        self.serialport.write(":TEMP:ACT?\n".encode()) # Reads the actual temperature
        tedtempact = self.serialport.read()
        return tedtempact
