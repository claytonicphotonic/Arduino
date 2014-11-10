'''
Created on May 29, 2014

@author: bay
'''

import time
import ctypes
import random

VOLTAGE_SOURCE = 0
CURRENT_SOURCE = 1

class ElectrodeBase(object):
    def __init__(self, 
                 short_name="", 
                 long_name=None, 
                 static_current=None, 
                 static_voltage=None, 
                 current_limit_min=None, 
                 current_limit_max=None, 
                 voltage_limit_min=None, 
                 voltage_limit_max=None, 
                 current_compliance=None, 
                 voltage_compliance=None, 
                 output_on=True, 
                 output_type=None):
        # This needs to be called by subclasses
        self.short_name = short_name
        if long_name is None:
            self.long_name = short_name
        else:
            self.long_name = long_name
        self.static_current = static_current
        self.static_voltage = static_voltage
        self.current_limit_min = current_limit_min
        self.current_limit_max = current_limit_max
        self.voltage_limit_min = voltage_limit_min
        self.voltage_limit_max = voltage_limit_max
        self.initial_on = output_on
#         self.current_compliance = current_compliance
#         self.voltage_compliance = voltage_compliance
        
        self._hardware_current_limit = None
        self._hardware_voltage_limit = None
        self._hardware_current_compliance = None
        self._hardware_voltage_compliance = None
        
        if current_compliance is not None:
            self.write_current_compliance(current_compliance)
        if voltage_compliance is not None:
            self.write_voltage_compliance(voltage_compliance)
        
        self.output_type = output_type
        if output_type is not None:
            if output_type == CURRENT_SOURCE:
                self.set_output_type(CURRENT_SOURCE)
            elif output_type == VOLTAGE_SOURCE:
                self.set_output_type(VOLTAGE_SOURCE)
            else:
                raise ValueError("output_type must be set to CURRENT_SOURCE or VOLTAGE_SOURCE")
            
            self.zero()
            
            if output_on:
                self.set_output_on(True)
    
    def _write_hardware_current(self, current):
        raise NotImplementedError
    
    def _write_hardware_voltage(self, voltage):
        raise NotImplementedError
    
    def _read_hardware_current(self):
        raise NotImplementedError
    
    def _read_hardware_voltage(self):
        raise NotImplementedError
    
    def write_current_compliance(self, current):
        raise NotImplementedError
    
    def write_voltage_compliance(self, voltage):
        raise NotImplementedError
    
    def read_compliance(self):
        raise NotImplementedError
    
    def set_output_type(self, state):
        raise NotImplementedError
    
    def read_output_type(self):
        return self.output_type # Important; this returns the output type saved in software, which *should* be what the source is set to, but it is not checked!
    
    def set_output_on(self, state):
        raise NotImplementedError
    
    def write_current(self, current):
        if current > self.current_limit_max or current < self.current_limit_min:
            raise Exception(self.long_name + " current out of limit")
            
        self._write_hardware_current(current)
        
    def write_voltage(self, voltage):
        if voltage > self.voltage_limit_max or voltage < self.voltage_limit_min:
            raise Exception(self.long_name + " voltage out of limit")
            
        self._write_hardware_voltage(voltage)
        
    def read_current(self):
        return self._read_hardware_current()
    
    def read_voltage(self):
        return self._read_hardware_voltage()
    
    def zero(self):
        if self.output_type == CURRENT_SOURCE and self.current_limit_min <= 0 and self.current_limit_max >= 0:
            self.write_current(0)
            return 0
        elif self.output_type == CURRENT_SOURCE and self.static_current is not None:
            self.write_static_current()
            return self.static_current
        elif self.output_type == CURRENT_SOURCE:
            # set to the allowed value closest to zero
            value = min(abs(self.current_limit_min), abs(self.current_limit_max)) * (abs(self.current_limit_min) / self.current_limit_min)
            self.write_current(value)
            return value
        elif self.output_type == VOLTAGE_SOURCE and self.voltage_limit_min <= 0 and self.voltage_limit_max >= 0:
            self.write_voltage(0)
            return 0
        elif self.output_type == VOLTAGE_SOURCE and self.static_voltage is not None:
            self.write_static_voltage()
            return self.static_voltage
        elif self.output_type == VOLTAGE_SOURCE:
            value = min(abs(self.voltage_limit_min), abs(self.voltage_limit_max)) * (abs(self.voltage_limit_min) / self.voltage_limit_min)
            self.write_voltage(value)
            return value
        else:
            raise Exception(self.long_name + " invalid output type")
        
    def write_static_current(self):
        if self.static_current is None:
            raise Exception(self.long_name + " does not define a static current")
        else:
            self.write_current(self.static_current)
            
    def write_static_voltage(self):
        if self.static_voltage is None:
            raise Exception(self.long_name + " does not define a static voltage")
        else:
            self.write_voltage(self.static_voltage)
            
