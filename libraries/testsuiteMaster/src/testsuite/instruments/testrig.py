# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 11:05:46 2013

@author: Bay
"""

import struct

from PyQt4 import QtGui
import numpy

from . import debugbox
from . import sfpbreakout
from . import dummybox
from testsuite.sfp_gui.strictdoublevalidator import StrictDoubleValidator

DEVICE_DEBUG_BOARD = 0
DEVICE_SFP_BREAKOUT = 1
DEVICE_DUMMY_BOARD = 2

ALARM_STATUS_GREEN = 0
ALARM_STATUS_YELLOW = 1
ALARM_STATUS_RED = 2


class Testrig():
    """Class representing SFP Interface, using ADCs and DACs"""
    SERIAL_BAUD = 115200
    SERIAL_TIMEOUT = .500
    COMMAND_READ = 144
    COMMAND_WRITE = 160
    
    def __init__(self, portname, devicetype):
        """
        Initialize and connect to SFP.
        
        portname(String) - serial port
        devicetype(int) - Device type, use class constants
        """
        if devicetype == DEVICE_DEBUG_BOARD:
            self.device = debugbox.DebugBox(portname)
        elif devicetype == DEVICE_SFP_BREAKOUT:
            self.device = sfpbreakout.SFP(portname)
        elif devicetype == DEVICE_DUMMY_BOARD:
            self.device = dummybox.DummyBox(portname)
        else:
            raise IOError("Invalid Device Type")
        
        # Set up laser sections
        self.mirror1 = Testrig.LaserSection(self, 814, 10, 90, 728, 844, 860, 864)
        self.laser_phase = Testrig.LaserSection(self, 810, 11, 20, 726, 846, 858, 866)
        self.gain = Testrig.LaserSection(self, 818, 12, 180, 730, 848, None, None)
#         self.gain1.validator.setTop(150)
        self.mirror2 = Testrig.LaserSection(self, 826, 14, 90, 734, 850, 862, 864)
#         self.front.validator.setTop(60)
        self.soa1 = Testrig.LaserSection(self, 822, 15, 300, 736, 852, None, None)
#         self.soa1.validator.setTop(150)
        self.soa2 = Testrig.LaserSection(self, 830, 16, 100, 738, 854, None, None, self.to_display_current_section2, self.to_internal_current_section2)
        self.phase1 = Testrig.LaserSection(self, 834, 13, 100, 732, 856, None, None, self.to_display_current_section2, self.to_internal_current_section2)
        
        self.voltage_max = 2.5 # This is now a constant
        
        self.full_rig = True
        
    def close(self):
        self.device.close()
        
    def write16bit(self, register, value):
        """Write 16-bit integer into register."""
        if value > ((2 ** 16) - 1) or value < 0:
            raise ValueError
        valuearray = struct.pack('!H', value)  # Place value into byte array, format '!H' is short, network order
        self.device.writeregistermulti(register, valuearray)
        
    def read16bit(self, register):
        """read 16-bit from register."""
        valuearray = bytearray(self.device.readregistermulti(register, 2))
        return struct.unpack('!H', valuearray)[0]
        
    def write14bit(self, register, value):
        """Write 14-bit integer into register."""
        if value > ((2 ** 14) - 1) or value < 0:
            raise ValueError
        valuearray = struct.pack('!H', value)  # Place value into byte array, format '!H' is short, network order
        self.device.writeregistermulti(register, valuearray)
        
    def read14bit(self, register):
        """read 14-bit from register."""
        valuearray = bytearray(self.device.readregistermulti(register, 2))
        return struct.unpack('!H', valuearray)[0] & ((2 ** 14) - 1)  # Convert to short and discard first two bits
        
    def read12bit(self, register):
        """Write 12-bit integer into register."""
        valuearray = bytearray(self.device.readregistermulti(register, 2))
        return struct.unpack('!H', valuearray)[0] & ((2 ** 12) - 1)  # Convert to short and discard first four bits
    
    def write12bit(self, register, value):
        """read 12-bit from register."""
        if value > ((2 ** 12) - 1) or value < 0:
            raise ValueError
        valuearray = struct.pack('!H', value)  # Place value into byte array, format '!H' is short, network order
        self.device.writeregistermulti(register, valuearray)
        
    def write24bit(self, register, value):
        """Write 24-bit integer into register."""
        if value > ((2 ** 24) - 1) or value < 0:
            raise ValueError
        valuearray = struct.pack('!I', value)  # Place value into byte array, format '!I' is int, network order
        self.device.writeregistermulti(register, valuearray[1:]) #Only 3 LSB bytes
        
    def set_bit(self, register, bit_index, state):
        """Write a single bit into a regster, preserving other bits."""
        oldvalue = self.device.readregister(register)
        if state:
            newvalue = oldvalue | 2 ** bit_index
        else:
            newvalue = oldvalue & ~(2 ** bit_index)
        
        self.device.writeregister(register, newvalue)
        
    def get_bit(self, register, bit_index):
        """Read boolean of single bit."""
        return (self.device.readregister(register) & (2 ** bit_index)) > 0
        
    def verify_connection(self):
        """Return true if connected device is valid."""
        return self.device.verify_connection()
        
    def write_debug(self, index, value):
        """Write 4-bit value into debug index."""
        if index == 1:
            currentvalue = self.device.readregister(1022)
            newvalue = currentvalue & 15
            newvalue = newvalue | (value << 4)
            self.device.writeregister(1022, newvalue)
        elif index == 2:
            currentvalue = self.device.readregister(1022)
            newvalue = currentvalue & 240
            newvalue = newvalue | (value)
            self.device.writeregister(1022, newvalue)
        elif index == 3:
            currentvalue = self.device.readregister(1023)
            newvalue = currentvalue & 15
            newvalue = newvalue | (value << 4)
            self.device.writeregister(1023, newvalue)
        elif index == 4:
            currentvalue = self.device.readregister(1023)
            newvalue = currentvalue & 240
            newvalue = newvalue | (value)
            self.device.writeregister(1023, newvalue)
        else:
            raise IOError("Index out of range")
        
    def read_string(self, register, length):
        """Read string of length from start register.
        
        :param register: Register to start from
        :type register: int
        :param length: Length of string
        :type length: int
        :rtype string
        """
        return bytearray(self.device.readregistermulti(register, length)).decode()
            
    def read_sfp_identifier(self):
        return self.device.readregister(0)
    
    def read_vendor_name(self):
        return self.read_string(20,16)
    
    def read_vendor_pn(self):
        return self.read_string(40,16)
    
    def read_vendor_rev(self):
        return self.read_string(56,4)
    
    def read_firmware_rev(self):
        return "0x" + '{:01x}'.format(self.device.readregister(997)) + '{:02x}'.format(self.device.readregister(998)) + '{:02x}'.format(self.device.readregister(999))
        
    def read_monitor_voltage(self, index):
        if index < 1 or index > 16:
            raise ValueError
        return self.to_voltage(self.read12bit(598 + 2 * index))
    
    def read_monitor_voltage_adc(self, index):
        if index < 1 or index > 16:
            raise ValueError
        return self.read12bit(598 + 2 * index)
        
    def read_uptime(self):  # 64-bit each unit is 100 ms
        return struct.unpack('!Q', bytearray(self.device.readregistermulti(1008, 8)))[0]
        
    def read_bias_voltage(self):
        return self.to_bias_voltage(self.read_monitor_voltage(1))
        
    def read_laser_temp(self):
        return self.to_celsius(self.read_monitor_voltage(2))

    def read_etalon_temp(self):
        return self.to_celsius(self.read_monitor_voltage(3))

    def read_laser_tec_current(self):
        return self.to_TEC_current(self.read_monitor_voltage(4))

    def read_etalon_tec_current(self):
        return self.to_TEC_current(self.read_monitor_voltage(5))

    def read_ref_power(self):
        return self.read_monitor_voltage(6)

    def read_etalon_power(self):
        return self.read_monitor_voltage(7)

    def read_recieved_power(self):
        return self.to_LIA_receive_power(self.read_monitor_voltage(8))
        
    def read_output_power(self):
        return self.read_monitor_voltage(9)

    def read_mirror1_voltage(self):
        return self.read_monitor_voltage(10)

    def read_laser_phase_voltage(self):
        return self.read_monitor_voltage(11)

    def read_gain_voltage(self):
        return self.read_monitor_voltage(12)
    
    def read_phase1_voltage(self):
        return self.read_monitor_voltage(13)

    def read_mirror2_voltage(self):
        return self.read_monitor_voltage(14)

    def read_soa1_voltage(self):
        return self.read_monitor_voltage(15)

    def read_soa2_voltage(self):
        return self.read_monitor_voltage(16)
        
    def write_averaging_amount(self, monitor, value):
        if value not in [1, 2, 4, 8, 16, 32, 64, 128, 255]:
            raise IOError("Averaging Amount must be power of 2")
            
        if (monitor < 1) | (monitor > 16):
            raise IOError("Monitor number must be 1-16")
            
        self.device.writeregister(639 + monitor, value)
        
    def read_averaging_amount(self, monitor):
        if (monitor < 1) | (monitor > 16):
            raise IOError("Monitor number must be 1-16")
            
        return self.device.readregister(639 + monitor)
    
    def read_laser_tec_alarm(self):
        value = self.device.readregister(585)
        
        if value & 2**1:
            return ALARM_STATUS_RED
        elif value & 2**0:
            return ALARM_STATUS_YELLOW
        else:
            return ALARM_STATUS_GREEN
        
    def read_etalon_tec_alarm(self):
        value = self.device.readregister(586)
        
        if value & 2**1:
            return ALARM_STATUS_RED
        elif value & 2**0:
            return ALARM_STATUS_YELLOW
        else:
            return ALARM_STATUS_GREEN
        
    def read_apc_alarm(self):
        value = self.device.readregister(587)
        
        if value & 2**1:
            return ALARM_STATUS_RED
        elif value & 2**0:
            return ALARM_STATUS_YELLOW
        else:
            return ALARM_STATUS_GREEN
        
    def read_laser_alarm(self):
        value = self.device.readregister(588)
        
        if value & 2**0:
            return ALARM_STATUS_YELLOW
        else:
            return ALARM_STATUS_GREEN
        
    def set_modulator_on(self, state):
        self.set_bit(513, 4, state)
        
    def set_apc_on(self, state):
        self.set_bit(513, 3, state)
        
    def set_laser_on(self, state):
        self.set_bit(513, 2, state)
        
    def set_laser_tec_on(self, state):
        self.set_bit(513, 1, state)
        
    def set_etalon_tec_on(self, state):
        self.set_bit(513, 0, state)
        
    def read_modulator_on(self):
        return self.get_bit(513, 4)
        
    def read_apc_on(self):
        return self.get_bit(513, 3)
        
    def read_laser_on(self):
        return self.get_bit(513, 2)
    
    def read_laser_tec_on(self):
        return self.get_bit(513, 1)
    
    def read_etalon_tec_on(self):
        return self.get_bit(513, 0)
    
    def set_los_hardware_controlled(self, state):
        self.set_bit(578, 0, state)
        
    def read_los_hardware_controlled(self):
        return self.get_bit(578, 0)
    
    def set_differential_output_dac(self, value):
        self.write12bit(580, value)
        
    def read_differential_output_dac(self):
        return self.read12bit(580)
        
    def set_software_los_dac(self, value):
        self.write12bit(582, value)
        
    def read_software_los_dac(self):
        return self.read12bit(582)
    
    def set_laser_apc_dac(self, value):
        self.write12bit(522, value)
    
    def read_laser_apc_dac(self):
        return self.read12bit(522)
    
    def set_laser_apc_min_dac(self, value):
        self.write12bit(524, value)
    
    def read_laser_apc_min_dac(self):
        return self.read12bit(524)
    
    def set_laser_apc_max_dac(self, value):
        self.write12bit(526, value)
    
    def read_laser_apc_max_dac(self):
        return self.read12bit(526)
    
    def set_laser_apc_yellow_dac(self, value):
        self.write12bit(528, value)
    
    def read_laser_apc_yellow_dac(self):
        return self.read12bit(528)
    
    def set_laser_apc_red_dac(self, value):
        self.write12bit(530, value)
    
    def read_laser_apc_red_dac(self):
        return self.read12bit(530)
    
    def set_laser_tec(self, value):
        self.write12bit(534, self.to_adc(self.to_voltage_from_celcius(value)))
        
    def read_laser_tec(self):
        return self.to_celsius(self.to_voltage(self.read12bit(534)))
    
    def set_laser_tec_min(self, value):
        self.write12bit(536, self.to_adc(self.to_voltage_from_celcius(value)))
        
    def read_laser_tec_min(self):
        return self.to_celsius(self.to_voltage(self.read12bit(536)))
    
    def set_laser_tec_max(self, value):
        self.write12bit(538, self.to_adc(self.to_voltage_from_celcius(value)))
        
    def read_laser_tec_max(self):
        return self.to_celsius(self.to_voltage(self.read12bit(538)))
    
    def set_laser_tec_yellow(self, value):
        self.write12bit(540, self.to_adc(-(self.to_voltage_from_celcius(value) - self.to_voltage_from_celcius(0))))
        
    def read_laser_tec_yellow(self):
        return -(self.to_celsius(self.to_voltage(self.read12bit(540)) + self.to_voltage_from_celcius(0)))
    
    def set_laser_tec_red(self, value):
        self.write12bit(542, self.to_adc(-(self.to_voltage_from_celcius(value) - self.to_voltage_from_celcius(0))))
        
    def read_laser_tec_red(self):
        return -(self.to_celsius(self.to_voltage(self.read12bit(542)) + self.to_voltage_from_celcius(0)))
    
    def set_laser_tec_time(self, value):
        self.write16bit(544, self.to_time_constant_dac(value))
        
    def read_laser_tec_time(self):
        return self.to_time_constant_display(self.read16bit(544))
    
    def set_laser_tec_gain(self, value):
        self.device.writeregister(546, value)
        
    def read_laser_tec_gain(self):
        return self.device.readregister(546)
    
    def set_laser_tec_phase1(self, value):
        self.device.writeregister(547, value)
        
    def read_laser_tec_phase1(self):
        return self.device.readregister(547)
    
    def set_etalon_tec(self, value):
        self.write12bit(550, self.to_adc(self.to_voltage_from_celcius(value)))
        
    def read_etalon_tec(self):
        return self.to_celsius(self.to_voltage(self.read12bit(550)))
    
    def set_etalon_tec_min(self, value):
        self.write12bit(552, self.to_adc(self.to_voltage_from_celcius(value)))
        
    def read_etalon_tec_min(self):
        return self.to_celsius(self.to_voltage(self.read12bit(552)))
    
    def set_etalon_tec_max(self, value):
        self.write12bit(554, self.to_adc(self.to_voltage_from_celcius(value)))
        
    def read_etalon_tec_max(self):
        return self.to_celsius(self.to_voltage(self.read12bit(554)))
    
    def set_etalon_tec_yellow(self, value):
        self.write12bit(556, self.to_adc(-(self.to_voltage_from_celcius(value) - self.to_voltage_from_celcius(0))))
        
    def read_etalon_tec_yellow(self):
        return -(self.to_celsius(self.to_voltage(self.read12bit(556)) + self.to_voltage_from_celcius(0)))
    
    def set_etalon_tec_red(self, value):
        self.write12bit(558, self.to_adc(-(self.to_voltage_from_celcius(value) - self.to_voltage_from_celcius(0))))
        
    def read_etalon_tec_red(self):
        return -(self.to_celsius(self.to_voltage(self.read12bit(558)) + self.to_voltage_from_celcius(0)))
    
    def set_etalon_tec_time(self, value):
        self.write16bit(560, self.to_time_constant_dac(value))
        
    def read_etalon_tec_time(self):
        return self.to_time_constant_display(self.read16bit(560))
    
    def set_etalon_tec_gain(self, value):
        self.device.writeregister(562, value)
        
    def read_etalon_tec_gain(self):
        return self.device.readregister(562)
    
    def set_etalon_tec_phase1(self, value):
        self.device.writeregister(563, value)
        
    def read_etalon_tec_phase1(self):
        return self.device.readregister(563)
    
    def set_laser_max_current(self, value):
        self.write12bit(564, self.to_output_current_dac(value))
        
    def read_laser_max_current(self):
        return self.to_output_current(self.read12bit(564))

    def set_laser_tec_coeff_a(self, value):
        self.to16bit2s(568, int(value))        

    def read_laser_tec_coeff_a(self):
        return self.from16bit2s(568)

    def set_laser_tec_coeff_b(self, value):
        self.to16bit2s(570, int(value)) 
        
    def read_laser_tec_coeff_b(self):
        return self.from16bit2s(570)

    def set_laser_tec_coeff_c(self, value):
        self.to16bit2s(572, int(value)) 
        
    def read_laser_tec_coeff_c(self):
        return self.from16bit2s(572)

    def set_laser_tec_coeff_d(self, value):
        self.to16bit2s(574, int(value)) 
        
    def read_laser_tec_coeff_d(self):
        return self.from16bit2s(574)        
 
    def set_etalon_max_current(self, value):
        self.write12bit(566, self.to_output_current_dac(value))
        
    def read_etalon_max_current(self):
        return self.to_output_current(self.read12bit(566))
    
    def write_mzm1_bias(self, value):
        self.write12bit(672, self.to_adc(value * -1, 5))
         
    def read_mzm1_bias(self):
        return self.to_voltage(self.read12bit(672), 5) * -1
         
    def write_mzm2_bias(self, value):
        self.write12bit(674, self.to_adc(value * -1, 5))
         
    def read_mzm2_bias(self):
        return self.to_voltage(self.read12bit(674), 5) * -1
         
    def write_chirp(self, value):
        self.write16bit(676, value)
         
    def read_chirp(self):
        return self.read16bit(676)
         
    def write_mzm1_drive(self, value):
        self.write12bit(678, self.to_adc(self.to_voltage_from_mzm_drive(value), 5))
     
    def read_mzm1_drive(self):
        return self.to_mzm_drive_voltage(self.to_voltage(self.read12bit(678), 5))
    
#     def read_firmware_rev(self, index):
#         if index < 1 or index > 4 or int(index) != index:
#             raise IndexError("Firmware Rev Invalid Index")
#         
#         return self.device.readregister(995 + index)
    
    def read_firmware_timestamp(self):
        valuearray = bytearray()
        for i in range(992, 996):
            valuearray.append(self.device.readregister(i))
         
        return struct.unpack('!i', valuearray)[0]
    
    def write_table_mzm1_bias(self, value):
        self.write12bit(740, self.to_adc(value * -1, 5))
        
    def read_table_mzm1_bias(self):
        return self.to_voltage(self.read12bit(740), 5) * -1
    
    def write_table_mzm2_bias(self, value):
        self.write12bit(742, self.to_adc(value * -1, 5))
        
    def read_table_mzm2_bias(self):
        return self.to_voltage(self.read12bit(742), 5) * -1
    
    def write_table_mzm1_drive(self, value):
        self.write12bit(744, self.to_adc(self.to_voltage_from_mzm_drive(value), 5))
        
    def read_table_mzm1_drive(self):
        return self.to_mzm_drive_voltage(self.to_voltage(self.read12bit(744), 5))
    
    def write_table_mzm2_drive(self, value):
        self.write12bit(746, self.to_adc(self.to_voltage_from_mzm_drive(value), 5))
        
    def read_table_mzm2_drive(self):
        return self.to_mzm_drive_voltage(self.to_voltage(self.read12bit(746), 5))
    
    def write_table_mzm_delay(self, value):
        self.write12bit(748, value)
        
    def read_table_mzm_delay(self):
        return self.read12bit(748)
    
    def write_table_chirp(self, value):
        self.write16bit(750, value)
        
    def read_table_chirp(self):
        return self.read16bit(750)
    
    def write_table_index(self, value):
        self.device.writeregister(725, value)
        
    def read_table_index(self):
        self.device.readregister(725)
        
    def set_table_read(self, value):
        self.set_bit(724, 7, value)
        
    def write_wavelength(self, value):
        self.write_wavelength_LSB(value)
        self.write_wavelength_MSB(0)
        
    def write_wavelength_MSB(self, value):
        self.device.writeregister(60, value)
        
    def write_wavelength_LSB(self, value):
        self.device.writeregister(61, value)
        
    def write_table_offset(self, value):
        self.device.writeregister(755, value)
        
    def read_table_offset(self):
        return self.device.readregister(755)
    
    def read_table_bytes(self): # Reads entire 32-bytes from wavelength table and outputs as raw bytes
        return bytes(self.device.readregistermulti(724, 32))
    
    def write_table_bytes(self, bytes): # Writes the last 30-bytes to the wavelength table, first two bytes are control bytes
        self.device.writeregistermulti(726, bytes)
    
    def non_persistence(self, value):
        self.set_bit(986, 0, value)

    
    def flash_check_busy(self):
        return self.get_bit(976, 7)
    
    def flash_enable_direct_control(self, value):
        self.set_bit(976, 6, value)
        
    def flash_trigger_readwrite(self, value):
        self.set_bit(976, 1, value)
        
    def flash_set_read(self, value):
        self.set_bit(976, 0, value)
        
    def flash_write_address(self, value):
        self.write24bit(977, value)
        
    def flash_write_byte(self, value):
        self.device.writeregister(984, value)
        
    def flash_read_byte(self):
        return self.device.readregister(984)
        
    def flash_write(self, values):
        for value in values:
            self.flash_write_byte(value)
            
    def flash_read(self, length):
        output = []
        for i in range(length):
            output.append(self.flash_read_byte())
        return output
    
    def read_laser_tec_power(self, pic_power, tec_current = None):
        if tec_current == None:
            current = self.read_laser_tec_current() / 1000
        else:
            current = tec_current / 1000
        voltage = -0.4833 * (current ** 2) + 3.3563 * current + (pic_power / 1000)
        return voltage * current
    
    def read_rx_los(self):
        return self.get_bit(599, 0)
    
    def read_rx_los_sw(self):
        return self.get_bit(599, 2)
    
    def read_rx_los_hw(self):
        return self.get_bit(599, 1)
    
    def reload_wavelength(self):
        self.set_bit(512, 7, True)
        
    def reload_i2c_registers(self):
        self.set_bit(512, 6, True)
        
    def soft_reset(self):
        self.set_bit(512, 0, True)
        self.set_bit(512, 0, False)
        
    def set_locker_on(self, state):
        self.set_bit(513, 5, state)
        
    def read_locker_on(self):
        return self.get_bit(513, 5)
        
# Conversion Formulas
    
    def to_voltage(self, adc_value, adc_voltage_max = None):
        if adc_voltage_max is None:
            adc_voltage_max = self.voltage_max
        return (adc_value / ((2 ** 12) - 1)) * adc_voltage_max
        
    def to_adc(self, voltage, adc_voltage_max = None):
        if adc_voltage_max is None:
            adc_voltage_max = self.voltage_max
        return int((voltage / adc_voltage_max) * ((2 ** 12) - 1))
    
    def to_bias_voltage(self, adc_voltage):
        return adc_voltage * (11/10)
    
#     def to_celsius_other_temp_nonlinear(self, adc_value):
#         RESISTOR_DIV = 10000
#         
#         voltage = self.to_voltage(self, adc_value)
#         resistance = RESISTOR_DIV / ((3.3 / voltage) - 1)
#         return 1 / (0.00112516 + (0.000234721098632 * math.log(resistance)) + 0.000000085877049 * (math.log(resistance) ** 3)) - 273.15
    
    def to_celsius_from_adc(self, adc_value):
        return -((30.4165 * self.to_voltage(adc_value)) - 74)
    
    def to_celsius(self, voltage):
        return -((30.4165 * voltage) - 74)
    
    def to_voltage_from_celcius(self, degrees_celsius):
        return (74 - degrees_celsius) / 30.4165
           
    def to_adc_from_celcius(self, degrees_celsius):
        return self.to_adc((74 - degrees_celsius) / 30.4165)
    
    def to_TEC_current(self, voltage):
        return (1250 * voltage) - 1875
        
    def to16bit2s(self,register, num):
        #Max Positive number 32767  0b0111111111111111
        #Max Negative number -32768 0b1000000000000000
        to2s = 0
        to2sp = 5
        
        if(num < 0):
          #it is negative
          to2s = 65535 + 1 + num
        else:
          #it is positive
          to2s = num

        byte_bits = bin(to2s)
        bit_len = len(byte_bits)      
        bits = "0b"

        if(to2s < 256):
            byte1 = 0 #this number is less than 8 bits
            byte2 = num                    
        else:        
            byte2 = int(byte_bits[(bit_len-8):bit_len],2)
            if(bit_len < 18):       
                for i in range(18 - bit_len):
                    #pad with zeros
                    bits+="0"
            bits += byte_bits[2:(bit_len-8)]
            byte1 = int(bits,2)
        
        self.device.writeregistermulti(register, [byte1, byte2])
    
    def from16bit2s(self,register):
        bytes = self.device.readregistermulti(register,2)
    
        bits = "0b"
        
        #setup first byte
        byte1_bits = bin(bytes[0])
        bit_len = len(byte1_bits)
        if(bit_len < 10):
          for i in range(10 - bit_len):
            #pad with zeros
            bits+="0"
            
          bits+=byte1_bits[2:bit_len]       
        else:   
          bits+=byte1_bits[2:10]
        
        #setup second byte
        byte2_bits = bin(bytes[1])
        bit_len = len(byte2_bits)
        if(bit_len < 10):
          for i in range(10 - bit_len):
            #pad with zeros
            bits+="0"
            
          bits+=byte2_bits[2:bit_len]     
        else:   
          bits+=byte2_bits[2:10]
        
        if(bytes[0] > 127):
          #it is a negative number
          return int(bits,2) - 65536
        else:
          return int(bits,2)
    
    def to_LIA_receive_power(self, voltage):
        voltage = round(voltage, 1)
        if voltage <= 1.1:
            return 0
        elif voltage == 1.2:
            return 60
        elif voltage == 1.3:
            return 90
        elif voltage == 1.4:
            return 120
        elif voltage == 1.5:
            return 140
        elif voltage == 1.6:
            return 160
        elif voltage == 1.7:
            return 195
        elif voltage == 1.8:
            return 230
        elif voltage == 1.9:
            return 260
        elif voltage == 2.0:
            return 295
        elif voltage == 2.1:
            return 330
        elif voltage == 2.2:
            return 400
        elif voltage == 2.3:
            return 420
        else:
            return 500
    
    def to_time_constant_display(self, dac_value):
        return dac_value / 10
    
    def to_time_constant_dac(self, display_value):
        return int(display_value * 10)
    
    def to_output_current_dac(self, current):
        return int(((((0.9 * current) + 1500) / 2500) * (4096)) - 1 - 2456)
    
    def to_output_current(self, dac_value):
        return ((((dac_value + 1 + 2456) / 4096) * 2500) - 1500) / .9
    
    def to_mzm_drive_voltage(self, voltage):
        mzm_voltage = (voltage * 2) - 7
        if 1 <= mzm_voltage <= 3:
            return mzm_voltage
        else:
            raise(ValueError)
    
    def to_voltage_from_mzm_drive(self, mzm_voltage):
        if 1 <= mzm_voltage <= 3:
            return (mzm_voltage + 7) / 2
        else:
            raise(ValueError)
        
    def to_internal_current_section2(self, display_current):
        #This is a quadratic fit, which isn't a great choice, but I could not find a better fit offhand
#         QUADFITCOEF = [ 0.00113462, -0.03498741,  0.45293333]
#         return QUADFITCOEF[0] * (display_current ** 2) + QUADFITCOEF[1] * display_current + QUADFITCOEF[2]
        return ((numpy.exp((display_current-45)/27)-0.121)/0.9)
    
    def to_display_current_section2(self, internal_current):
#         QUADFITCOEF = [ 0.00113462, -0.03498741,  0.45293333]
#         disc = (QUADFITCOEF[1] ** 2) - (4 * QUADFITCOEF[0] * (QUADFITCOEF[2] - internal_current))
#         if disc > 0:
#             return (-QUADFITCOEF[1] + numpy.sqrt(disc)) / (2 * QUADFITCOEF[0])
#         else:
#             return 0
        if (0.9 * internal_current + 0.121) > 0:
            return max((27 * numpy.log(0.9 * internal_current+0.121) + 45), 0)
        else:
            return 0
        
    def to_power_microamps(self, voltage):
        return (voltage * 50)
    
    def to_voltage_from_power_microamps(self, current):
        return (current / 50)
       
    class SerialPortException(Exception):  # Just so we can handle this specific exception
        pass
    
    class LaserSection():
        
        def __init__(self, 
                     testrig, 
                     current_register, 
                     voltage_monitor, 
                     max_current, 
                     table_register, 
                     max_current_register, 
                     dithering_register, 
                     time_constant_register, 
                     to_display_current = lambda x: x, 
                     to_internal_current = lambda x: x):
            self.register = current_register
            self.testrig = testrig
            self.monitor = voltage_monitor
            self.max_current_dac = max_current # Current out if DAC is maxed, used for conversion
            self.table_register = table_register
            self.max_current_register = max_current_register
            self.dithering_register = dithering_register
            self.time_constant_register = time_constant_register
            self.to_display_current = to_display_current
            self.to_internal_current = to_internal_current
            
            #self.validator = QtGui.QDoubleValidator()
            self.validator = StrictDoubleValidator()
            self.validator.setBottom(0)
            self.validator.setTop(self.read_max_current())
            self.validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
            
            # For use in the current maximums windows. This validator should not be modified.
            self.max_validator = StrictDoubleValidator()
            self.max_validator.setBottom(0)
            self.max_validator.setTop(self.max_current_dac)
            self.max_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
            
        def write_current(self, value):
            if value > self.validator.top():
                raise IOError("Current over maximum set")
            self.testrig.write14bit(self.register, self.to_dac(self.to_internal_current(value)))
            
        def write_current_dac(self, value):
            self.write_current(self.from_dac(value))
            
        def read_current(self):
            return self.to_display_current(self.from_dac(self.testrig.read14bit(self.register)))
        
        def read_current_dac(self):
            return self.to_dac(self.read_current())
        
        def read_voltage(self):
            return self.testrig.read_monitor_voltage(self.monitor)
        
        def read_voltage_adc(self):
            return self.testrig.to_adc(self.testrig.read_monitor_voltage(self.monitor))
        
        def to_dac(self, value):
            return int((value / self.max_current_dac) * 16383)
        
        def from_dac(self, value):
            return (value / 16383) * self.max_current_dac
        
        def write_table_current(self, value):
            self.testrig.write14bit(self.table_register, self.to_dac(self.to_internal_current(value)))
        
        def write_table_dac(self, value):
            self.write_table_current(self.from_dac(value))
            
        def read_table_current(self):
            return self.to_display_current(self.from_dac(self.testrig.read14bit(self.table_register)))
            
        def read_table_dac(self):
            return self.to_dac(self.read_table_current())
        
        def read_max_current(self):
            return self.to_display_current(self.from_dac(self.testrig.read14bit(self.max_current_register)))
        
        def write_max_current(self, value):
            self.testrig.write14bit(self.max_current_register, self.to_dac(self.to_internal_current(value)))
            
        def read_dithering(self):
            if self.dithering_register != None:
                return self.from_dac(self.testrig.read14bit(self.dithering_register))
            else:
                raise IOError("Laser Section does not have a dithering value")
        
        def write_dithering(self, value):
            if self.dithering_register != None:
                self.testrig.write14bit(self.dithering_register, self.to_dac(value))
            else:
                raise IOError("Laser Section does not have a dithering value")
            
        def read_time_constant(self):
            if self.time_constant_register != None:
                return self.testrig.to_time_constant_display(self.testrig.read14bit(self.time_constant_register))
            else:
                raise IOError("Laser Section does not have a time constant value")
        
        def write_time_constant(self, value):
            if self.time_constant_register != None:
                self.testrig.write14bit(self.time_constant_register, self.testrig.to_time_constant_dac(value))
            else:
                raise IOError("Laser Section does not have a time constant value")
        
    # This class exists to allow the laser section voltage monitors to be read as a single block
    class LaserBlockRead():
        
        def __init__(self, testrig):
            self.testrig = testrig
            blockread = testrig.device.readregistermulti(618, 14)
            
            self.mirror1 = Testrig.BlockLaserSection(testrig, testrig.mirror1.register, testrig.mirror1.monitor, testrig.mirror1.max_current_dac, testrig.mirror1.table_register, testrig.mirror1.max_current_register, testrig.mirror1.dithering_register, testrig.mirror1.time_constant_register, testrig.mirror1.to_internal_current, testrig.mirror1.to_display_current, blockread)
            self.laser_phase = Testrig.BlockLaserSection(testrig, testrig.laser_phase.register, testrig.laser_phase.monitor, testrig.laser_phase.max_current_dac, testrig.laser_phase.table_register, testrig.laser_phase.max_current_register, testrig.laser_phase.dithering_register, testrig.laser_phase.time_constant_register, testrig.laser_phase.to_internal_current, testrig.laser_phase.to_display_current, blockread)
            self.gain = Testrig.BlockLaserSection(testrig, testrig.gain.register, testrig.gain.monitor, testrig.gain.max_current_dac, testrig.gain.table_register, testrig.gain.max_current_register, testrig.gain.dithering_register, testrig.gain.time_constant_register, testrig.gain.to_internal_current, testrig.gain.to_display_current, blockread)
            self.phase1 = Testrig.BlockLaserSection(testrig, testrig.phase1.register, testrig.phase1.monitor, testrig.phase1.max_current_dac, testrig.phase1.table_register, testrig.phase1.max_current_register, testrig.phase1.dithering_register, testrig.phase1.time_constant_register, testrig.phase1.to_internal_current, testrig.phase1.to_display_current, blockread)
            self.mirror2 = Testrig.BlockLaserSection(testrig, testrig.mirror2.register, testrig.mirror2.monitor, testrig.mirror2.max_current_dac, testrig.mirror2.table_register, testrig.mirror2.max_current_register, testrig.mirror2.dithering_register, testrig.mirror2.time_constant_register, testrig.mirror2.to_internal_current, testrig.mirror2.to_display_current, blockread)
            self.soa1 = Testrig.BlockLaserSection(testrig, testrig.soa1.register, testrig.soa1.monitor, testrig.soa1.max_current_dac, testrig.soa1.table_register, testrig.soa1.max_current_register, testrig.soa1.dithering_register, testrig.soa1.time_constant_register, testrig.soa1.to_internal_current, testrig.soa1.to_display_current, blockread)
            self.soa2 = Testrig.BlockLaserSection(testrig, testrig.soa2.register, testrig.soa2.monitor, testrig.soa2.max_current_dac, testrig.soa2.table_register, testrig.soa2.max_current_register, testrig.soa2.dithering_register, testrig.soa2.time_constant_register, testrig.soa2.to_internal_current, testrig.soa2.to_display_current, blockread)
        
    class BlockLaserSection(LaserSection):
        def __init__(self, testrig, current_register, voltage_monitor, max_current, table_register, max_current_register, dithering_register, time_constant_register, to_internal_current, to_display_current, blockread):
            self.blockread = blockread
            super().__init__(testrig, current_register, voltage_monitor, max_current, table_register, max_current_register, dithering_register, time_constant_register, to_internal_current, to_display_current)
        
        def read_voltage(self):
            arrayindex = (self.monitor * 2) - 20
            return self.testrig.to_voltage(struct.unpack('!H', bytearray(self.blockread[arrayindex:(arrayindex + 2)]))[0] & ((2 ** 12) - 1))
    
        def read_voltage_adc(self):
            arrayindex = (self.monitor * 2) - 20
            return struct.unpack('!H', bytearray(self.blockread[arrayindex:(arrayindex + 2)]))[0] & ((2 ** 12) - 1)  # Convert to short and discard first four bits
        
def sfp_string(value):
    if value == 0:
        return 'Unspecified'
    elif value == 1:
        return 'GBIC'
    elif value == 2:
        return 'Module Soldered to Motherboard'
    elif value == 3:
        return 'SFP+'
    elif value == 4:
        return '300 pin XBI'
    elif value == 5:
        return 'Xenpak'
    elif value == 6:
        return 'XFP'
    elif value == 7:
        return 'XFF'
    elif value == 8:
        return 'XFP-E'
    elif value == 9:
        return 'XPak'
    elif value == 10:
        return 'X2'
    elif value == 11:
        return 'DWDM-SFP'
    elif value == 12:
        return 'QSFP'
    elif 13 <= value <= 127:
        return 'Reserved, Unallocated'
    elif 128 <= value <= 255:
        return 'Vendor Specific'
    else:
        raise IOError("Invalid SFP Identifier")
    
def to_wavelength(index):
    c = 299792458  # Speed of light
    freq = 196.1 * (10 ** 12) - ((index - 1) * .05 * (10 ** 12))
    return c / freq

