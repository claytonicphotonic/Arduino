'''
Created on Feb 14, 2014

@author: bay
'''

import socket

class GPIBEthernet(): #No longer limited to just GPIB Ethernet contollers
    def __init__(self, interface, gpib_addr):
        self.interface = interface
        self.gpib_addr = gpib_addr
        
    def read(self):
        return self.interface.read(self.gpib_addr)
        
    def send(self, string):
        self.interface.send(string, self.gpib_addr)
        
    def ask(self, string, delay=None):
        return self.interface.ask(string, self.gpib_addr, delay=delay)
    
    def closesocket(self):
        self.interface.closesocket()
        
    def close(self):
        self.closesocket()