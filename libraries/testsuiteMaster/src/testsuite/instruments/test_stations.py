'''
Created on May 29, 2014

@author: bay
'''

#from testsuite.instruments import K2600
from testsuite.instruments import electrodes
from testsuite.instruments import testrig
import time

GAIN1_CURRENT = 150.0
SOA_CURRENT = 50.0
MIRROR_CURRENT = 0.0
LASPHA_CURRENT = 0.0
SOA_VOLTAGE = -1.0
DETECTOR_VOLTAGE = -3.0
PHASE1_CURRENT = 0.0
MOD_VOLTAGE = -2.0
VEE_VOLTAGE = -5.2

class TestStationBase(object):
    def zero_all(self):
        for electrode in self.electrode_list:
            electrode.zero()
            
    def set_output_on_all(self, value):
        for electrode in self.electrode_list:
            electrode.set_output_on(value)
            
class TestStationDC(TestStationBase):
    def __init__(self, output_on_all=True, nplc=None):
        k1 = electrodes.K2600('192.168.1.120')
        k2 = electrodes.K2600('192.168.1.119')
        k3 = electrodes.K2600('192.168.1.118')
        k4 = electrodes.K2600('192.168.1.115')
        k6 = electrodes.K2600('192.168.1.114')
        k7 = electrodes.K2600('192.168.1.113')
        
        self._keithley_list = [k1, k2, k3, k4, k6, k7]
        
        self.gain1 = electrodes.K2600Channel(keithley=k1, 
                                             channel='a', 
                                             short_name='gain1', 
                                             long_name='Gain 1', 
                                             static_current=GAIN1_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=170.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.mirror1 = electrodes.K2600Channel(keithley=k2, 
                                             channel='a', 
                                             short_name='mirror1', 
                                             long_name='Mirror 1', 
                                             static_current=MIRROR_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=70.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.mirror2 = electrodes.K2600Channel(keithley=k2, 
                                             channel='b', 
                                             short_name='mirror2', 
                                             long_name='Mirror 2', 
                                             static_current=MIRROR_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=70.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.phase1 = electrodes.K2600Channel(keithley=k3, 
                                             channel='a', 
                                             short_name='phase1', 
                                             long_name='Phase 1', 
                                             static_current=PHASE1_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=15.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.soa1 = electrodes.K2600Channel(keithley=k4, 
                                             channel='a', 
                                             short_name='soa1', 
                                             long_name='SOA 1', 
                                             static_current=SOA_CURRENT, 
                                             static_voltage=SOA_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=80.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.soa2 = electrodes.K2600Channel(keithley=k4, 
                                             channel='b', 
                                             short_name='soa2', 
                                             long_name='SOA 2', 
                                             static_current=SOA_CURRENT, 
                                             static_voltage=SOA_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=80.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.modulator1 = electrodes.K2600Channel(keithley=k6, 
                                             channel='a', 
                                             short_name='mod1', 
                                             long_name='Modulator 1', 
                                             static_current=None, 
                                             static_voltage=MOD_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=15.0, 
                                             voltage_limit_min=-6.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.VOLTAGE_SOURCE)
        
        self.modulator2 = electrodes.K2600Channel(keithley=k6, 
                                             channel='b', 
                                             short_name='mod2', 
                                             long_name='Modulator 2', 
                                             static_current=None, 
                                             static_voltage=MOD_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=15.0, 
                                             voltage_limit_min=-6.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.VOLTAGE_SOURCE)
        
        self.detector = electrodes.K2600Channel(keithley=k7, 
                                             channel='a', 
                                             short_name='detector', 
                                             long_name='Detector', 
                                             static_current=None, 
                                             static_voltage=DETECTOR_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=10.0, 
                                             voltage_limit_min=-3.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.VOLTAGE_SOURCE)
        
        self.laser_phase = electrodes.K2600Channel(keithley=k7, 
                                             channel='b', 
                                             short_name='laspha', 
                                             long_name='Laser Phase', 
                                             static_current=LASPHA_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=10.0, 
                                             voltage_limit_min=-2.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.electrode_list = self.full_list = [self.gain1, self.mirror1, self.mirror2, self.phase1, self.soa1, self.soa2, self.modulator1, self.modulator2, self.detector, self.laser_phase]
            
        if nplc is not None:
            for electrode in self.electrode_list:
                electrode.write_nplc(nplc)
                
    def close(self):        
        self.zero_all()
        
        self.set_output_on_all(False)
        
        time.sleep(0.05)
            
        for keithley in self._keithley_list:
            keithley.close()
            
class TestStationRF_TOSA(TestStationBase):
    def __init__(self, output_on_all=True):
        smu2 = electrodes.NI414X(2)
        smu3 = electrodes.NI414X(3)
        smu4 = electrodes.NI414X(4)
        smu5 = electrodes.NI414X(5)
        
        self._smu_list = [smu2, smu3, smu4, smu5]
        
        self.gain1 = electrodes.NI414XChannel(smu=smu2, 
                                             channel=0, 
                                             short_name='gain1', 
                                             long_name='Gain 1', 
                                             static_current=GAIN1_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=150.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.mirror1 = electrodes.NI414XChannel(smu=smu2, 
                                             channel=2, 
                                             short_name='mirror1', 
                                             long_name='Mirror 1', 
                                             static_current=MIRROR_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=70.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.mirror2 = electrodes.NI414XChannel(smu=smu2, 
                                             channel=1, 
                                             short_name='mirror2', 
                                             long_name='Mirror 2', 
                                             static_current=MIRROR_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=70.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.phase1 = electrodes.NI414XChannel(smu=smu4, 
                                             channel=0, 
                                             short_name='phase1', 
                                             long_name='Phase 1', 
                                             static_current=PHASE1_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=15.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.phase4 = electrodes.NI414XChannel(smu=smu4, 
                                             channel=1, 
                                             short_name='phase4', 
                                             long_name='Phase 4', 
                                             static_current=PHASE1_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=15.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.soa1 = electrodes.NI414XChannel(smu=smu4, 
                                             channel=2, 
                                             short_name='soa1', 
                                             long_name='SOA 1', 
                                             static_current=SOA_CURRENT, 
                                             static_voltage=SOA_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=80.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.soa2 = electrodes.NI414XChannel(smu=smu4, 
                                             channel=3, 
                                             short_name='soa2', 
                                             long_name='SOA 2', 
                                             static_current=SOA_CURRENT, 
                                             static_voltage=SOA_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=80.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.modulator1 = electrodes.NI414XChannel(smu=smu5, 
                                             channel=1, 
                                             short_name='mod1', 
                                             long_name='Modulator 1', 
                                             static_current=None, 
                                             static_voltage=MOD_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=15.0, 
                                             voltage_limit_min=-6.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.VOLTAGE_SOURCE)
        
        self.modulator2 = electrodes.NI414XChannel(smu=smu5, 
                                             channel=0, 
                                             short_name='mod2', 
                                             long_name='Modulator 2', 
                                             static_current=None, 
                                             static_voltage=MOD_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=15.0, 
                                             voltage_limit_min=-6.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.VOLTAGE_SOURCE)
        
        self.detector = electrodes.NI414XChannel(smu=smu5, 
                                             channel=2, 
                                             short_name='detector', 
                                             long_name='Detector', 
                                             static_current=None, 
                                             static_voltage=DETECTOR_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=10.0, 
                                             voltage_limit_min=-3.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.VOLTAGE_SOURCE)
        
        self.laser_phase = electrodes.NI414XChannel(smu=smu2, 
                                             channel=3, 
                                             short_name='laspha', 
                                             long_name='Laser Phase', 
                                             static_current=LASPHA_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=10.0, 
                                             voltage_limit_min=-2.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        vee1 = electrodes.NI414XChannel(smu=smu3, 
                                             channel=0, 
                                             short_name='vee1', 
                                             long_name='VEE 1', 
                                             static_current=None, 
                                             static_voltage=VEE_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=0.0, 
                                             voltage_limit_min=-5.2, 
                                             voltage_limit_max=0, 
                                             current_compliance=500.0, 
                                             voltage_compliance=None, 
                                             output_on=False, 
                                             output_type=electrodes.VOLTAGE_SOURCE)
        
        vee2 = electrodes.NI414XChannel(smu=smu3, 
                                             channel=1, 
                                             short_name='vee2', 
                                             long_name='VEE 2', 
                                             static_current=None, 
                                             static_voltage=VEE_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=0.0, 
                                             voltage_limit_min=-5.2, 
                                             voltage_limit_max=0, 
                                             current_compliance=500.0, 
                                             voltage_compliance=None, 
                                             output_on=False, 
                                             output_type=electrodes.VOLTAGE_SOURCE)
        
        self.vee = electrodes.LinkedChannel([vee1, vee2], "vee", "VEE")
        
        self.mod_set = electrodes.NI414XChannel(smu=smu3, 
                                             channel=2, 
                                             short_name='modset', 
                                             long_name='MOD SET', 
                                             static_current=None, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=0.0, 
                                             voltage_limit_min=-5.2, 
                                             voltage_limit_max=0, 
                                             current_compliance=50.0, 
                                             voltage_compliance=None, 
                                             output_on=False, 
                                             output_type=electrodes.VOLTAGE_SOURCE)
        
        self.mod_pwc = electrodes.NI414XChannel(smu=smu3, 
                                             channel=3, 
                                             short_name='modpwc', 
                                             long_name='MOD PWC', 
                                             static_current=None, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=0.0, 
                                             voltage_limit_min=-5.2, 
                                             voltage_limit_max=0, 
                                             current_compliance=50.0, 
                                             voltage_compliance=None, 
                                             output_on=False, 
                                             output_type=electrodes.VOLTAGE_SOURCE)
        
        self.electrode_list = [self.gain1, self.mirror1, self.mirror2, self.phase1, self.soa1, self.soa2, self.modulator1, self.modulator2, self.detector, self.laser_phase]
        self.full_list = [self.gain1, self.mirror1, self.mirror2, self.phase1, self.soa1, self.soa2, self.modulator1, self.modulator2, self.detector, self.laser_phase, self.vee, self.mod_set, self.mod_pwc]
        
    def close(self):        
        self.zero_all()
        
        self.set_output_on_all(False)
        
        time.sleep(0.05)
            
        for smu in self._smu_list:
            smu.close()
            
class TestStationRF_COC(TestStationBase):
    def __init__(self, output_on_all=True):
        smu2 = electrodes.NI414X(2)
        smu3 = electrodes.NI414X(3)
        smu4 = electrodes.NI414X(4)
        smu5 = electrodes.NI414X(5)
        
        self._smu_list = [smu2, smu3, smu4, smu5]
        
        self.gain1 = electrodes.NI414XChannel(smu=smu4, 
                                             channel=0, 
                                             short_name='gain1', 
                                             long_name='Gain 1', 
                                             static_current=GAIN1_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=150.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.mirror1 = electrodes.NI414XChannel(smu=smu3, 
                                             channel=1, 
                                             short_name='mirror1', 
                                             long_name='Mirror 1', 
                                             static_current=MIRROR_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=50.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.mirror2 = electrodes.NI414XChannel(smu=smu4, 
                                             channel=1, 
                                             short_name='mirror2', 
                                             long_name='Mirror 2', 
                                             static_current=MIRROR_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=50.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.phase1 = electrodes.NI414XChannel(smu=smu4, 
                                             channel=2, 
                                             short_name='phase1', 
                                             long_name='Phase 1', 
                                             static_current=PHASE1_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=15.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.phase2 = electrodes.NI414XChannel(smu=smu3, 
                                             channel=0, 
                                             short_name='phase1', 
                                             long_name='Phase 1', 
                                             static_current=PHASE1_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=15.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.soa1 = electrodes.NI414XChannel(smu=smu4, 
                                             channel=3, 
                                             short_name='soa1', 
                                             long_name='SOA 1', 
                                             static_current=SOA_CURRENT, 
                                             static_voltage=SOA_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=80.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.soa2 = electrodes.NI414XChannel(smu=smu2, 
                                             channel=3, 
                                             short_name='soa2', 
                                             long_name='SOA 2', 
                                             static_current=SOA_CURRENT, 
                                             static_voltage=SOA_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=80.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.modulator1 = electrodes.NI414XChannel(smu=smu5, 
                                             channel=1, 
                                             short_name='mod1', 
                                             long_name='Modulator 1', 
                                             static_current=None, 
                                             static_voltage=MOD_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=15.0, 
                                             voltage_limit_min=-6.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.VOLTAGE_SOURCE)
        
        self.modulator2 = electrodes.NI414XChannel(smu=smu2, 
                                             channel=1, 
                                             short_name='mod2', 
                                             long_name='Modulator 2', 
                                             static_current=None, 
                                             static_voltage=MOD_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=15.0, 
                                             voltage_limit_min=-6.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.VOLTAGE_SOURCE)
        
        self.detector = electrodes.NI414XChannel(smu=smu5, 
                                             channel=3, 
                                             short_name='detector', 
                                             long_name='Detector', 
                                             static_current=None, 
                                             static_voltage=DETECTOR_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=10.0, 
                                             voltage_limit_min=-3.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.VOLTAGE_SOURCE)
        
        self.laser_phase = electrodes.NI414XChannel(smu=smu3, 
                                             channel=2, 
                                             short_name='laspha', 
                                             long_name='Laser Phase', 
                                             static_current=LASPHA_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=10.0, 
                                             voltage_limit_min=-2.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.electrode_list = self.full_list = [self.gain1, self.mirror1, self.mirror2, self.phase1, self.phase2, self.soa1, self.soa2, self.modulator1, self.modulator2, self.detector, self.laser_phase]
        
    def close(self):        
        self.zero_all()
        
        self.set_output_on_all(False)
        
        time.sleep(0.05)
            
        for smu in self._smu_list:
            smu.close()
            
class TestStationDummy(TestStationBase):
    def __init__(self, output_on_all=True):
        
        self.gain1 = electrodes.DummyElectrode(short_name='gain1', 
                                             long_name='Gain 1', 
                                             static_current=GAIN1_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=150.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.mirror1 = electrodes.DummyElectrode(short_name='mirror1', 
                                             long_name='Mirror 1', 
                                             static_current=MIRROR_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=50.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.mirror2 = electrodes.DummyElectrode(short_name='mirror2', 
                                             long_name='Mirror 2', 
                                             static_current=MIRROR_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=50.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.phase1 = electrodes.DummyElectrode(short_name='phase1', 
                                             long_name='Phase 1', 
                                             static_current=PHASE1_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=15.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.soa1 = electrodes.DummyElectrode(short_name='soa1', 
                                             long_name='SOA 1', 
                                             static_current=SOA_CURRENT, 
                                             static_voltage=SOA_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=80.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.soa2 = electrodes.DummyElectrode(short_name='soa2', 
                                             long_name='SOA 2', 
                                             static_current=SOA_CURRENT, 
                                             static_voltage=SOA_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=80.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.modulator1 = electrodes.DummyElectrode(short_name='mod1', 
                                             long_name='Modulator 1', 
                                             static_current=None, 
                                             static_voltage=MOD_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=15.0, 
                                             voltage_limit_min=-6.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.VOLTAGE_SOURCE)
        
        self.modulator2 = electrodes.DummyElectrode(short_name='mod2', 
                                             long_name='Modulator 2', 
                                             static_current=None, 
                                             static_voltage=MOD_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=15.0, 
                                             voltage_limit_min=-6.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.VOLTAGE_SOURCE)
        
        self.detector = electrodes.DummyElectrode(short_name='detector', 
                                             long_name='Detector', 
                                             static_current=None, 
                                             static_voltage=DETECTOR_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=10.0, 
                                             voltage_limit_min=-3.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.VOLTAGE_SOURCE)
        
        self.laser_phase = electrodes.DummyElectrode(short_name='laspha', 
                                             long_name='Laser Phase', 
                                             static_current=LASPHA_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=10.0, 
                                             voltage_limit_min=-2.0, 
                                             voltage_limit_max=2.0, 
                                             current_compliance=15.0, 
                                             voltage_compliance=2.7, 
                                             output_on=output_on_all, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.electrode_list = self.full_list = [self.gain1, self.mirror1, self.mirror2, self.phase1, self.soa1, self.soa2, self.modulator1, self.modulator2, self.detector, self.laser_phase]
        
    def close(self):        
        pass
    
class TestStationSFP(TestStationBase):
    def __init__(self, 
                 serial_port, 
                 device_type=testrig.DEVICE_SFP_BREAKOUT):
        self.rig = testrig.Testrig(serial_port, device_type)
        self.rig.set_laser_tec_on(True)
        self.rig.set_etalon_tec_on(True)
        self.rig.set_laser_on(True)
        
        self.gain1 = electrodes.SFPElectrode(testrig_laser_section=self.rig.gain, 
                                             short_name='gain1', 
                                             long_name='Gain 1', 
                                             static_current=GAIN1_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=150.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.mirror1 = electrodes.SFPElectrode(testrig_laser_section=self.rig.mirror1, 
                                             short_name='mirror1', 
                                             long_name='Mirror 1', 
                                             static_current=MIRROR_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=50.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.mirror2 = electrodes.SFPElectrode(testrig_laser_section=self.rig.mirror2, 
                                             short_name='mirror2', 
                                             long_name='Mirror 2', 
                                             static_current=MIRROR_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=50.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.phase1 = electrodes.SFPElectrode(testrig_laser_section=self.rig.phase1, 
                                             short_name='phase1', 
                                             long_name='Phase 1', 
                                             static_current=PHASE1_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=15.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.soa1 = electrodes.SFPElectrode(testrig_laser_section=self.rig.soa1, 
                                             short_name='soa1', 
                                             long_name='SOA 1', 
                                             static_current=SOA_CURRENT, 
                                             static_voltage=SOA_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=80.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.soa2 = electrodes.SFPElectrode(testrig_laser_section=self.rig.soa2, 
                                             short_name='soa2', 
                                             long_name='SOA 2', 
                                             static_current=SOA_CURRENT, 
                                             static_voltage=SOA_VOLTAGE, 
                                             current_limit_min=0.0, 
                                             current_limit_max=80.0, 
                                             voltage_limit_min=-4.0, 
                                             voltage_limit_max=2.0, 
                                             output_type=electrodes.CURRENT_SOURCE)
        
        self.laser_phase = electrodes.SFPElectrode(testrig_laser_section=self.rig.laser_phase, 
                                             short_name='laspha', 
                                             long_name='Laser Phase', 
                                             static_current=LASPHA_CURRENT, 
                                             static_voltage=None, 
                                             current_limit_min=0.0, 
                                             current_limit_max=10.0, 
                                             voltage_limit_min=-2.0, 
                                             voltage_limit_max=2.0, 
                                             output_type=electrodes.CURRENT_SOURCE)
                                             
        self.electrode_list = self.full_list = [self.gain1, self.mirror1, self.mirror2, self.phase1, self.soa1, self.soa2, self.laser_phase]
        
    def read_ref_power(self):
        return self.rig.read_ref_power()
    
    def read_mzm_power(self):
        return self.rig.read_output_power()
    
    def read_etalon_power(self):
        return self.rig.read_etalon_power()
              
    def set_locker_on(self, state):
        self.rig.set_locker_on(state)
        
    def read_laser_phase_time_constant(self):
        return self.rig.laser_phase.read_time_constant() # Units in 100 us
        
    def close(self):
        self.rig.set_laser_tec_on(False)
        self.rig.set_etalon_tec_on(False)
        self.rig.set_laser_on(False)
        
        self.rig.close()