'''
Created on Mar 1, 2014

@author: bay
'''
import visa

class PowerMonitor():
    def __init__(self):
        WAVELENGTH = 1563.0
        inst_list = visa.get_instruments_list()
        inst_str = inst_list[0] + '::INSTR'
        self.instrument = visa.instrument(inst_str)
        self.instrument.write('*CLS\n')
        #self.instrument.write('CORR:WAV' + format(WAVELENGTH) + '\n')
        self.instrument.write('CORR:WAV 1563\n')
        
    def read_value(self):
        try:
            #pom.write('*CLS\n')        
            self.instrument.write('INIT:IMM\n')
            self.instrument.write('CONF:POW\n')
            self.instrument.write('MEAS:POW\n')
            self.instrument.write('READ?\n')
            return self.instrument.read_values()[0] * 1000
        except:
            print('VISA exception')
            return 1e-8
        
    def close(self):
        self.instrument.close()