class K2600(object):
    def __init__(self, ip):
        import visa
        self.visa_instrument = visa.Instrument('TCPIP::' + ip + '::inst0::INSTR')
         
    def close(self):
        self.visa_instrument.close()
            
class K2600Channel(ElectrodeBase):
    def __init__(self, 
                 keithley, 
                 channel,  
                 short_name="", 
                 long_name=None, 
                 static_current=None, 
                 static_voltage=None, 
                 current_limit_min=None, 
                 current_limit_max=None, 
                 voltage_limit_min=None, 
                 voltage_limit_max=None, 
                 current_compliance=None, 
                 voltage_compliance=None, 
                 output_on=True, 
                 output_type=None):
        self.visa_instrument = keithley.visa_instrument
        self.channel = channel
        
        self.set_measure_autorangei()
        self.set_measure_autorangev()
        
        self.set_source_autorangei()
        self.set_source_autorangev()
        
        self.write_nplc(0.2)
        
        self.set_high_z()
        
        ElectrodeBase.__init__(self, 
                                short_name=short_name, 
                                long_name=long_name, 
                                static_current=static_current, 
                                static_voltage=static_voltage, 
                                current_limit_min=current_limit_min, 
                                current_limit_max=current_limit_max, 
                                voltage_limit_min=voltage_limit_min, 
                                voltage_limit_max=voltage_limit_max, 
                                current_compliance=current_compliance, 
                                voltage_compliance=voltage_compliance, 
                                output_on=output_on, 
                                output_type=output_type)
                
    def _write_hardware_current(self, current):
        if self.output_type != CURRENT_SOURCE:
            self.set_output_type(CURRENT_SOURCE)
        self.visa_instrument.write('smu' + self.channel + '.source.leveli = ' + str(current / 1000))
        time.sleep(0.005)  #Wait for the input to stabilize
    
    def _write_hardware_voltage(self, voltage):
        if self.output_type != VOLTAGE_SOURCE:
            self.set_output_type(VOLTAGE_SOURCE)
        self.visa_instrument.write('smu' + self.channel + '.source.levelv = ' + str(voltage))
        time.sleep(0.005)  #Wait for the input to stabilize
    
    def _read_hardware_current(self):
        self.visa_instrument.write("print (" + 'smu' + self.channel + ".measure.i())")
        time.sleep(0.005)
        return (self.visa_instrument.read_values()[0] * 1000)
    
    def _read_hardware_voltage(self):
        self.visa_instrument.write("print (" + 'smu' + self.channel + ".measure.v())")
        time.sleep(0.005)
        return self.visa_instrument.read_values()[0]
        
    def set_output_type(self, state):
        if state == VOLTAGE_SOURCE:
            self.visa_instrument.write('smu' + self.channel + ".source.func = " + 'smu' + self.channel + ".OUTPUT_DCVOLTS")
            self.visa_instrument.write("display." + 'smu' + self.channel + ".measure.func = display.MEASURE_DCAMPS")
            self.visa_output_type = "V"
        elif state == CURRENT_SOURCE:
            self.visa_instrument.write('smu' + self.channel + ".source.func = " + 'smu' + self.channel + ".OUTPUT_DCAMPS")
            self.visa_instrument.write("display." + 'smu' + self.channel + ".measure.func = display.MEASURE_DCVOLTS")
            self.visa_output_type = "I"
        else:
            raise IOError
    
    def set_measure_autorangei(self):
        self.visa_instrument.write('smu' + self.channel + '.measure.autorangei = ' + 'smu' + self.channel + '.AUTORANGE_ON')
        
    def set_measure_autorangev(self):
        self.visa_instrument.write('smu' + self.channel + '.measure.autorangev = ' + 'smu' + self.channel + '.AUTORANGE_ON')
        
    def set_source_autorangei(self):    
        self.visa_instrument.write('smu' + self.channel + '.source.autorangei = ' + 'smu' + self.channel + '.AUTORANGE_ON')
        
    def set_source_autorangev(self):    
        self.visa_instrument.write('smu' + self.channel + '.source.autorangev = ' + 'smu' + self.channel + '.AUTORANGE_ON')
        
    def write_nplc(self, nplc):    
        self.visa_instrument.write('smu' + self.channel + '.measure.nplc = ' + str(nplc))
        
    def set_high_z(self):    
        self.visa_instrument.write('smu' + self.channel + ".source.offmode = " + 'smu' + self.channel + ".OUTPUT_HIGH_Z")    
    
    def write_current_compliance(self, current):
        self.visa_instrument.write('smu' + self.channel + '.source.limiti = ' + str(current / 1000))
    
    def write_voltage_compliance(self, voltage):
        self.visa_instrument.write('smu' + self.channel + '.source.limitv = ' + str(voltage))
    
    def read_compliance(self):
        self.visa_instrument.write('smu' + self.channel + '.source.compliance')
        time.sleep(0.005)
        return self.visa_instrument.read_values()[0] == 'true'
    
    def set_output_on(self, state):
        if state:
            self.visa_instrument.write('smu' + self.channel + '.source.output = ' + 'smu' + self.channel + '.OUTPUT_ON')
        else:
            self.visa_instrument.write('smu' + self.channel + '.source.output = ' + 'smu' + self.channel + '.OUTPUT_OFF')
            time.sleep(0.05)
            
