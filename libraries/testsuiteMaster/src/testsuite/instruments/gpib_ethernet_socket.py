# -*- coding: utf-8 -*-
"""
Created on Tue Mar 04 19:53:11 2014

@author: jsbarton
"""

import socket
import time

class GPIBEthernet():
    def __init__(self, ip, port=1234, timeout=2, ip_timeout=.5, command_delay=0.05):
        self.timeout = timeout
        self.command_delay = command_delay
        
        timeout_time = time.time() + timeout
        while True:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP )
                self.sock.settimeout(ip_timeout)
                self.sock.connect( ( ip, port ) )
                time.sleep(self.command_delay)
                self.sock.send("++mode 1\n".encode())
                time.sleep(self.command_delay)
                self.sock.send("++auto 0\n".encode())
                time.sleep(self.command_delay)
                self.sock.send("++read_tmo_ms 500\n".encode())
                time.sleep(self.command_delay)
                self.sock.send("++eos 3\n".encode())
                time.sleep(self.command_delay)
                self.sock.send("++eoi 1\n".encode())
                time.sleep(self.command_delay)
                return
            except socket.timeout:
                if time.time() < timeout_time:
                    continue
                else:
                    raise(socket.timeout)
        
    def read(self, gpib_addr):
        self.sock.send(("++addr " + gpib_addr + "\n").encode())
        time.sleep(self.command_delay)
        self.sock.send("++read eoi\n".encode())
        time.sleep(self.command_delay)
        return(self.sock.makefile().readline())
        
    def send(self, string, gpib_addr):
        self.sock.send(("++addr " + gpib_addr + "\n").encode())
        time.sleep(self.command_delay)
        self.sock.send((string + "\n").encode())
        time.sleep(self.command_delay)
        
    def ask(self, string, gpib_addr, delay=None):
        command_delay = self.command_delay
        if delay is not None:
            self.command_delay = delay
        timeout_time = time.time() + self.timeout
        while True:
            try:
                self.send(string, gpib_addr)
                time.sleep(delay)
                output = self.read(gpib_addr)
                self.command_delay = command_delay
                return output
            except socket.timeout:
                if time.time() < timeout_time:
                    continue
                else:
                    raise(socket.timeout)
    
    def closesocket(self):
        self.sock.close()