class NI414X(object):
    def __init__(self, slot, channels=None, reset=True, option_string="", initiate=True):
        self.dcpower = ctypes.cdll.LoadLibrary('nidcpower_32')
        proto = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_ushort, ctypes.c_char_p, ctypes.POINTER(ctypes.c_ulong))
        dcpower_init = proto(("niDCPower_InitializeWithChannels", self.dcpower))
        if channels is None:
            channel_string = ""
        else:
            channel_string = ""
            for channel in channels:
                channel_string = channel_string + format(channel) + ','
            channel_string = channel_string[:-1]
            
        if reset:
            reset_c = 1
        else:
            reset_c = 0
            
        self.viSession = ctypes.c_uint()
        error_code = dcpower_init(("PXI1Slot" + format(slot)).encode(), channel_string.encode(), reset_c, option_string.encode(), ctypes.byref(self.viSession))
        
        if error_code != 0:
            raise Exception(self.error_message(error_code))
            
        if initiate:
            self.initiate()
        
    def error_message(self, error_code):
        proto = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_int, ctypes.c_char_p)
        func = proto(("niDCPower_error_message", self.dcpower))
        
        error_code_c = ctypes.c_int(error_code)
        error_message = ctypes.c_char_p((" " * 256).encode())
        func(self.viSession, error_code_c, error_message)
        return error_message
            
    def initiate(self):
        proto = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong)
        func = proto(("niDCPower_Initiate", self.dcpower))
        error_code = func(self.viSession)
        
        if error_code != 0:
            raise Exception(self.error_message(error_code))
            
    def abort(self):
        proto = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong)
        func = proto(("niDCPower_Abort", self.dcpower))
        error_code = func(self.viSession)
        
        if error_code != 0:
            raise Exception(self.error_message(error_code))
        
    def close(self):
        proto = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong)
        func = proto(("niDCPower_close", self.dcpower))
        error_code = func(self.viSession)
        
        if error_code != 0:
            raise Exception(self.error_message(error_code))
        
class NI414XChannel(ElectrodeBase):
    _HARDWARE_VOLTAGE_OUTPUT = 1006
    _HARDWARE_CURRENT_OUTPUT = 1007
    
    _HARDWARE_MEASURE_VOLTAGE = 1
    _HARDWARE_MEASURE_CURRENT = 0
    
    _HARDWARE_VAL_CURRENT_REGULATE = 0
    
    def __init__(self, 
                 smu, 
                 channel,  
                 short_name="", 
                 long_name=None, 
                 static_current=None, 
                 static_voltage=None, 
                 current_limit_min=None, 
                 current_limit_max=None, 
                 voltage_limit_min=None, 
                 voltage_limit_max=None, 
                 current_compliance=None, 
                 voltage_compliance=None, 
                 output_on=True, 
                 output_type=None):
        self.channel = channel
        self.channel_bytes = format(channel).encode()
        self.smu = smu
        
        ElectrodeBase.__init__(self, 
                                short_name=short_name, 
                                long_name=long_name, 
                                static_current=static_current, 
                                static_voltage=static_voltage, 
                                current_limit_min=current_limit_min, 
                                current_limit_max=current_limit_max, 
                                voltage_limit_min=voltage_limit_min, 
                                voltage_limit_max=voltage_limit_max, 
                                current_compliance=current_compliance, 
                                voltage_compliance=voltage_compliance, 
                                output_on=output_on, 
                                output_type=output_type)
                
    def _write_hardware_current(self, current):
        if self.output_type != CURRENT_SOURCE:
            self.set_output_type(CURRENT_SOURCE)
            
        proto = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_char_p, ctypes.c_double)
        func = proto(("niDCPower_ConfigureCurrentLevel", self.smu.dcpower))
        
        error_code = func(self.smu.viSession, self.channel_bytes, float(current) / 1000)
        
        if error_code != 0:
            raise Exception(self.smu.error_message(error_code))
    
    def _write_hardware_voltage(self, voltage):
        if self.output_type != VOLTAGE_SOURCE:
            self.set_output_type(VOLTAGE_SOURCE)
            
        proto = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_char_p, ctypes.c_double)
        func = proto(("niDCPower_ConfigureVoltageLevel", self.smu.dcpower))
        
        error_code = func(self.smu.viSession, self.channel_bytes, voltage)
        
        if error_code != 0:
            raise Exception(self.smu.error_message(error_code))
        
    def _measure(self, measure_type):
        proto = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_double))
        func = proto(("niDCPower_Measure", self.smu.dcpower))
        
        output = ctypes.c_double()
        
        error_code = func(self.smu.viSession, self.channel_bytes, measure_type, ctypes.byref(output))
        
        if error_code != 0:
            raise Exception(self.smu.error_message(error_code))
        
        return output.value  
    
    def _read_hardware_current(self):
        return self._measure(self._HARDWARE_MEASURE_CURRENT) * 1000
    
    def _read_hardware_voltage(self):
        return self._measure(self._HARDWARE_MEASURE_VOLTAGE)
        
    def set_output_type(self, state, initiate=True):
        proto = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_char_p, ctypes.c_int)
        func = proto(("niDCPower_ConfigureOutputFunction", self.smu.dcpower))
        
        if state == CURRENT_SOURCE:
            hardware_state = self._HARDWARE_CURRENT_OUTPUT
        elif state == VOLTAGE_SOURCE:
            hardware_state = self._HARDWARE_VOLTAGE_OUTPUT
                   
        self.smu.abort()
        error_code = func(self.smu.viSession, self.channel_bytes, hardware_state)
        
        self.output_type = state
        
        if error_code != 0:
            raise Exception(self.smu.error_message(error_code))
            
        if initiate:
            self.smu.initiate()
    
    def write_current_compliance(self, current):
        proto = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_char_p, ctypes.c_int, ctypes.c_double)
        func = proto(("niDCPower_ConfigureCurrentLimit", self.smu.dcpower))
        
        error_code = func(self.smu.viSession, self.channel_bytes, self._HARDWARE_VAL_CURRENT_REGULATE, current / 1000)
        
        if error_code != 0:
            raise Exception(self.smu.error_message(error_code))
    
    def write_voltage_compliance(self, voltage):
        proto = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_char_p, ctypes.c_double)
        func = proto(("niDCPower_ConfigureVoltageLimit", self.smu.dcpower))
        
        error_code = func(self.smu.viSession, self.channel_bytes, voltage)
        
        if error_code != 0:
            raise Exception(self.smu.error_message(error_code))
    
    def read_compliance(self):
        proto = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_double))
        func = proto(("niDCPower_QueryInCompliance", self.smu.dcpower))
        
        output = ctypes.c_bool()
        
        error_code = func(self.smu.viSession, self.channel_bytes, ctypes.byref(output))
        
        if error_code != 0:
            raise Exception(self.smu.error_message(error_code))
        
        return output.value  
    
    def set_output_on(self, state):
        proto = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_char_p, ctypes.c_ushort)
        func = proto(("niDCPower_ConfigureOutputEnabled", self.smu.dcpower))
        
        if state:
            output_int = 1
        else:
            output_int = 0
        
        error_code = func(self.smu.viSession, self.channel_bytes, output_int)
        
        if error_code != 0:
            raise Exception(self.smu.error_message(error_code))
        
class LinkedChannel(ElectrodeBase): # Links an arbitrary number of channels to show as a single channel. NOTE: reading values looks at the first in the list, which may not be what is intended!
    def __init__(self, 
                 channel_list, 
                 short_name="", 
                 long_name=None):
        self.channel_list = channel_list
        
        self.short_name = short_name
        if long_name is None:
            self.long_name = short_name
        else:
            self.long_name = long_name
        
        #This deliberately does not call the __init__ function of ElectrodeBase
        
    @property
    def initial_on(self):
        return self.channel_list[0].initial_on
        
    @property
    def static_current(self):
        return self.channel_list[0].static_current
    
    @property
    def static_voltage(self):
        return self.channel_list[0].static_voltage
    
    @property
    def current_limit_min(self):
        return self.channel_list[0].current_limit_min
    
    @property
    def current_limit_max(self):
        return self.channel_list[0].current_limit_max
    
    @property
    def voltage_limit_min(self):
        return self.channel_list[0].voltage_limit_min
    
    @property
    def voltage_limit_max(self):
        return self.channel_list[0].voltage_limit_max
    
    @property
    def current_compliance(self):
        return self.channel_list[0].current_compliance
    
    @property
    def voltage_compliance(self):
        return self.channel_list[0].voltage_compliance
    
    @property
    def output_on(self):
        return self.channel_list[0].output_on
    
    @property
    def output_type(self):
        return self.channel_list[0].output_type
                
    def _write_hardware_current(self, current):
        for channel in self.channel_list:
            channel._write_hardware_current(current)
    
    def _write_hardware_voltage(self, voltage):
        for channel in self.channel_list:
            channel._write_hardware_voltage(voltage)
    
    def _read_hardware_current(self):
        return self.channel_list[0]._read_hardware_current()
    
    def _read_hardware_voltage(self):
        return self.channel_list[0]._read_hardware_voltage()
        
    def set_output_type(self, state):
        for channel in self.channel_list:
            channel.set_output_type(state)
    
    def write_current_compliance(self, current):
        for channel in self.channel_list:
            channel.write_current_compliance(current)
    
    def write_voltage_compliance(self, voltage):
        for channel in self.channel_list:
            channel.write_current_compliance(voltage)
    
    def read_compliance(self):
        output = True
        for channel in self.channel_list:
            output = output and channel.read_compliance()
            
        return output
    
    def set_output_on(self, state):
        for channel in self.channel_list:
            channel.set_output_on(state)
        
class DummyElectrode(ElectrodeBase):
    def __init__(self, 
                 short_name="", 
                 long_name=None, 
                 static_current=None, 
                 static_voltage=None, 
                 current_limit_min=None, 
                 current_limit_max=None, 
                 voltage_limit_min=None, 
                 voltage_limit_max=None, 
                 current_compliance=None, 
                 voltage_compliance=None, 
                 output_on=True, 
                 output_type=None):
        
        ElectrodeBase.__init__(self, 
                                short_name=short_name, 
                                long_name=long_name, 
                                static_current=static_current, 
                                static_voltage=static_voltage, 
                                current_limit_min=current_limit_min, 
                                current_limit_max=current_limit_max, 
                                voltage_limit_min=voltage_limit_min, 
                                voltage_limit_max=voltage_limit_max, 
                                current_compliance=current_compliance, 
                                voltage_compliance=voltage_compliance, 
                                output_on=output_on, 
                                output_type=output_type)
                
    def _write_hardware_current(self, current):
        pass
    
    def _write_hardware_voltage(self, voltage):
        pass
    
    def _read_hardware_current(self):
        return random.random() * 15
    
    def _read_hardware_voltage(self):
        return random.random() * 2
        
    def set_output_type(self, state, initiate=True):
        self.output_type = state
    
    def write_current_compliance(self, current):
        pass
    
    def write_voltage_compliance(self, voltage):
        pass
    
    def read_compliance(self):
        return True
    
    def set_output_on(self, state):
        pass
    
class SFPElectrode(ElectrodeBase):
    def __init__(self, 
                 testrig_laser_section, 
                 short_name="", 
                 long_name=None, 
                 static_current=None, 
                 static_voltage=None, 
                 current_limit_min=None, 
                 current_limit_max=None, 
                 voltage_limit_min=None, 
                 voltage_limit_max=None, 
                 current_compliance=None, 
                 voltage_compliance=None, 
                 output_on=True, 
                 output_type=None):
        
        self.laser_section = testrig_laser_section
        
        ElectrodeBase.__init__(self, 
                                short_name=short_name, 
                                long_name=long_name, 
                                static_current=static_current, 
                                static_voltage=static_voltage, 
                                current_limit_min=current_limit_min, 
                                current_limit_max=current_limit_max, 
                                voltage_limit_min=voltage_limit_min, 
                                voltage_limit_max=voltage_limit_max, 
                                current_compliance=current_compliance, 
                                voltage_compliance=voltage_compliance, 
                                output_on=output_on, 
                                output_type=output_type)
                
    def _write_hardware_current(self, current):
        self.laser_section.write_current(current)
    
    def _write_hardware_voltage(self, voltage):
        raise IOError("SFP cannot set voltage on electrodes")
    
    def _read_hardware_current(self):
        raise IOError("SFP cannot read output current on electrodes")
    
    def read_set_current(self):
        return self.laser_section.read_current()
    
    def _read_hardware_voltage(self):
        return self.laser_section.read_voltage()
        
    def set_output_type(self, state):
        self.output_type = state # Does nothing for SFP
    
    def write_current_compliance(self, current):
        #SFP compliances should be set in SFP GUI, and are saved in FPGA
        pass
    
    def write_voltage_compliance(self, voltage):
        # SFP compliances should be set in SFP GUI, and are saved in FPGA
        pass
    
    def read_compliance(self):
        return True #No way to tell from SFP
    
    def set_output_on(self, state):
        # SFP cannot set electrodes output, set current to zero instead
        pass
            