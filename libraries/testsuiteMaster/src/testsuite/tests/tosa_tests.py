'''
Created on Feb 10, 2014

Tests that are run on the TOSA stage, parameterized to be hardware-agnostic.

All data files are expected to have 9 lines of header and a row of column headers.

All wavelength values in nm

All current values in mA

All voltage vales in V
'''
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as ml
import matplotlib.ticker as ticker
import scipy.ndimage as ndimage
import socket
import time
import sys
import os
import scipy.signal
from scipy import stats
from datetime import datetime

from mpl_toolkits.mplot3d import Axes3D
import math as math

from testsuite.instruments import test_stations

DEVICE_TYPE_AQ6331 = 0
DEVICE_TYPE_86120B = 1

# FORMAT_STRING = ".7f"
# FORMAT_STRING_PERCENT = "%.7f"
FORMAT_STRING = ".7E"
FORMAT_STRING_PERCENT = "%.7E"

MIRROR1 = 0
LASER_PHASE = 1
GAIN1 = 2
MIRROR2 = 3
SOA1 = 4
SOA2 = 5
PHASE1 = 6
    
class StopButtonException(Exception):
    pass
        
def check_tec(tec, test_station, max_iter=10):
    """Check if a thermal runaway is detected and exits program if detected.
    
    :param tec: Temperature controller device
    :type tec: testsuite.instruments.LDT5910B.TEC
    :test_station: Initialized test station instance
    :type test_station: testsuite.instruments.test_stations
    """
    if tec is not None:
        while True:
            try:
                if tec.check_cutoff():
                    test_station.close()
                    sys.exit("Thermal Runaway detetcted")
                else:
                    return
            except socket.timeout:
                if iter > max_iter:
                    test_station.close()
                    sys.exit("Thermal Runaway detetcted")
                else:
                    pass
    
def gain_voltage_map(output_filename, 
                     output_img_filename_base, 
                     test_station,  
                     min_current, 
                     max_current, 
                     num_current_steps, 
                     laser_phase_current=0.0, 
                     laser_TEC=None, 
                     record_photocurrents=True, 
                     locker_callback=None, 
                     progress_callback=None):
    #TODO Add plots for SOA1/2 voltage
    """Generate a gain-voltage map.
    
    :param output_filename: Path to output CSV file. Columns: Mirr1_current,Mirr2_current,Gain_voltage,LasPha_current,SOA1_current,SOA2_current,SOA1_voltage,SOA2_voltage
    :type output_filename: str
    :param output_img_filename_base: Path to save 3d plots of Mirror 1 (x), Mirror 2(y), Gain 1 (z), appended with electrode type.
    :type output_img_filename_base: str
    :param test_station: Current device test station I/O
    :type test_station: testsuite.instruments.test_stations
    :param min_current: Minimum current for both mirrors
    :type min_current: float
    :param max_current: Maximum current for both mirrors
    :type max_current: float
    :param num_current_steps: Number of steps to use when sweeping both mirrors
    :type max_current: int
    :param laser_phase_current: Laser Phase current to set during sweep
    :type laser_phase_current: float
    :param laser_TEC: Laser TEC controller, used to monitor laser temp and shutdown if a temp runaway is detected
    :type laser_TEC: testsuite.instruments.LDT5910B.TEC
    :param record_photocurrents: Reverse-bias SOAs and record photocurrents in GV map
    :type record_photocurrents: bool
    :param locker_callback: Function callback to run locker. Must return laser phase value
    :type: locker_callback: function
    :param progress_callback: Function callback to track progress. Has parameters current_progress, max_progress
    :type progress_callback: function
    """
    
    if not os.path.exists(os.path.dirname(output_filename)):
        os.makedirs(os.path.dirname(output_filename))
        
    if not os.path.exists(os.path.dirname(output_img_filename_base)):
        os.makedirs(os.path.dirname(output_img_filename_base))
        
        
        
    test_station.gain1.write_static_current()
    
    if record_photocurrents and locker_callback is not None:
        raise Exception("Cannot record photocurrents and use an etalon locker at the same time")
    
    if record_photocurrents:
        test_station.soa1.write_static_voltage()
        test_station.soa2.write_static_voltage()
        
    if locker_callback is not None:
        test_station.soa1.write_static_current()
        test_station.soa2.write_static_current()
    
    test_station.laser_phase.write_current(laser_phase_current)
    
    # loop voltage as record current in on-chip detector and powermeter
    time.sleep(0.1)
    
    min_current = min_current
    max_current = np.sqrt(max_current)
    current_step = np.sqrt(max_current)/num_current_steps
    
    save_data = []
    
    sqrtMirror1_range = np.arange(min_current, max_current, current_step)
    sqrtMirror2_range = np.arange(min_current, max_current, current_step)
    
    mirror1_range = [x**2 for x in sqrtMirror1_range]
    mirror2_range = [x**2 for x in sqrtMirror2_range]
    
    gain1_voltage = test_station.gain1.read_voltage()
    
    max_progress = len(mirror1_range) * len(mirror2_range)
    progress = 0
    
    for mirror1_current in mirror1_range:
        test_station.mirror1.write_current(mirror1_current)
        for mirror2_current in mirror2_range:
            check_tec(laser_TEC, test_station)
            test_station.mirror2.write_current(mirror2_current)
            time.sleep(0.002)
            if locker_callback is not None:
                laser_phase_current = locker_callback()
            gain1_voltage = test_station.gain1.read_voltage()
            if record_photocurrents:
                soa1_current = test_station.soa1.read_current()
                soa2_current = test_station.soa2.read_current()
            
            #Gain1_voltages.append(Gain1_value)
            save_value = [mirror1_current, mirror2_current, gain1_voltage, laser_phase_current]
            if record_photocurrents:
                save_value.extend([soa1_current, soa2_current, test_station.soa1.static_voltage, test_station.soa2.static_voltage])
            if type(test_station) == test_stations.TestStationSFP:
                save_value.extend([test_station.read_ref_power(), test_station.read_mzm_power(), test_station.read_etalon_power()])
            save_data.append(save_value)
            
            if progress_callback is not None:
                progress += 1
                progress_callback(progress, max_progress)
    
    ## Generate header to save in the file
    h = ""
    for i in range(9):
        h = h + "\n" #Header lines
    h = h + 'Mirr1_current,Mirr2_current,Gain_voltage,LasPha_current'
    if record_photocurrents:
        h = h + ',SOA1_current,SOA2_current,SOA1_voltage,SOA2_voltage'
    if type(test_station) == test_stations.TestStationSFP:
        h = h + ',ref_power,mzm_power,etalon_power'
    
    np.savetxt(output_filename, save_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
    # title=None, x_label=None, y_label=None, z_label=None
    #The list(zip(*save_data))[n] is a wonky, but fast way to take the transpose of a list, letting us extract the n-th column in our dataset
    plot_3d(list(zip(*save_data))[0], list(zip(*save_data))[1], list(zip(*save_data))[2], filename=output_img_filename_base + '_GAIN.png', title='Gain Voltage Map', x_label='Mirror1 current (mA)', y_label='Mirror2 current (mA)', z_label='Gain voltage (V)')
    if record_photocurrents:
        plot_3d(list(zip(*save_data))[0], list(zip(*save_data))[1], list(zip(*save_data))[4], filename=output_img_filename_base + '_SOA1.png', title='SOA1 photo current map', x_label='Mirror1 current (mA)', y_label='Mirror2 current (mA)', z_label='SOA1 photo current (mA)')
        plot_3d(list(zip(*save_data))[0], list(zip(*save_data))[1], list(zip(*save_data))[5], filename=output_img_filename_base + '_SOA2.png', title='SOA2 photo current map', x_label='Mirror1 current (mA)', y_label='Mirror2 current (mA)', z_label='SOA2 photo current (mA)')
        

def minima_finder(input_filename, 
                  output_filename, 
                  mirror1_squared=False, 
                  mirror2_squared=False, 
                  mirror1_linspace=1000, 
                  mirror2_linspace=1000, 
                  gauss1_sigma=None, 
                  gauss2_sigma=50.0, 
                  gauss3_sigma=5.0, 
                  minima_width=1, 
                  plot_minima=True, 
                  output_img_filename=None, 
                  magnitude_section=GAIN1, 
                  debug_filename=None):
    """Generate a list of minima from a gain-voltage sweep file.
    
    :param input_filename: Path to input CSV gain-voltage data. Columns: Mirr1_current,Mirr2_current,Gain_voltage,LasPha_current,SOA1_current,SOA2_current,SOA1_voltage,SOA2_voltage
    :type input_filename: str
    :param output_filename: Path to output CSV file. Columns: Mirr1_current,Mirr2_current,LasPha_current
    :type output_filename: str
    :param mirror1_squared: Square Mirror 1 values before applying filters
    :type mirror1_squared: bool
    :param mirror2_squared: Square Mirror 2 values before applying filters
    :type mirror2_squared: bool
    :param mirror1_linspace: Number of values to form a linspace to fit input data over Mirror 1
    :type mirror1_linspace: int
    :param mirror2_linspace: Number of values to form a linspace to fit input data over Mirror 2
    :type mirror2_linspace: int
    :param gauss1_sigma: Sigma value of first Gaussian filter, low-pass
    :type gauss1_sigma: float
    :param gauss2_sigma: Sigma value of second Gaussian filter, high-pass
    :type gauss2_sigma: float
    :param gauss3_sigma: Sigma value of third Gaussian filter, low-pass
    :type gauss3_sigma: float
    :param minima_width: Radius of values considered to determine local minima, square pattern
    :type minima_width: int
    :param plot_minima: Plot and show minima found on gain-voltage graph
    :type plot_minima: bool
    :param output_img_filename: Path to save plot of minima on gain-voltage graph
    :type output_img_filename: str
    :param magnitude_section: Laser section to find minima on. Use module-level constants
    :type magnitude_section: int
    :param debug_filename: Path to debug output CSV file. Debug data is full linspace data after filters are applied. Value is dependent on parameter magnitude_section. Columns: Mirr1_current,Mirr2_current,value
    :type debug_filename: str
    """
    sweepdata = np.genfromtxt(input_filename, skip_header=9, delimiter=",", names=True)
    
    laser_phase_current = sweepdata["LasPha_current"][0]
        
    if mirror1_squared:
        x = np.sqrt(sweepdata["Mirr1_current"])
    else:
        x = sweepdata["Mirr1_current"]
        
    if mirror2_squared:
        y = np.sqrt(sweepdata["Mirr2_current"])
    else:
        y = sweepdata["Mirr2_current"]
    
    if magnitude_section == GAIN1:
        z = sweepdata["Gain_voltage"]
    elif magnitude_section == SOA1:
        z = sweepdata["SOA1_current"]
    elif magnitude_section == SOA2:
        z = sweepdata["SOA2_current"]
    else:
        raise ValueError("Laser Section" + format(magnitude_section) + " is not valid for minima_finder")
    
    xi = np.linspace(min(x),max(x), mirror1_linspace)
    yi = np.linspace(min(y),max(y), mirror2_linspace)
    zi = ml.griddata(x,y,z,xi,yi)
    
    #Run Gaussian Filters
    
    if gauss1_sigma is not None:
        zi = ndimage.gaussian_filter(zi, sigma=gauss1_sigma, order=0)
        
    if gauss2_sigma is not None:
        gauss = ndimage.gaussian_filter(zi, sigma=gauss2_sigma, order=0)
        zi = np.subtract(zi, gauss)
        
    if gauss3_sigma is not None:
        zi = ndimage.gaussian_filter(zi, sigma=gauss3_sigma, order=0)
        
    #Output debug data
    if debug_filename is not None:
        debug_data = []
        for x_index in range(mirror1_linspace):
            for y_index in range(mirror2_linspace):
                debug_item = []
                debug_item.append(xi[x_index])
                debug_item.append(yi[y_index])
                debug_item.append(zi[x_index][y_index])
                debug_data.append(debug_item)
        h = ""
        for i in range(9):
            h = h + "\n" #Header lines
        h = h + 'Mirr1_current,Mirr2_current,value'
        np.savetxt(debug_filename, debug_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
        
    #Find Minima
    
    # Iterate over each point in the linear space
    array_data = zi
    minima = []
    
    for x in range(mirror1_linspace):
        for y in range(mirror2_linspace):
            if type(array_data[x, y]) == np.ma.core.MaskedConstant or np.isnan(array_data[x, y]):
                continue
            else:
                # Create a sub-array of values to compare against
                sub_array = array_data[max(0, x - minima_width ):min(mirror1_linspace - 1, x + minima_width) + 1,max(0, y - minima_width ):min(mirror2_linspace - 1, y + minima_width) + 1]
                is_minima = True
                for point in sub_array.flatten():
                    if type(point) == np.ma.core.MaskedConstant or np.isnan(point):
                        is_minima = False
                        break
                    elif point < array_data[x, y]:
                        is_minima = False
                        break
                if is_minima:
                    #print(format(xi[x]) + "(" + format(x) + ")," + format(yi[y]) + "(" + format(x) + "):" + format(array_data[y, x]))
                    minima.append([xi[x], yi[y]])
                    
    if plot_minima or output_img_filename is not None:
        plt.close("all")
        plt.figure(1)
        plt.pcolormesh(xi, yi, zi, cmap = plt.get_cmap('gray_r'),vmin=np.ma.min(zi),vmax=np.ma.max(zi))
        plt.xlabel("Mirr1 current (mA)")
        plt.ylabel("Mirr2 current (mA)")
        plt.suptitle("Minima Data", fontsize = 20)
        plt.title(input_filename, fontsize = 12)
        plt.colorbar()
        
        for point in minima:
            plt.plot(point[0],point[1],'o')
            
        if plot_minima:
            plt.show()
            
        if output_img_filename is not None:
            plt.savefig(output_img_filename)
        
        plt.close("all")
            
    else:
        print("Minima detection complete")
            
    #Output minima to file
    
    #output_path = open(output_filename, 'w')
    ## Generate header to save in the file
    h = ""
    for i in range(9):
        h = h + "\n" #Header lines
    h = h + "Mirr1_current,Mirr2_current,LasPha_current"
    save_data = []
    for point in minima:
        if mirror1_squared:
            point[0] = point[0] ** 2
        if mirror2_squared:
            point[1] = point[1] ** 2
        save_data.append([point[0], point[1], laser_phase_current])
    np.savetxt(output_filename, save_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
    

def manual_minima_finder(input_filename, 
                   output_filename, 
                   mirror1_squared=False, 
                   mirror2_squared=False, 
                   mirror1_linspace=1000, 
                   mirror2_linspace=1000, 
                   gauss1_sigma=None, 
                   gauss2_sigma=50.0, 
                   gauss3_sigma=5.0, 
                   output_img_filename=None, 
                   magnitude_section=GAIN1, 
                   debug_filename=None):
    """Generate a list of minima from a gain-voltage sweep file.
    
    :param input_filename: Path to input CSV gain-voltage data. Columns: Mirr1_current,Mirr2_current,Gain_voltage,LasPha_current,SOA1_current,SOA2_current,SOA1_voltage,SOA2_voltage
    :type input_filename: str
    :param output_filename: Path to output CSV file. Columns: Mirr1_current,Mirr2_current,LasPha_current
    :type output_filename: str
    :param mirror1_squared: Square Mirror 1 values before applying filters
    :type mirror1_squared: bool
    :param mirror2_squared: Square Mirror 2 values before applying filters
    :type mirror2_squared: bool
    :param mirror1_linspace: Number of values to form a linspace to fit input data over Mirror 1
    :type mirror1_linspace: int
    :param mirror2_linspace: Number of values to form a linspace to fit input data over Mirror 2
    :type mirror2_linspace: int
    :param gauss1_sigma: Sigma value of first Gaussian filter, low-pass
    :type gauss1_sigma: float
    :param gauss2_sigma: Sigma value of second Gaussian filter, high-pass
    :type gauss2_sigma: float
    :param gauss3_sigma: Sigma value of third Gaussian filter, low-pass
    :type gauss3_sigma: float
    :param minima_width: Radius of values considered to determine local minima, square pattern
    :type minima_width: int
    :param plot_minima: Plot and show minima found on gain-voltage graph
    :type plot_minima: bool
    :param output_img_filename: Path to save plot of minima on gain-voltage graph
    :type output_img_filename: str
    :param magnitude_section: Laser section to find minima on. Use module-level constants
    :type magnitude_section: int
    :param debug_filename: Path to debug output CSV file. Debug data is full linspace data after filters are applied. Value is dependent on parameter magnitude_section. Columns: Mirr1_current,Mirr2_current,value
    :type debug_filename: str
    """
    sweepdata = np.genfromtxt(input_filename, skip_header=9, delimiter=",", names=True)
    
    laser_phase_current = sweepdata["LasPha_current"][0]
        
    if mirror1_squared:
        x = np.sqrt(sweepdata["Mirr1_current"])
    else:
        x = sweepdata["Mirr1_current"]
        
    if mirror2_squared:
        y = np.sqrt(sweepdata["Mirr2_current"])
    else:
        y = sweepdata["Mirr2_current"]
    
    if magnitude_section == GAIN1:
        z = sweepdata["Gain_voltage"]
    elif magnitude_section == SOA1:
        z = sweepdata["SOA1_current"]
    elif magnitude_section == SOA2:
        z = sweepdata["SOA2_current"]
    else:
        raise ValueError("Laser Section" + format(magnitude_section) +  " is not valid for minima_finder")
    
    xi = np.linspace(min(x),max(x), mirror1_linspace)
    yi = np.linspace(min(y),max(y), mirror2_linspace)
    zi = ml.griddata(x,y,z,xi,yi)
    
    #Run Gaussian Filters
    
    if gauss1_sigma is not None:
        zi = ndimage.gaussian_filter(zi, sigma=gauss1_sigma, order=0)
        
    if gauss2_sigma is not None:
        gauss = ndimage.gaussian_filter(zi, sigma=gauss2_sigma, order=0)
        zi = np.subtract(zi, gauss)
        
    if gauss3_sigma is not None:
        zi = ndimage.gaussian_filter(zi, sigma=gauss3_sigma, order=0)
        
    #Output debug data
    if debug_filename is not None:
        debug_data = []
        for x_index in range(mirror1_linspace):
            for y_index in range(mirror2_linspace):
                debug_item = []
                debug_item.append(xi[x_index])
                debug_item.append(yi[y_index])
                debug_item.append(zi[x_index][y_index])
                debug_data.append(debug_item)
        h = ""
        for i in range(9):
            h = h + "\n" #Header lines
        h = h + 'Mirr1_current,Mirr2_current,value'
        np.savetxt(debug_filename, debug_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
        
    #Find Minima
    def on_click(event):
        #print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(event.button, event.x, event.y, event.xdata, event.ydata)
        plt.plot(event.xdata, event.ydata, 'o')
        plt.show()
        minima.append([event.xdata, event.ydata])
    
    minima = []
    
    plt.close("all")
    fig = plt.figure(1)
    plt.pcolormesh(xi, yi, zi, cmap = plt.get_cmap('gray_r'),vmin=np.ma.min(zi),vmax=np.ma.max(zi))
    plt.xlabel("Mirr1 current (mA)")
    plt.ylabel("Mirr2 current (mA)")
    plt.suptitle("Minima Data", fontsize = 20)
    plt.title(input_filename, fontsize = 12)
    plt.colorbar()
    fig.canvas.mpl_connect('button_press_event', on_click)
    plt.show()
    
    if output_img_filename is not None:
        plt.close("all")
        fig = plt.figure(1)
        plt.pcolormesh(xi, yi, zi, cmap = plt.get_cmap('gray_r'),vmin=np.ma.min(zi),vmax=np.ma.max(zi))
        plt.xlabel("Mirr1 current (mA)")
        plt.ylabel("Mirr2 current (mA)")
        plt.suptitle("Minima Data", fontsize = 20)
        plt.title(input_filename, fontsize = 12)
        plt.colorbar()
        for point in minima:
            plt.plot(point[0],point[1],'o')
        plt.savefig(output_img_filename)
    
    plt.close("all")
            
    #Output minima to file
    
    #output_path = open(output_filename, 'w')
    ## Generate header to save in the file
    h = ""
    for i in range(9):
        h = h +  "\n" #Header lines
    h = h +  "Mirr1_current,Mirr2_current,LasPha_current"
    save_data = []
    for point in minima:
        if mirror1_squared:
            point[0] = point[0] ** 2
        if mirror2_squared:
            point[1] = point[1] ** 2
        save_data.append([point[0], point[1], laser_phase_current])
    np.savetxt(output_filename, save_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
  

def wavelength_finder(input_filename, #Add sorting to make sure lowest current value is chosen if multiple values can fit into one slot
                      output_filename, 
                      wavemeter, 
                      test_station, 
                      laser_TEC=None):
    """Scan OSA to find primary and secondary peak values for each minima in input data.
    
    :param input_filename: Path to input CSV minima data. Columns: Mirr1_current,Mirr2_current,LasPha_current
    :type input_filename: str
    :param output_filename: Path to output CSV file. Columns: Mirr1_current,Mirr2_current,LasPha_current,peak1_wavelength,peak1_power,peak2_wavelength,peak2_power
    :type output_filename: str
    :param wavemeter: Initialized wavemeter to perform wavelength/power sweeps on
    :type wavemeter: testsuite.instruments.AQ6331.OSA or testsuite.instruments.HP86120B.OSA
    :param test_station: Initialized test station
    :type test_station: testsuite.instruments.test_stations
    :param laser_TEC: Laser TEC controller, used to monitor laser temp and shutdown if a temp runaway is detected
    :type laser_TEC: testsuite.instruments.LDT5910B.TEC
    """    
    minima_data = np.genfromtxt(input_filename, skip_header=9, delimiter=",", names=True)
    
    laser_phase_current = minima_data["LasPha_current"][0]
    test_station.zero_all()
    test_station.gain1.write_static_current()
    test_station.soa1.write_static_current()
    test_station.soa2.write_static_current()
    
    while True:
        try:
            wavemeter.writesweepstart(1525)
            wavemeter.writesweepstop(1565)
            wavemeter.writeresolution(0.05)
            break
        except socket.timeout:
            print("wavelengh_finder timeout 1")
            pass # Loop through peak finder again
        
    save_data = []
    
    ## Generate header to save in the file
    h = ""
    for i in range(9):
        h = h + "\n" #Header lines
    h = h + "Mirr1_current,Mirr2_current,LasPha_current,peak1_wavelength,peak1_power,peak2_wavelength,peak2_power"
    
    for minima in minima_data:
        peakfound = False
        while not peakfound:
            #try:
                check_tec(laser_TEC, test_station)
                test_station.mirror1.write_current(float(minima["Mirr1_current"]))
                test_station.mirror2.write_current(float(minima["Mirr2_current"]))

                time.sleep(0.01)
                wavemeter.startsweep()
                
                peaks = wavemeter.readpeak()
                #print(peaks)
                data = []
                data.append(minima["Mirr1_current"])
                data.append(minima["Mirr2_current"])
                data.append(laser_phase_current)
                if len(peaks) > 0:
                    data.append(peaks[0]["wavelength"])
                    data.append(peaks[0]["power"])
                else:
                    data.append(0)
                    data.append(-100)
                if len(peaks) > 1:
                    data.append(peaks[1]["wavelength"])
                    data.append(peaks[1]["power"])
                else:
                    data.append(0)
                    data.append(-100)
                save_data.append(data)
                    
                peakfound = True
#            except socket.timeout:
#                print("wavelengh_finder timeout 2")
#                pass # Loop through peak finder again
            
    np.savetxt(output_filename, save_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
    
def generate_blank_itu(output_filename, 
                       index_list=None):
    """Generate blank itu grid file.
    
    :param output_filename: Path to output CSV file. All current columns filled with -1. Columns: itu_index,itu_wavelength,Mirr1_current,Mirr2_current,LasPha_current
    :type output_filename: str
    :param index_list: List of indices to include. If not defined, will do entire ITU grid.
    :type index_list: List
    """
    h = itu_header()
    
    save_data = []
    if index_list is not None:
        iterator = index_list
    else:
        iterator = range(100)
    for itu_index in iterator:
        datum = []
        datum.append(itu_index)
        datum.append(-1)
        datum.append(-1)
        datum.append(-1)
        datum.append(-1)
        save_data.append(datum)
        
    np.savetxt(output_filename, save_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
    
def crude_itu_grid_fitter(input_filename, 
                          output_filename, 
                          min_smsr=35.0, 
                          max_itu_deviation=0.15, 
                          output_power_minimum=-10.0):
    """Generate crudely fit ITU grid file using minima data with peak values.
    Will pass through partially data already filled, only searching for new values for ITU grid indices not filled.
    
    :param input_filename: Path to input CSV minima with peaks data. Columns: Mirr1_current,Mirr2_current,LasPha_current,peak1_wavelength,peak1_power,peak2_wavelength,peak2_power
    :type input_filename: str
    :param output_filename: Path to output CSV file. Well-formed file must already exist. Columns: itu_index,itu_wavelength,Mirr1_current,Mirr2_current,LasPha_current
    :type output_filename: str
    :param min_smsr: Minimum SMSR to validate a G-V minima
    :type min_smsr: float
    :param max_itu_deviation: Maximum deviation from ITU grid to validate G-V minima
    :type max_itu_deviation: float
    :param output_power_minimum: Minimum peak power to validate G-V minima
    :type output_power_minimum: float
    :return: Number of unmatched ITU grid indices
    :rtype: int
    """
    #output_filename must already exist, with -1 in currents if value has not been found
    data = np.genfromtxt(input_filename, skip_header=9, delimiter=",", names=True)
    data.sort(order=["peak1_wavelength"])
    laser_phase_current = data["LasPha_current"][0]
    
    old_itu = np.genfromtxt(output_filename, skip_header=9, delimiter=",", names=True)
    
    #Generate ITU grid
    #file = open(output_filename, 'w')
    save_data = []
    h = itu_header()
    
    minima_index = 0  # Starting at second element
    unmatched_itu = 0
    for itu_index in old_itu["itu_index"]:
        if old_itu["Mirr1_current"][itu_index] != -1:
            save_data.append([old_itu["itu_index"][itu_index], old_itu["itu_wavelength"][itu_index], old_itu["Mirr1_current"][itu_index], old_itu["Mirr2_current"][itu_index], old_itu["LasPha_current"][itu_index]])
            continue # ITU grid already filled
            
        best_index = None
        while minima_index < len(data):
            if data["peak1_power"][minima_index] < output_power_minimum:
                minima_index += 1
                continue
            elif (data["peak1_power"][minima_index] - data["peak2_power"][minima_index]) < min_smsr:
                minima_index += 1
                continue
            elif itu_wavelength(itu_index) > data["peak1_wavelength"][minima_index]:  # laser wavelength too low
                minima_index += 1
                continue
            elif itu_wavelength(itu_index) - data["peak1_wavelength"][minima_index] < -(max_itu_deviation):  # laser wavelength too high, map cannot be completed
            #elif itu_wavelength(itu_index) < data["peak1_wavelength"][minima_index]:  # laser wavelength too high, map cannot be completed
                break
            else: # Good data point
                if best_index is None or data["peak1_power"][minima_index] > data["peak1_power"][best_index]:
                    best_index = minima_index  
                minima_index += 1
                
        if best_index is None:
            save_data.append([itu_index, itu_wavelength(itu_index), -1, -1, -1])
            unmatched_itu = unmatched_itu + 1
        else:
            save_data.append([itu_index, itu_wavelength(itu_index), data["Mirr1_current"][best_index], data["Mirr2_current"][best_index], laser_phase_current])
    
    np.savetxt(output_filename, save_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
    return unmatched_itu
    
def itu_wavelength(index):
    """Return ITU wavelength from ITU index.
    
    :param index: ITU table index
    :type index: int
    :return: ITU wavelength
    :rtype: float
    """
    freq = 196.1 * (10 ** 12) + index * (-.05 * (10 ** 12))
    c = 299792458
    return (c / freq) * (10 ** 9)

def itu_header():
    """Generate base header to use in ITU grid format CSV files.
    
    :return: Column headers for itu_index,itu_wavelength,Mirr1_current,Mirr2_current,LasPha_current
    :rtype: str
    """
    ## Generate header to save in the file
    h = ""
    for i in range(9):
        h = h + "\n" #Header lines
    h = h + 'itu_index,itu_wavelength,Mirr1_current,Mirr2_current,LasPha_current'
    return h
    
def fine_itu_grid_fitter(input_filename, 
                         output_filename, 
                         test_station, 
                         wavemeter, 
                         laser_phase_max_delta, #Non-inclusive
                         laser_phase_step=.1, 
                         debug_filename=None, 
                         laser_TEC=None):
    #TODO Add another check for SMSR
    """Fine tune wavelength of ITU grid using Laser Phase current.
    
    :param input_filename: Path to input CSV ITU crude data. Columns: itu_index, itu_wavelength, Mirr1_current, Mirr2_current, LasPha_current, peak1_wavelength, peak1_power, peak2_wavelength, peak2_power
    :type input_filename: str
    :param output_filename: Path to output CSV file. Columns: itu_index, itu_wavelength, Mirr1_current, Mirr2_current, LasPha_current
    :type output_filename: str
    :param test_station: Initialized test station
    :type test_station: testsuite.instruments.test_stations
    :param wavemeter: Initialized wavemeter to perform sweeps on
    :type wavemeter: testsuite.instruments.AQ6331.OSA or testsuite.instruments.HP86120B.OSA
    :param laser_phase_max_delta: Maximum of current to sweep laser phase section relative to existing laser_phase_current
    :type laser_phase_max_delta: float
    :param laser_phase_step: Step of current to sweep laser phase section
    :type laser_phase_step: float
    :param debug_filename: Path to output CSV file of all osa/wavemeter measurements. Columns: itu_index,itu_wavelength,Mirr1_current,Mirr2_current,LasPha_currentpeak1_power,peak1_wavelength
    :param debug_filename: str
    :param laser_TEC: Laser TEC controller, used to monitor laser temp and shutdown if a temp runaway is detected
    :type laser_TEC: testsuite.instruments.LDT5910B.TEC
    """
    test_station.zero_all()
    test_station.gain1.write_static_current()
    test_station.soa1.write_static_current()
    test_station.soa2.write_static_current()
    
    while True:
        try:
            wavemeter.writesweepstart(1525)
            wavemeter.writesweepstop(1565)
            wavemeter.writeresolution(0.05)
            break
        except socket.timeout:
            pass # Loop through peak finder again
    
    data = np.genfromtxt(input_filename, skip_header=9, delimiter=",", names=True)
    
    save_data = []
    debug_data = []
    h = itu_header()
    debug_h = h + ",peak1_power,peak1_wavelength"
    
    for itu_index in data["itu_index"]:
        check_tec(laser_TEC, test_station)
        wavelength = itu_wavelength(itu_index)
        if data["Mirr1_current"][itu_index] == -1:
            save_data.append([itu_index, itu_wavelength(itu_index), -1, -1, -1])
            debug_data.append([itu_index, itu_wavelength(itu_index), -1, -1, -1, -1, -1])
        else:
            test_station.mirror1.write_current(data["Mirr1_current"][itu_index])
            test_station.mirror2.write_current(data["Mirr2_current"][itu_index])
            best_laser_phase_current = 0
            best_wavelength_delta = np.inf # Arbitrary high
            for current in np.arange(data["LasPha_current"][itu_index], data["LasPha_current"][itu_index] + laser_phase_max_delta, laser_phase_step):
                test_station.laser_phase.write_current(current)
                while True:
                    try:
                        osa_peaks = wavemeter.readpeak()
                        break
                    except socket.timeout:
                        pass # Loop through peak finder again
                    
                datum = [itu_index, itu_wavelength(itu_index), data["Mirr1_current"][itu_index], data["Mirr2_current"][itu_index], current]
                if len(osa_peaks) == 0:
                    datum.append(-1)
                    datum.append(-1)
                else:
                    datum.append(osa_peaks[0]["wavelength"])
                    datum.append(osa_peaks[0]["power"])
                debug_data.append(datum)
                    
                if len(osa_peaks) == 0:
                    pass
                elif abs(osa_peaks[0]["wavelength"] - wavelength) < best_wavelength_delta:
                    osa_wavelength = osa_peaks[0]["wavelength"]
                    best_laser_phase_current = current
                    best_wavelength_delta = abs(osa_wavelength - wavelength)
            save_data.append([itu_index, itu_wavelength(itu_index), data["Mirr1_current"][itu_index], data["Mirr2_current"][itu_index], best_laser_phase_current])
    np.savetxt(output_filename, save_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
    if debug_filename is not None:
        np.savetxt(debug_filename, debug_data, header = debug_h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
    
def plot_3d(x, 
            y, 
            z, 
            display=False, 
            filename=None, 
            title=None, 
            x_label=None, 
            y_label=None, 
            z_label=None, 
            colormap=plt.get_cmap('gray_r'), 
            min_x=None, 
            max_x=None, 
            min_y=None, 
            max_y=None, 
            min_z=None, 
            max_z=None, 
            linspace_x=200, 
            linspace_y=200):
    """Plot a 3d dataset as color plot.
    
    :param x: X data
    :type x: List
    :param y: Y data
    :type y: List
    :param z: Z data
    :type z: List
    :param display: Show plot in interactive pyPlot window
    :type display: bool
    :param filename: Image filename to save plot at default angle
    :type filename: str
    :param title: Main title of plot
    :param x_label: Label of X axis
    :type x_label: str
    :param y_label: Label of Y axis
    :type y_label: str
    :param z_label: Label of Z axis
    :type z_label: str
    :param colormap: pyPlot colormap to use to plot z data
    :type colormap: matplotlib.cm
    :param min_x: Minimum value to plot X data
    :type min_x: float
    :param max_x: Maximum value to plot X data
    :type max_x: float
    :param min_y: Minimum value to plot Y data
    :type min_y: float
    :param max_y: Maximum value to plot Y data
    :type max_y: float
    :param min_z: Minimum value to plot Z data
    :type min_z: float
    :param max_z: Maximum value to plot Z data
    :type max_z: float
    :param linspace_x: Linear space manginute to fit X axis
    :type linspace_x: int
    :param linspace_y: Linear space manginute to fit Y axis
    :type linspace_y: int
    """
    if min_x is None:
        min_x = min(x)
    if max_x is None:
        max_x = max(x)
    if min_y is None:
        min_y = min(y)
    if max_y is None:
        max_y = max(y)
    if min_z is None:
        min_z = min(z)
    if max_z is None:
        max_z = max(z)
        
    xi = np.linspace(min_x, max_x, linspace_x)
    yi = np.linspace(min_y, max_y, linspace_y)
    zi = ml.griddata(x, y, z, xi, yi)
    
    plt.close("all")
    plt.figure(1)
    plt.pcolormesh(xi, yi, zi, cmap=plt.get_cmap('spectral'), vmin=min_z, vmax=max_z)
    cbar = plt.colorbar()
    
    if title is not None:
        plt.title(title)
    if x_label is not None:
        plt.xlabel(x_label)
    if y_label is not None:
        plt.ylabel(y_label)
    if z_label is not None:
        cbar.ax.set_ylabel(z_label)
    
    if filename is not None:
        plt.savefig(filename)
    if display:
        plt.show()
        
    plt.close("all")
        
def measure_2d_phase_intensity_maximum(test_station, 
                                       power_monitor, 
                                       mirror1_current, 
                                       mirror2_current, 
                                       laser_phase_current, 
                                       soa1_current, 
                                       soa2_current, 
                                       phase_current_start=0.0, 
                                       phase_current_end=15.0, 
                                       phase_current_step=0.1, 
                                       output_filename=None, 
                                       output_img_filename=None, 
                                       stab_time=5.0):
    """Sweep phase1 and phase4 and optimize for maximum output intensity. Return optimal phase values and plot intensity.
    
    This is currently under developement and the function to run this over the ITU grid is not written.
    
    :param test_station: Initialized test station
    :type test_station: testsuite.instruments.test_stations
    :param power_monitor: Power Monitor to measure output intensity
    :type power_monitor: testsuite.instruments.PM100USB.PowerMonitor
    :param mirror1_current: Mirror 1 current while test is run
    :type mirror1_current: float
    :param mirror2_current: Mirror 2 current while test is run
    :type mirror2_current: float
    :param laser_phase_current: Laser Phase current while test is run
    :type laser_phase_current: float
    :param soa1_current: SOA 1 current while test is run
    :type soa1_current: float
    :param soa2_current: SOA 2 current while test is run
    :type soa2_current: float
    :param phase_current_start: Start point for both phase current sweeps
    :type phase_current_start: float
    :param phase_current_end: End point for both phase current sweeps
    :type phase_current_end: float
    :param phase_current_step: Step value for both phase current sweeps
    :type phase_current_step: float
    :param output_filename: Filename to store CSV sweep data. Columns: phase1_current,phase4_current,power_monitor,detector_current
    :type output_filename: str
    :param output_img_filename: Filename to store PNG sweep image
    :type output_img_filename: str
    :param stab_time: Time in seconds to wait after setting currents
    :type stab_time: float
    :return: Current for phase1 and phase4 that maximize output intensity
    :rtype: dict{"phase1","phase4"}
    """
    
    test_station.zero_all()
    test_station.gain1.write_static_current()
    test_station.mirror1.write_current(mirror1_current)
    test_station.mirror2.write_current(mirror2_current)
    test_station.soa1.write_current(soa1_current)
    test_station.soa2.write_current(soa1_current)
    test_station.laser_phase.write_current(laser_phase_current)
    test_station.detector.write_static_voltage()
    
    time.sleep(stab_time)
    
    save_data = []
    for phase1_current in np.arange(phase_current_start, phase_current_end, phase_current_step):
        test_station.phase1.write_current(phase1_current)
        for phase4_current in np.arange(phase_current_start, phase_current_end, phase_current_step):
            test_station.phase4.write_current(phase4_current)
            save_data.append([phase1_current, phase4_current, power_monitor.read_value(), test_station.detector.read_current()])
            
    transpose_data = list(zip(*save_data))
    phase1 = transpose_data[0]
    phase4 = transpose_data[1]
    power_monitor = transpose_data[2]
    
    output = dict()
    output["phase1"] = phase1[np.argmax(power_monitor)]
    output["phase4"] = phase4[np.argmax(power_monitor)]
    
    ## Generate header to save in the file
    t = 'Gain1_current (mA) , ' + str(test_station.gain1.static_current) + \
    '\n Gain2_current (A) , N/A' + \
    '\n Mirror1_current (A), '+ str(mirror1_current) + \
    '\n Mirror2_current (A), '+ str(mirror2_current) + \
    '\n LaserPhase_current (A), '+ str(laser_phase_current) + \
    '\n SOA1_current (A), '+ str(soa1_current) + \
    '\n SOA2_current (A), '+ str(soa2_current) + \
    '\n Detector_voltage (V), '+ str(test_station.detector.static_voltage) + '\n' 
    h = t + 'phase1_current,phase4_current,power_monitor,detector_current'
    
    if output_filename is not None:
        np.savetxt(output_filename, save_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
        
    if output_img_filename is not None:
        plot_3d(x=phase1, 
            y=phase4, 
            z=power_monitor, 
            filename=output_img_filename, 
            title="Phase Intensity", 
            x_label="Phase 1 (mA)", 
            y_label="Phase 4 (mA)", 
            z_label="Power Monitor")
        
    return output

def characterize_MZM_operation_range(test_station, 
                                     power_monitor, 
                                     mirror1_current, 
                                     mirror2_current, 
                                     laser_phase_current, 
                                     soa1_current, 
                                     soa2_current, 
                                     phase1_current, 
                                     phase4_current, 
                                     mod_voltage_start=0.0, 
                                     mod_voltage_end=-6.0, 
                                     mod_voltage_step=-0.1, 
                                     output_filename=None, 
                                     output_img_filename=None, 
                                     stab_time=5.0, 
                                     mzm_operation_voltage_range=2.0):
    """Find the ideal operation range that maximizes extinction ratio when modulating using modulator voltages. This method has variable chirp along the operation range, and is not being used right now.
    
    This is currently under developement and the function to run this over the ITU grid is not written.
    
    :param test_station: Initialized test station
    :type test_station: testsuite.instruments.test_stations
    :param power_monitor: Power Monitor to measure output intensity
    :type power_monitor: testsuite.instruments.PM100USB.PowerMonitor
    :param mirror1_current: Mirror 1 current while test is run
    :type mirror1_current: float
    :param mirror2_current: Mirror 2 current while test is run
    :type mirror2_current: float
    :param laser_phase_current: Laser Phase current while test is run
    :type laser_phase_current: float
    :param soa1_current: SOA 1 current while test is run
    :type soa1_current: float
    :param soa2_current: SOA 2 current while test is run
    :type soa2_current: float
    :param phase1_current: Phase 1 current while test is run
    :type phase1_current: float
    :param phase4_current: Phase 4 current while test is run
    :type phase4_current: float
    :param mod_voltage_start: Start point for both modulator voltage sweeps
    :type mod_voltage_start: float
    :param mod_voltage_end: End point for both modulator voltage sweeps
    :type mod_voltage_end: float
    :param mod_voltage_step: Step value for both modulator voltage sweeps
    :type mod_voltage_step: float
    :param output_filename: Filename to store CSV sweep data. Columns: mod1_voltage,mod2_voltage,power_monitor,detector_current
    :type output_filename: str
    :param output_img_filename: Filename to store PNG sweep image
    :type output_img_filename: str
    :param stab_time: Time in seconds to wait after setting currents
    :type stab_time: float
    :param mzm_operation_voltage_range: Voltage range that modulator operates over
    :type mzm_operation_voltage_range: float
    :return: Voltage that modulator is fully on. Voltage is always the same for both modulators, and modulator off setting can be derived by subtracting mzm_operation_voltage_range. 3dB Point must be found with an additional test.
    :rtype: float
    """
    test_station.zero_all()
    test_station.gain1.write_static_current()
    test_station.mirror1.write_current(mirror1_current)
    test_station.mirror2.write_current(mirror2_current)
    test_station.soa1.write_current(soa1_current)
    test_station.soa2.write_current(soa1_current)
    test_station.laser_phase.write_current(laser_phase_current)
    test_station.detector.write_static_voltage()
    test_station.phase1.write_current(phase1_current)
    test_station.phase4.write_current(phase4_current)
    
    time.sleep(stab_time)
    
    save_data = []
    for mod1_voltage in np.arange(mod_voltage_start, mod_voltage_end, mod_voltage_step):
        test_station.modulator1.write_voltage(mod1_voltage)
        for mod2_voltage in np.arange(mod_voltage_start, mod_voltage_end, mod_voltage_step):
            test_station.modulator2.write_voltage(mod2_voltage)
            save_data.append([mod1_voltage, mod2_voltage, power_monitor.read_value(), test_station.detector.read_current()])
            
    transpose_data = list(zip(*save_data))
    mod1 = transpose_data[0]
    mod2 = transpose_data[1]
    power_monitor = transpose_data[2]
    
    linspace = int(50 * abs(mod_voltage_end - mod_voltage_start))
    mod_range_index_delta = int(50 * mzm_operation_voltage_range)
    xi, yi = np.linspace(mod_voltage_start, mod_voltage_end, linspace)
    zi = ml.griddata(mod1, mod2, power_monitor, xi, yi)
    
    extinction_ratio_list = []
    for mod_index in range(mod_range_index_delta, linspace):
        extinction_ratio_list.append(abs(zi[mod_index, mod_index] - zi[mod_index - mod_range_index_delta, mod_index - mod_range_index_delta]))
        
    mod_voltage_max = xi(np.argmax(extinction_ratio_list) + mod_range_index_delta)
    
    ## Generate header to save in the file
    t = 'Gain1_current (mA) , ' + str(test_station.gain1.static_current) + \
    '\n Mirror1_current (A), '+ str(mirror1_current) + \
    '\n Mirror2_current (A), '+ str(mirror2_current) + \
    '\n LaserPhase_current (A), '+ str(laser_phase_current) + \
    '\n SOA1_current (A), '+ str(soa1_current) + \
    '\n SOA2_current (A), '+ str(soa2_current) + \
    '\n phase1_current (A), '+ str(phase1_current) + \
    '\n phase4_current (A), '+ str(phase4_current) + '\n'  
    h = t + 'mod1_voltage,mod2_voltage,power_monitor,detector_current'
    
    if output_filename is not None:
        np.savetxt(output_filename, save_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
        
    if output_img_filename is not None:
        plot_3d(x=mod1, 
            y=mod2, 
            z=power_monitor, 
            filename=output_img_filename, 
            title="Phase Intensity", 
            x_label="Modulator 1 (V)", 
            y_label="Modulator 4 (V)", 
            z_label="Power Monitor")
        
    return mod_voltage_max
        
def Measure_1D_Phase_Intensity_map_current(test_station, 
                                           Phase1_current_start, 
                                           Phase1_current_end, 
                                           Phase1_step, 
                                           power_monitor, 
                                           mirror1_current, 
                                           mirror2_current, 
                                           laser_phase_current, 
                                           soa1_current, 
                                           soa2_current, 
                                           output_filename=None, 
                                           output_img_filename=None, 
                                           laser_TEC=None, 
                                           stab_time=5.0):
    #Add option to select which phase section to sweep, change default to Phase1
    """Measure 1D phase intensity map for a single set of laser section values.
    
    :param test_station: Current device laser sections I/O
    :type test_station: LaserSections
    :param Phase1_current_start: Minimum current of Phase 1 section
    :type Phase1_current_start: float
    :param Phase1_current_end: Maximum current of Phase 1 section
    :type Phase1_current_end: float
    :param Phase1_step: Current step of Phase 1 section
    :type Phase1_step: float
    :param power_monitor: Power Monitor to measure IS power
    :type power_monitor: instruments.PM100USB.PowerMonitor
    :param output_filename: Path to output CSV file. Columns: modulator1_voltage,modulator2_voltage,onchip_detector_value,is_detector_value
    :type output_filename: str
    :param output_img_filename: Path to output image file of plot
    :type output_img_filename: str
    :param laser_TEC: Laser TEC controller, used to monitor laser temp and shutdown if a temp runaway is detected
    :type laser_TEC: instruments.LDT5910B.TEC
    :param stab_time: Time to stabilize laser after setting currents
    :type stab_time: float
    :return: Current values for max and min power
    :rtype: dict{"IS_min","IS_max","IS_mid","Onchip_min","Onchip_max","Onchip_mid"}
    """
    test_station.zero_all()
    test_station.gain1.write_static_current()
    test_station.mirror1.write_current(mirror1_current)
    test_station.mirror2.write_current(mirror2_current)
    test_station.phase1.zero()
    test_station.soa1.write_current(soa1_current)
    test_station.soa2.write_current(soa1_current)
    test_station.laser_phase.write_current(laser_phase_current)
    test_station.modulator1.zero()
    test_station.modulator2.zero()
    test_station.detector.write_static_voltage()
    
    time.sleep(stab_time)
    
    # loop voltage as record current in on-chip detector and powermeter
    
    save_data = []
    Phase1_range = np.arange(Phase1_current_start, Phase1_current_end + Phase1_step, Phase1_step)
    num = (Phase1_current_end - Phase1_current_start) / Phase1_step
    #print(num)
    detector_currents = []
    IS_detector = np.zeros(num + 1) # Light array initialization    
    onchip_detector = np.zeros(num + 1)
    phase1_currentarr = np.zeros(num + 1)
    i = 0
    for phase1_current in Phase1_range:
        check_tec(laser_TEC, test_station)
        test_station.phase1.write_current(phase1_current)
        phase1_currentarr[i] = phase1_current
        IS_detector[i] = power_monitor.read_value()
        onchip_detector[i] = abs(test_station.detector.read_current())
        detector_currents.append(onchip_detector)
        save_data.append([phase1_current, onchip_detector[i], IS_detector[i]])
        i = i + 1    
    
    ## Generate header to save in the file
    t = 'Gain1_current (A) , ' + str(test_station.gain1.static_current) + \
    '\n Gain2_current (A) , N/A' + \
    '\n Mirror1_current (A), '+ str(mirror1_current) + \
    '\n Mirror2_current (A), '+ str(mirror2_current) + \
    '\n LaserPhase_current (A), '+ str(laser_phase_current) + \
    '\n SOA1_current (A), '+ str(soa1_current) + \
    '\n SOA2_current (A), '+ str(soa2_current) + \
    '\n Detector_voltage (V), '+ str(test_station.detector.static_voltage) + '\n' 
    h = t + 'phase1_current,onchip_detector_value,is_detector_value'
    
    if output_filename is not None:
        np.savetxt(output_filename, save_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
    
    if output_img_filename is not None:
        Phase_plot(phase1_currentarr, IS_detector, onchip_detector, save_data[np.argmin(IS_detector)][0], save_data[np.argmax(IS_detector)][0], save_data[np.argmin(onchip_detector)][0], save_data[np.argmax(onchip_detector)][0], 'W', 'Phase 1 Current (mA)','IS power (mW)', 'Phase vs Power', output_img_filename) 
        
    #Find mid-point
    def find_midpoint(dataset):
        mid = min(dataset) + ((max(dataset) - min(dataset))/2)
        best_index = 0
        best_delta = np.inf
        for index in range(np.argmin(dataset),np.argmax(dataset)):
            if (dataset[index] - mid) < best_delta:
                best_index = index
                
        return best_index
        
    return_data = {}
    return_data["IS_min"] = save_data[np.argmin(IS_detector)][0]
    return_data["IS_max"] = save_data[np.argmax(IS_detector)][0]
    return_data["IS_mid"] = save_data[find_midpoint(IS_detector)][0]
    return_data["Onchip_min"] = save_data[np.argmin(onchip_detector)][0]
    return_data["Onchip_max"] = save_data[np.argmax(onchip_detector)][0]
    return_data["Onchip_mid"] = save_data[find_midpoint(onchip_detector)][0]
    return return_data
    
    
def Phase_plot(x, 
               yl, 
               y2, 
               Phasecurrentmin, 
               Phasecurrentmax, 
               Onchipphasecurrentmin, 
               Onchipphasecurrentmax, 
               units, 
               x_label, 
               yl_label, 
               title, 
               imagefilename):  # For Phase only
    
    """Plot phase data and save image. This function is pulled directly from old code, has not been updated
    
    :param x: Phase 1 current data
    :type x: numpy.array
    :param y1: Integrating Sphere intensity data
    :type y1: numpy.array
    :param y2: On-Chip detector intensity data
    :type y2: numpy.array
    :param Phasecurrentmin: Modulator minimum using the IS data. Used for displaying text on plot only
    :type Phasecurrentmin: float
    :param Phasecurrentmax: Modulator maximum using the IS data. Used for displaying text on plot only
    :type Phasecurrentmax: float
    :param Onchipphasecurrentmin: Modulator minimum using the on-chip data. Used for displaying text on plot only
    :type Onchipphasecurrentmin: float
    :param Onchipphasecurrentmax: Modulator maximum using the on-chip data. Used for displaying text on plot only
    :type Onchipphasecurrentmax: float
    :param units: Units used for intensity data
    :type units: str
    :param x_label: X label of plot
    :type x_label: str
    :param yl_label: Y label of plot
    :type yl_label: str
    :param title: Title of plot
    :type title: str
    :param imagefilename: Filename to save plot
    :type imagefilename: str
    """

    plt.close("all")
    fig, ax1 = plt.subplots()
    ax1.plot(x, yl, 'b-')

    ax1.set_xlabel(x_label)
    # Make the y-axis label and tick labels match the line color.
    ax1.set_ylabel(yl_label, fontsize = 12, color = 'b')
    ax1.set_title(title)
    ax1.grid(True)
    for tl in ax1.get_yticklabels():
        tl.set_color('b')
        
    ax2 = ax1.twinx()
    ax2.plot(x, y2, 'k-')
    ax2.set_ylabel('photo current (mA)', color='k')
    for tl in ax2.get_yticklabels():
        tl.set_color('k')

    string = '(blue) IS Phasemin = ' + str(Phasecurrentmin) + 'mA IS Phasemax = ' + str(Phasecurrentmax) + 'mA'   # string for insertion into plot
    string2 = '(black) On chip Phasemin = ' + str(Onchipphasecurrentmin) + 'mA Onchip Phasemax = ' + str(Onchipphasecurrentmax) + 'mA'   # string for insertion into plot
    ax1.text(0.05, .9, string,
        verticalalignment='top', horizontalalignment='left',
        transform=ax1.transAxes,
        color='blue', fontsize=12)
    ax1.text(0.05, .8, string2,
        verticalalignment='top', horizontalalignment='left',
        transform=ax1.transAxes,
        color='black', fontsize=12)
    formatter = ticker.EngFormatter(unit = units, places = 1)
    formatter.ENG_PREFIXES[-6] = 'u'
    #ax1.yaxis.set_major_formatter(formatter)
    fig.show()
    fig.savefig(imagefilename)
    plt.close("all")
    

def sweep_1d_phase_ITU(input_filename, 
                       output_filename, 
                       test_station, 
                       Phase1_current_start, 
                       Phase1_current_end, 
                       Phase1_step, 
                       power_monitor, 
                       sweep_data_folder=None, 
                       sweep_img_folder=None, 
                       laser_TEC=None, 
                       stab_time=5.0):
    """Sweep across modulator phase for each ITU index.
    
    :param input_filename: Path to input CSV ITU SOA Balanced data. Columns: itu_index, itu_wavelength, Mirr1_current, Mirr2_current, LasPha_current, SOA1_current, SOA2_current, Photocurrent_Mod1, Photocurrent_Mod2, origphotocurrent1, origphotocurrent2
    :type input_filename: str
    :param output_filename: Path to output CSV file. Columns: itu_index, itu_wavelength, Mirr1_current, Mirr2_current, LasPha_current, SOA1_current, SOA2_current, Photocurrent_Mod1, Photocurrent_Mod2, origphotocurrent1, origphotocurrent2, is_min, is_max, is_mid, onchip_min, onchip_max, onchip_mid
    :type output_filename: str
    :param test_station: Current device laser sections I/O
    :type test_station: LaserSections
    :param Phase1_current_start: Minimum current of Phase 1 section
    :type Phase1_current_start: float
    :param Phase1_current_end: Maximum current of Phase 1 section
    :type Phase1_current_end: float
    :param Phase1_step: Current step of Phase 1 section
    :type Phase1_step: float
    :param power_monitor: Power Monitor to measure IS power
    :type power_monitor: instruments.PM100USB.PowerMonitor
    :param sweep_data_folder: Path to folder to save 1d mod phase data in. Filenames will be [ITU Index].csv
    :type sweep_data_folder: str
    :param sweep_img_folder: Path to folder to save 1d mod phase plots. Filenames will be [ITU Index].png
    :type sweep_img_folder: str
    :param laser_TEC: Laser TEC controller, used to monitor laser temp and shutdown if a temp runaway is detected
    :type laser_TEC: instruments.LDT5910B.TEC
    :param stab_time: Time to stabilize laser after setting currents
    :type stab_time: float
    """
    if sweep_data_folder is not None and not os.path.exists(sweep_data_folder):
        os.makedirs(sweep_data_folder)
    if sweep_img_folder is not None and not os.path.exists(sweep_img_folder):
        os.makedirs(sweep_img_folder)
    data = np.genfromtxt(input_filename, skip_header=9, delimiter=",", names=True)
    h = itu_header() + ",SOA1_current,SOA2_current,Photocurrent_Mod1,Photocurrent_Mod2,origphotocurrent1,origphotocurrent2,is_min,is_max,is_mid,onchip_min,onchip_max,onchip_mid"
    save_data = []
    for itu_index in data["itu_index"]:
        if data[itu_index]["Mirr1_current"] == -1:
            output_item = []
            #itu_index,itu_wavelength,Mirr1_current,Mirr2_current,LasPha_current,SOA1_current,SOA2_current,Photocurrent_Mod1,Photocurrent_Mod2,origphotocurrent1,origphotocurrent2,is_min,is_max,onchip_min,onchip_max
            output_item.append(itu_index)
            output_item.append(itu_wavelength(itu_index))
            output_item.append(-1)
            output_item.append(-1)
            output_item.append(-1)
            
            output_item.append(-1)
            output_item.append(-1)
            output_item.append(-1)
            output_item.append(-1)
            output_item.append(-1)
            output_item.append(-1)
            
            output_item.append(-1)
            output_item.append(-1)
            output_item.append(-1)
            output_item.append(-1)
            output_item.append(-1)
            output_item.append(-1)
            
            save_data.append(output_item)
        else:
            if sweep_data_folder is not None:
                data_filename = sweep_data_folder + format(itu_index, '.0f') + "_1dPhaseData.csv"
            else:
                data_filename = None
                
            if sweep_img_folder is not None:
                img_filename = sweep_img_folder + format(itu_index, '.0f') + "_1dPhaseData.png"
            else:
                img_filename = None
    
            phase_data = Measure_1D_Phase_Intensity_map_current(test_station=test_station, 
                                                                Phase1_current_start=Phase1_current_start, 
                                                                Phase1_current_end=Phase1_current_end, 
                                                                Phase1_step=Phase1_step, 
                                                                power_monitor=power_monitor, 
                                                                output_filename=data_filename, 
                                                                output_img_filename=img_filename, 
                                                                mirror1_current=data["Mirr1_current"][itu_index], 
                                                                mirror2_current=data["Mirr2_current"][itu_index], 
                                                                laser_phase_current=data["LasPha_current"][itu_index], 
                                                                soa1_current=data["SOA1_current"][itu_index], 
                                                                soa2_current=data["SOA2_current"][itu_index], 
                                                                laser_TEC=laser_TEC, 
                                                                stab_time=stab_time)
            output_item = []
            #itu_index,itu_wavelength,Mirr1_current,Mirr2_current,LasPha_current,SOA1_current,SOA2_current,Photocurrent_Mod1,Photocurrent_Mod2,origphotocurrent1,origphotocurrent2,is_min,is_max,onchip_min,onchip_max
            output_item.append(itu_index)
            output_item.append(itu_wavelength(itu_index))
            output_item.append(data["Mirr1_current"][itu_index])
            output_item.append(data["Mirr2_current"][itu_index])
            output_item.append(data["LasPha_current"][itu_index])
            
            output_item.append(data["SOA1_current"][itu_index])
            output_item.append(data["SOA2_current"][itu_index])
            output_item.append(data["Photocurrent_Mod1"][itu_index])
            output_item.append(data["Photocurrent_Mod2"][itu_index])
            output_item.append(data["origphotocurrent1"][itu_index])
            output_item.append(data["origphotocurrent2"][itu_index])
            
            output_item.append(phase_data["IS_min"])
            output_item.append(phase_data["IS_max"])
            output_item.append(phase_data["IS_mid"])
            output_item.append(phase_data["Onchip_min"])
            output_item.append(phase_data["Onchip_max"])
            output_item.append(phase_data["Onchip_mid"])
            
            save_data.append(output_item)
    
    np.savetxt(output_filename, save_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
    
def balance_SOAs(input_filename, 
                 output_filename, 
                 test_station, 
                 SOA_increment=.1, 
                 laser_TEC=None):
    """For each item in the input ITU grid, set SOA currents to static voltage, then decrease arm with greater photocurrent until photocurrents are equal.
    
    :param input_filename: Path to input CSV ITU fine data. Columns: itu_index,itu_wavelength,Mirr1_current,Mirr2_current,LasPha_current
    :type input_filename: str
    :param output_filename: Path to output CSV file. Columns: itu_index,itu_wavelength,Mirr1_current,Mirr2_current,LasPha_current,SOA1_current,SOA2_current,Photocurrent_Mod1,Photocurrent_Mod2,origphotocurrent1,origphotocurrent2
    :type output_filename: str
    :param test_station: Initialized test station
    :type test_station: testsuite.instruments.test_stations
    :param SOA_increment: Step size to decrease SOA current
    :type SOA_increment: float
    :param laser_TEC: Laser TEC controller, used to monitor laser temp and shutdown if a temp runaway is detected
    :type laser_TEC: testsuite.instruments.LDT5910B.TEC
    """
    sweepdata = np.genfromtxt(input_filename, skip_header=9, delimiter=",", names=True)
    #x=0
    #ITU_all = []
    
    ITU_all = sweepdata["itu_index"]
    wavelength_all = sweepdata["itu_wavelength"]
    mirror1all = sweepdata["Mirr1_current"]
    mirror2all = sweepdata["Mirr2_current"]
    phase_all = sweepdata["LasPha_current"]
    #Phase1_all = sweepdata["mod_phase1_current"]
    save_data = []
    for itu_index in sweepdata["itu_index"]:
        if (mirror1all[itu_index] != -1):
            test_station.zero_all()
            
            test_station.gain1.write_static_current()
            test_station.phase1.write_static_current()
            test_station.soa1.write_static_current()
            test_station.soa2.write_static_current()
            test_station.modulator1.write_static_voltage()
            test_station.modulator2.write_static_voltage()
            
            test_station.mirror1.write_current(mirror1all[itu_index])
            test_station.mirror2.write_current(mirror2all[itu_index])
            test_station.laser_phase.write_current(phase_all[itu_index])
            
            P1 = test_station.modulator1.read_current() * -1  # evaluate photocurrent in both modulators prior to changing SOA biases to match powers. 
            P2 = test_station.modulator2.read_current() * -1
            P1orig = P1
            P2orig = P2
            
            if (P1 > P2):
                SOA1_current_ch = test_station.soa1.static_current
                SOA2_current_ch = test_station.soa2.static_current
                test_station.soa1.write_current(SOA1_current_ch)
                test_station.soa2.write_current(SOA2_current_ch)
                P1 = test_station.modulator1.read_current() * -1
                P2 = test_station.modulator2.read_current() * -1
                while (P1 > P2) and (SOA1_current_ch - SOA_increment > 0):
                    check_tec(laser_TEC, test_station)
                    SOA1_current_ch = SOA1_current_ch - SOA_increment
                    test_station.soa1.write_current(SOA1_current_ch)
                    P1 = test_station.modulator1.read_current() * -1
                    P2 = test_station.modulator2.read_current() * -1
            else:
                SOA1_current_ch = test_station.soa1.static_current
                SOA2_current_ch = test_station.soa2.static_current
                test_station.soa1.write_current(SOA1_current_ch)
                test_station.soa2.write_current(SOA2_current_ch)
                P1 = test_station.modulator1.read_current() * -1
                P2 = test_station.modulator2.read_current() * -1
                while (P1 < P2) and (SOA2_current_ch - SOA_increment > 0):
                    check_tec(laser_TEC, test_station)
                    SOA2_current_ch = SOA2_current_ch - SOA_increment
                    test_station.soa2.write_current(SOA2_current_ch)
                    P1 = test_station.modulator1.read_current() * -1
                    P2 = test_station.modulator2.read_current() * -1
            save_data.append([ITU_all[itu_index],wavelength_all[itu_index],mirror1all[itu_index], mirror2all[itu_index], phase_all[itu_index], SOA1_current_ch, SOA2_current_ch, P1, P2, P1orig, P2orig])
        else:
            save_data.append([ITU_all[itu_index],wavelength_all[itu_index],-1,-1,-1,-1,-1,-1,-1,-1,-1])
            
    h = ""
    for i in range(9):
        h = h + "\n" #Header lines
    h = h + 'itu_index,itu_wavelength,Mirr1_current,Mirr2_current,LasPha_current,SOA1_current,SOA2_current,Photocurrent_Mod1,Photocurrent_Mod2,origphotocurrent1,origphotocurrent2'
    #output_filename = path_base + '_Power_in_Arms_Balance_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.csv'
    np.savetxt(output_filename, save_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)

def measure_MZM_Intensity_matrix(output_filename_base,
                                 output_img_filename_base,
                                 test_station,
                                 min_voltage,
                                 max_voltage,
                                 voltage_step,
                                 power_monitor,
                                 mirror1_current,
                                 mirror2_current,
                                 laser_phase_current,
                                 phase1_current,
                                 soa1_current,
                                 soa2_current,
                                 laser_TEC=None, 
                                 stab_time=5.0):
    
    """Take a 2d MZM map for for a given set of currents
    
    :param output_filename_base: Folder location to save CSV debug data. Not actually neccesary to have a folder, only outputs one file... columns: modulator1_voltage, modulator2_voltage, detector_value, power
    :type output_filename_base: str
    :param output_img_filename_base: Folder location to save PNG plots, as IS, IS log 10, and on-chiplog 10
    :type output_img_filename_base: str
    :param test_station: Initialized test station
    :type test_station: testsuite.instruments.test_stations
    :param min_voltage: Minimum MZM voltage
    :type min_voltage: float
    :param max_voltage: Maximum MZM voltage
    :type max_voltage: float
    :param voltage_step: MZM voltage step
    :type voltage_step: float
    :param power_monitor: Power Monitor to measure IS power
    :type power_monitor: instruments.PM100USB.PowerMonitor
    :param mirror1_current: Mirror 1 current while test is run
    :type mirror1_current: float
    :param mirror2_current: Mirror 2 current while test is run
    :type mirror2_current: float
    :param phase1_current: Phase 1 current while test is run
    :type phase1_current: float
    :param laser_phase_current: Laser Phase current while test is run
    :type laser_phase_current: float
    :param soa1_current: SOA 1 current while test is run
    :type soa1_current: float
    :param soa2_current: SOA 2 current while test is run
    :type soa2_current: float
    :param laser_TEC: Laser TEC controller, used to monitor laser temp and shutdown if a temp runaway is detected
    :type laser_TEC: testsuite.instruments.LDT5910B.TEC
    :param stab_time: Time in seconds to wait after setting currents
    :type stab_time: float
    """
                                     
    if not os.path.exists(os.path.dirname(output_filename_base)):
        os.makedirs(os.path.dirname(output_filename_base))
        
    if not os.path.exists(os.path.dirname(output_img_filename_base)):
        os.makedirs(os.path.dirname(output_img_filename_base))
        
    test_station.zero_all()
        
    test_station.gain1.write_static_current()
    test_station.mirror1.write_current(mirror1_current)
    test_station.mirror2.write_current(mirror2_current)
    test_station.phase1.write_current(phase1_current)
    test_station.soa1.write_current(soa1_current)
    test_station.soa2.write_current(soa2_current)
    test_station.laser_phase.write_current(laser_phase_current)
    test_station.detector.write_static_voltage()
    
    time.sleep(stab_time)
    
    # loop voltage as record current in on-chip detector and powermeter
        
    save_data = []
    mod1_range = np.arange(min_voltage, max_voltage + voltage_step, voltage_step)
    mod2_range = np.arange(min_voltage, max_voltage + voltage_step, voltage_step)
    onchipDetector_currents = []
    ISdetector_currents = []
    test_station.modulator1.zero()
    test_station.modulator2.zero()
    for modulator1_voltage in mod1_range:
        test_station.modulator1.write_voltage(modulator1_voltage)
        for modulator2_voltage in mod2_range:
            check_tec(laser_TEC, test_station)
            test_station.modulator2.write_voltage(modulator2_voltage)
            IS_Detector = power_monitor.read_value()
            OnchipDetector = abs(test_station.detector.read_current())
            onchipDetector_currents.append(OnchipDetector)
            ISdetector_currents.append(IS_Detector)
            save_data.append([modulator1_voltage, modulator2_voltage, OnchipDetector, IS_Detector])
    
    ## Generate header to save in the file
    t = 'Gain1_current (A) , ' + str(test_station.gain1.static_current) + \
    '\n Mirror1_current (A), '+ str(mirror1_current) + \
    '\n Mirror2_current (A), '+ str(mirror2_current) + \
    '\n Phase1_current (A), '+ str(phase1_current) + \
    '\n LaserPhase_current (A), '+ str(laser_phase_current) + \
    '\n SOA1_current (A), '+ str(soa1_current) + \
    '\n SOA2_current (A), '+ str(soa2_current) + \
    '\n Detector_voltage (V), '+ str(test_station.detector.static_voltage) + '\n\n' 
    h = t + 'modulator1_voltage,modulator2_voltage,detector_value,power'
    
    #filename = path_base + '\\MZM' + '\\UID' + fname + '_MzmMapVoltage_' + str(Phase1_current) + '_ITUChannel_'+ str(ITU_channel) + '_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.csv'
    out_filename = output_filename_base + 'Mzm2DMap_data.csv'
    np.savetxt(out_filename, save_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
    
    # Plot data
    plt.close("all")
    Mod1_voltages, Mod2_voltages = np.meshgrid(mod1_range, mod2_range)
    POW = np.reshape(np.array(onchipDetector_currents), (len(Mod1_voltages), len(Mod2_voltages)))
    
    log_det_currents = 10 * np.log10([x/max(onchipDetector_currents) for x in onchipDetector_currents])
    POW2 = np.reshape(np.array(log_det_currents), (len(Mod1_voltages), len(Mod2_voltages)))
    
    log_IS_currents = 10 * np.log10([x for x in ISdetector_currents])
    POW3 = np.reshape(np.array(log_IS_currents), (len(Mod1_voltages), len(Mod2_voltages)))    
    
    POW4 = np.reshape(np.array(ISdetector_currents), (len(Mod1_voltages), len(Mod2_voltages)))   
    
    f2 = plt.figure()
    ax2 = f2.add_subplot(111)
    im = ax2.imshow(POW, origin='lower', cmap = plt.get_cmap('spectral'), extent=[min_voltage,max_voltage,min_voltage,max_voltage])
    cbar = plt.colorbar(im, shrink = 0.5)  # adding the colobar on the right
    cbar.ax.set_ylabel('on-chip photo current (mA)' )
    #imgfilename = path_base + '\\MZM' + '\\UID' + fname + '_Mzm2DMapVoltage_' + str(Mirror1_current) + '_ITUChannel' + str(ITU_channel) +'_'+ datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.png'
    imgfilename = output_img_filename_base + 'Mzm2DMapVoltage_OC.png'
    plt.xlabel('Mod1 (V)')
    plt.ylabel('Mod2 (V)')
    plt.title(r'On-chip output intensity')
    
    f2.savefig(imgfilename)
    plt.close(f2)
    
    f2 = plt.figure()
    ax2 = f2.add_subplot(111)
    im = ax2.imshow(POW2, origin='lower', cmap = plt.get_cmap('spectral') , extent=[min_voltage,max_voltage,min_voltage,max_voltage])
    cbar = plt.colorbar(im, shrink = 0.5)  # adding the colorbar on the right
    cbar.ax.set_ylabel('norm. Power (dB)' )
    #imgfilename = path_base + '\\MZM' + '\\UID' + fname + '_Mzm2DMapVoltageLog10_' + str(Mirror1_current) + 'ITUChannel' + str(ITU_channel) + '_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.png'
    imgfilename = output_img_filename_base + 'Mzm2DMapVoltage_OC_Log10.png'
    plt.xlabel('Mod1 (V)')
    plt.ylabel('Mod2 (V)')
    plt.title(r'On-chip output norm. log10 intensity')
    f2.savefig(imgfilename)
    plt.close(f2)
    
    f2 = plt.figure()
    ax2 = f2.add_subplot(111)
    im = ax2.imshow(POW3, origin='lower', cmap = plt.get_cmap('spectral') , extent=[min_voltage,max_voltage,min_voltage,max_voltage])
    cbar = plt.colorbar(im, shrink = 0.5)  # adding the colorbar on the right
    cbar.ax.set_ylabel('norm. Power (dBm)' )
    #imgfilename = path_base + '\\MZM' + '\\UID' + fname + '_Mzm2DMapVoltageISLog10_' + str(Mirror1_current) + '_ITU_Channel'+ str(ITU_channel) + '_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.png'
    imgfilename = output_img_filename_base + 'Mzm2DMapVoltage_IS_Log10.png'
    plt.xlabel('Mod1 (V)')
    plt.ylabel('Mod2 (V)')
    plt.title(r'IS output - log10 intensity')
    f2.savefig(imgfilename)
    plt.close(f2)
    
    f2 = plt.figure()
    ax2 = f2.add_subplot(111)
    im = ax2.imshow(POW4, origin='lower', cmap = plt.get_cmap('spectral') , extent=[min_voltage,max_voltage,min_voltage,max_voltage])
    cbar = plt.colorbar(im, shrink = 0.5)  # adding the colorbar on the right
    cbar.ax.set_ylabel('IS output power (mW)' )
    #imgfilename = path_base + '\\MZM' + '\\UID' + fname + '_Mzm2DMapVoltageISLog10_' + str(Mirror1_current) + '_ITU_Channel'+ str(ITU_channel) + '_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.png'
    imgfilename = output_img_filename_base + 'Mzm2DMapVoltage_IS.png'
    plt.xlabel('Mod1 (V)')
    plt.ylabel('Mod2 (V)')
    plt.title(r'IS output intensity')
    f2.savefig(imgfilename)
    plt.close(f2)
    
    plt.close("all") #Just in case
    
def MZM_2d_ITU(input_filename, 
               output_data_path, 
               test_station, 
               power_monitor, 
               mzm_voltage_min, 
               mzm_voltage_max, 
               mzm_voltage_step, 
               laser_TEC=None):
    """For each valid row of the ITU grip, store a 2d MZM map
    
    :param input_filename: Path to input CSV ITU Modulator characterized data. Columns: itu_index, itu_wavelength, Mirr1_current, Mirr2_current, LasPha_current, SOA1_current, SOA2_current, Photocurrent_Mod1, Photocurrent_Mod2, origphotocurrent1, origphotocurrent2, is_min, is_max, is_mid, onchip_min, onchip_max, onchip_mid
    :type input_filename: str
    :param output_data_path: Folder path to save 2d MZM data and plots
    :type output_data_path: str
    :param test_station: Initialized test station
    :type test_station: testsuite.instruments.test_stations
    :param power_monitor: Power Monitor to measure IS power
    :type power_monitor: instruments.PM100USB.PowerMonitor
    :param mzm_voltage_min: Minimum MZM voltage
    :type mzm_voltage_min: float
    :param mzm_voltage_max: Maximum MZM voltage
    :type mzm_voltage_max: float
    :param mzm_voltage_step: MZM voltage step value
    :type mzm_voltage_step: float
    :param laser_TEC: Laser TEC controller, used to monitor laser temp and shutdown if a temp runaway is detected
    :type laser_TEC: testsuite.instruments.LDT5910B.TEC
    """
    sweepdata = np.genfromtxt(input_filename, skip_header=9, delimiter=",", names=True)
    for itu_index in sweepdata["itu_index"]:
        if sweepdata["Mirr1_current"][itu_index] != -1:
            measure_MZM_Intensity_matrix(output_filename_base=output_data_path + '\\' + format(itu_index, '.0f') + '\\',
                             output_img_filename_base=output_data_path + '\\' + format(itu_index, '.0f') + '\\',
                             test_station=test_station,
                             min_voltage=mzm_voltage_min,
                             max_voltage=mzm_voltage_max,
                             voltage_step=mzm_voltage_step,
                             power_monitor=power_monitor, 
                             mirror1_current=sweepdata["Mirr1_current"][itu_index],
                             mirror2_current=sweepdata["Mirr2_current"][itu_index],
                             laser_phase_current=sweepdata["LasPha_current"][itu_index],
                             phase1_current=sweepdata["is_mid"][itu_index],
                             soa1_current=sweepdata["SOA1_current"][itu_index],
                             soa2_current=sweepdata["SOA2_current"][itu_index],
                             laser_TEC=laser_TEC)
                
def verify_wavetable(input_filename, 
                     test_station, 
                     full_osa, 
                     wavemeter, 
                     output_filename=None, 
                     minimum_power=-3.0, 
                     minimum_smsr=40.0, 
                     maximum_itu_delta=.1, 
                     laser_TEC=None, 
                     connection_loss=3.5):
    """Verify that wavetable file still meets ITU grid
    
    :param input_filename: Path to wavetable file. Columns: itu_index,itu_wavelength,Mirr1_current,Mirr2_current,LasPha_current,SOA1_current,SOA2_current
    :type input_filename: str
    :param test_station: Current device laser sections I/O
    :type test_station: LaserSections
    :param full_osa: Initialized OSA to get SMSR data
    :type full_osa: instruments.MS9740.OSA
    :param wavemeter: Initialized wavemeter to get wavelength and power data
    :type wavemeter: instruments.HP86120B.OSA
    :param output_filename: Path to output CSV file. Columns: itu_index,itu_wavelength,power,smsr
    :type output_filename: str
    :param minimum_power: Minimum laser peak power
    :type minimum_power: float
    :param minimum_smsr: Minimum SMSR
    :type minimum_smsr: flot
    :param maximum_itu_delta: Maximum deviation from ITU wavelength
    :type maximum_itu_delta: float
    :param laser_TEC: Laser TEC controller, used to monitor laser temp and shutdown if a temp runaway is detected
    :type laser_TEC: instruments.LDT5910B.TEC
    :param connection_loss: dB loss of connectors/splitters
    :type connection_loss: float
    :return: List of ITU wavetable entries out of spec. Empty list if all entries in spec
    :rtype: List
    """
    
    test_station.gain1.write_static_current()
    wavetable_data = np.genfromtxt(input_filename, skip_header=9, delimiter=",", names=True)
    invalid_list = []
    output_data = []
    for itu_index in wavetable_data["itu_index"]:
        if wavetable_data[itu_index]["Mirr1_current"] == -1:
            continue
        test_station.mirror1.write_current(wavetable_data["Mirr1_current"][itu_index])
        test_station.mirror2.write_current(wavetable_data["Mirr2_current"][itu_index])
        test_station.laser_phase.write_current(wavetable_data["LasPha_current"][itu_index])
        test_station.soa1.write_current(wavetable_data["SOA1_current"][itu_index])
        test_station.soa2.write_current(wavetable_data["SOA2_current"][itu_index])
        time.sleep(0.2)
        full_osa.sweep_single()
        full_osa.wait_for_sweepcomplete()
        time.sleep(0.5)
        peakfound = False
        while not peakfound:
            try:
                check_tec(laser_TEC, test_station)
                peakdata = wavemeter.readpeak()
                peakfound = True
            except socket.timeout:
                pass # Loop through peak finder again
        
        wavemeter_power = peakdata[0]["power"]
        wavemeter_WL = peakdata[0]["wavelength"]
        SMSR = full_osa.read_smsr()
        output_data.append([itu_index,wavemeter_WL,wavemeter_power,SMSR])
            
        if len(peakdata) == 0:
            invalid_list.append(itu_index)
            continue
        if wavemeter_power + connection_loss < minimum_power:
            invalid_list.append(itu_index)
            continue
        if abs(wavemeter_WL - itu_wavelength(itu_index)) > maximum_itu_delta:
            invalid_list.append(itu_index)
            continue
        if SMSR < minimum_smsr:
            invalid_list.append(itu_index)
            continue
        
    if output_filename is not None:
        h = ""
        for i in range(9):
            h = h + "\n" #Header lines
        h = h + 'itu_index,wavelength,power,smsr'
        np.savetxt(output_filename, output_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
        
    return invalid_list,output_data

def mirror_sweep_1d(mirror_section, 
                    test_station, 
                    output_filename, 
                    full_osa, 
                    min_current, 
                    max_current, 
                    step_current, 
                    laser_phase_current=0, 
                    laser_TEC=None, 
                    debug_data_filename=None, 
                    gauss_sigma=12, 
                    mirror_current=50):
    """Start finding mirror currents for ITU grid by sweeping a single mirror section with gain off, but SOAs on into an OSA to record spontaneous emissions. Write peaks of osa trace to file.
    
    :param mirror_section: Constant to signify which mirror section to sweep. Other arm of laser is set constant, wth modulator reverse-biased to soak. 
    :type mirror_section: testsuite.tests.tosa_tests.MIRROR1 or testsuite.tests.tosa_tests.MIRROR2
    :param test_station: Current device laser sections I/O
    :type test_station: LaserSections
    :param output_filename: Path to output CSV file. Columns: current,wavelength,power,LasPha_current
    :type output_filename: str
    :param full_osa: OSA hooked to laser output
    :type full_osa: testsuite.instruments.MS9740.OSA
    :param min_current: Minimum current to sweep selected mirror
    :type min_current: float
    :param max_current: Maximum current to sweep selected mirror
    :type max_current: float
    :param step_current: Current step to sweep selected mirror
    :type step_current: float
    :param laser_phase_current: Laser Phase current to set for sweep
    :type laser_phase_current: float
    :param laser_TEC: Laser TEC controller, used to monitor laser temp and shutdown if a temp runaway is detected
    :type laser_TEC: instruments.LDT5910B.TEC
    :param debug_data_filename: Path to output debug CSV file with full OSA sweep. Columns: current,wavelength,power,LasPha_current
    :type debug_data_filename: str
    :param gauss_sigma: Gaussian sigma parameter to smooth OSA trace before finding peaks
    :type gauss_sigma: float
    :param mirror_current: Current to set non-selected mirror to during test. Used to heat laser as close to operation temp as possible
    :type mirror_current: float
    """
    
    #Need to setup other laser phase sections
    test_station.zero_all()
    test_station.laser_phase.write_current(laser_phase_current)
    test_station.soa1.write_static_current()
    test_station.soa2.write_static_current()
    test_station.gain1.write_static_current()
    if mirror_section == MIRROR1:
        write_current_func = test_station.mirror1.write_current
        test_station.modulator2.write_static_voltage()
        test_station.mirror2.write_current(mirror_current)
    elif mirror_section == MIRROR2:
        write_current_func = test_station.mirror2.write_current
        test_station.modulator2.write_static_voltage()
        test_station.mirror1.write_current(mirror_current)
    else:
        raise(TypeError("mirror_section must be either MIRROR1 or MIRROR2"))
    
    center_wl = 1560.0
    span = 110
    resolution = 0.07
    vbw = 100
    full_osa.set_center_wavelength(center_wl)
    full_osa.set_span(span)
    full_osa.set_resolution(resolution)
    full_osa.set_video_bandwidth(vbw)
    
    save_data = []
    debug_data = []
    
    for current in range(min_current, max_current, step_current):
        write_current_func(current)
        full_osa.sweep_single()
        time.sleep(20)
        trace_data = full_osa.read_trace_memory_A()
        for trace_item in trace_data:
            debug_data.append([current, trace_item[0], trace_item[1], laser_phase_current])
        
        trace_flat = [] # Flat power data
        for item in trace_data:
            trace_flat.append(item[1])
        trace_flat_array = np.array(trace_flat)
        min_indices = scipy.signal.argrelmax(ndimage.filters.gaussian_filter1d(trace_flat_array, gauss_sigma))[0]
        for min_index in min_indices:
            save_data.append([current, trace_data[min_index][0], trace_data[min_index][1], laser_phase_current])
            
    h = ""
    for i in range(9):
        h = h + "\n" #Header lines
    h = h + 'current,wavelength,power,LasPha_current'
    np.savetxt(output_filename, save_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
    if debug_data_filename is not None:
        np.savetxt(debug_data_filename, debug_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)

def clearall():
    """clear all globals"""
    #This is INCREDIBLY dangerous
    for uniquevar in [var for var in globals().copy() if var[0] != "_" and var != 'clearall']:
        del globals()[uniquevar]

def measure_vpi(test_station):
    """Unsure what this does, talk to Chad."""
    test_station.zero_all()
    test_station.gain1.write_current(150)
    test_station.soa1.write_current(60)
    test_station.soa2.write_current(28)
    test_station.mirror1.write_current(5)
    test_station.mirror2.write_current(4.465)
    test_station.detector.write_voltage(-3)
    test_station.modulator1.write_voltage(0)
    test_station.modulator2.write_voltage(0)
    detector_current = []
    datapoints = 50
    phase_currents = np.linspace(0,15,datapoints)
    max_detector_current = 10
    phase_current_for_max_detector_current = 0
    
    for counter in range(datapoints):
        test_station.phase1.write_current(phase_currents[counter])
        detector_current.append(abs(test_station.detector.read_current()))
        if abs(detector_current[counter]) < max_detector_current:
            max_detector_current = abs(detector_current[counter])
            phase_current_for_max_detector_current = phase_currents[counter]
            
    test_station.phase1.write_current(phase_current_for_max_detector_current)
    mod_voltages = np.linspace(0,-6,datapoints)
    detector_currents_across_modulator1 = []  
    detector_currents_across_modulator2 = []
   
    test_station.modulator2.write_voltage(0)    
    
    for counter in range(datapoints):
        test_station.modulator1.write_voltage(mod_voltages[counter])
        detector_currents_across_modulator1.append(abs(test_station.detector.read_current()))
        
    test_station.modulator1.write_voltage(0)
    
    for counter in range(datapoints):
        test_station.modulator2.write_voltage(mod_voltages[counter])
        detector_currents_across_modulator2.append(abs(test_station.detector.read_current()))
    
    vpi1 = round(mod_voltages[np.argmax(detector_currents_across_modulator1)]*100)/100 
    vpi2 = round(mod_voltages[np.argmax(detector_currents_across_modulator2)]*100)/100    
    
#    print(size())
#    print(size())
    
    plt.close("all")    
    
    plt.figure(0)
    plt.plot(mod_voltages,detector_currents_across_modulator1)
    plt.xlabel('Modulator 1 Voltage (V)')
    plt.ylabel('Detector Current (A)')
    plt.title('Modulator 1 Vpi measurement. Vpi 1 = ' + str(vpi1))
    plt.gca().invert_xaxis()
  
    plt.figure(1)
    plt.plot(mod_voltages,detector_currents_across_modulator2)
    plt.xlabel('Modulator 2 Voltage (V)')
    plt.ylabel('Detector Current (A)')
    plt.title('Modulator 2 Vpi measurement. Vpi 2 ='  + str(vpi2))
    plt.gca().invert_xaxis()

def checkit(a, s, maxd_limit):
    num_modes = np.size(s)
    stype = np.zeros(np.size(s))    
        
    c = 0
    d = 0
    maxd = 0
    print(num_modes)
    print(s)
    for i in range(num_modes):
        d = 0
        maxd = 0
        for c in range(s[i]):
            if a[i,c+1]-a[i,c] == 0:
                d = d + 1
                if d>maxd:
                    maxd = d
            else:
                d = 0
        stype[i] = maxd < maxd_limit
    

    return stype
    
def checkit_all(x1, x2, x3, x4, s, s2, maxd_limit):
    print("hello")
    a = checkit(x1, s, maxd_limit)
    b = checkit(x2, s, maxd_limit)
    c = checkit(x3, s2, maxd_limit)
    d = checkit(x4, s2, maxd_limit)
    print("a = " + str(a))
    print("b = " + str(b))
    print("c = " + str(c))
    print("d = " + str(d))
    print(np.size(a))
    normal_looking_traces = np.zeros(np.size(a))
    scan_between = np.zeros(np.size(a))
    scan_below = np.zeros(np.size(a))
    scan_above = np.zeros(np.size(a))
    
    count = 0    
    for count in range(np.size(a)):
        normal_looking_traces[count] = a[count] and b[count] and c[count] and d[count]
        
    scan_between = normal_looking_traces * 1
    for i in range(np.size(a)-1):
        scan_below[i] = (scan_between[i+1] - scan_between[i]) == -1
        scan_above[i+1] = (scan_between[i+1] - scan_between[i]) == 1
        if normal_looking_traces[i+1] == 0: 
            print("once " + str(i))
            scan_between[i] = 0
            print(str(scan_between[i]))
    scan_below[np.size(a,0)-1] = 1
    scan_above[0] = 1
    return [normal_looking_traces, scan_between, scan_below, scan_above]
 
def mirror_search(path_b1, 
                    test_station,
                    saved_data,
                    output_filename, 
                    full_osa, 
                    laser_TEC=None, 
                    debug_data_filename=None):
    """Procedure to find ITU mirror currents by dithering along mode-switching lines."""
    continue_measurements = 1     
    continue_measurements = raw_input('continue measurements after search? (1=yes  0=no) :') 
    demo = raw_input('demo? (y = yes or n = no):') 
    
    ITU_index = np.linspace(0,299,300)
    ITU_channel = np.array([1490.76,1491.13,1491.5,1491.88,1492.25,1492.62,1492.99,1493.36,1493.73,1494.11,1494.48,1494.85,1495.22,1495.6,1495.97,1496.34,1496.72,1497.09,1497.46,1497.84,1498.21,1498.59,1498.96,1499.34,1499.71,1500.09,1500.46,1500.84,1501.21,1501.59,1501.97,1502.34,1502.72,1503.1,1503.47,1503.85,1504.23,1504.6,1504.98,1505.36,1505.74,1506.12,1506.49,1506.87,1507.25,1507.63,1508.01,1508.39,1508.77,1509.15,1509.53,1509.91,1510.29,1510.67,1511.05,1511.43,1511.81,1512.19,1512.58,1512.96,1513.34,1513.72,1514.1,1514.49,1514.87,1515.25,1515.63,1516.02,1516.4,1516.78,1517.17,1517.55,1517.94,1518.32,1518.71,1519.09,1519.48,1519.86,1520.25,1520.63,1521.02,1521.4,1521.79,1522.18,1522.56,1522.95,1523.34,1523.72,1524.11,1524.5,1524.89,1525.27,1525.66,1526.05,1526.44,1526.83,1527.22,1527.6,1527.99,1528.38,1528.77,1529.16,1529.55,1529.94,1530.33,1530.72,1531.12,1531.51,1531.9,1532.29,1532.68,1533.07,1533.47,1533.86,1534.25,1534.64,1535.04,1535.43,1535.82,1536.22,1536.61,1537,1537.4,1537.79,1538.19,1538.58,1538.98,1539.37,1539.77,1540.16,1540.56,1540.95,1541.35,1541.75,1542.14,1542.54,1542.94,1543.33,1543.73,1544.13,1544.53,1544.92,1545.32,1545.72,1546.12,1546.52,1546.92,1547.32,1547.72,1548.11,1548.51,1548.91,1549.32,1549.72,1550.12,1550.52,1550.92,1551.32,1551.72,1552.12,1552.52,1552.93,1553.33,1553.73,1554.13,1554.54,1554.94,1555.34,1555.75,1556.15,1556.55,1556.96,1557.36,1557.77,1558.17,1558.58,1558.98,1559.39,1559.79,1560.2,1560.61,1561.01,1561.42,1561.83,1562.23,1562.64,1563.05,1563.45,1563.86,1564.27,1564.68,1565.09,1565.5,1565.9,1566.31,1566.72,1567.13,1567.54,1567.95,1568.36,1568.77,1569.18,1569.59,1570.01,1570.42,1570.83,1571.24,1571.65,1572.06,1572.48,1572.89,1573.3,1573.71,1574.13,1574.54,1574.95,1575.37,1575.78,1576.2,1576.61,1577.03,1577.44,1577.86,1578.27,1578.69,1579.1,1579.52,1579.93,1580.35,1580.77,1581.18,1581.6,1582.02,1582.44,1582.85,1583.27,1583.69,1584.11,1584.53,1584.95,1585.36,1585.78,1586.2,1586.62,1587.04,1587.46,1587.88,1588.3,1588.73,1589.15,1589.57,1589.99,1590.41,1590.83,1591.26,1591.68,1592.1,1592.52,1592.95,1593.37,1593.79,1594.22,1594.64,1595.06,1595.49,1595.91,1596.34,1596.76,1597.19,1597.62,1598.04,1598.47,1598.89,1599.32,1599.75,1600.17,1600.6,1601.03,1601.46,1601.88,1602.31,1602.74,1603.17,1603.6,1604.03,1604.46,1604.88,1605.31,1605.74,1606.17,1606.6,1607.04,1607.47,1607.9,1608.33,1608.76,1609.19,1609.62,1610.06,1610.49])    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print("time is" + timestamp)
    
    #Need to setup other laser phase sections
    test_station.zero_all()
    test_station.laser_phase.write_current(0)
    test_station.soa1.write_static_current()
    #test_station.soa2.write_static_current()
    test_station.soa2.write_current(0) #I set this to zero so that there is not interference in the MMI
    test_station.gain1.write_static_current()
    
    write_current_func1 = test_station.mirror1.write_current
    test_station.mirror2.write_current(0)
    
    write_current_func2 = test_station.mirror2.write_current
    write_laspha_current = test_station.laser_phase.write_current
    test_station.mirror1.write_current(0)
   
    center_wl = 1555.0
    span = 70
    span_short = 12 #span
    resolution = 0.03 #I have not played around with resolution yet.
    vbw = 100000 #I found 100000 to be max without errors.  Better code could allow 1000000 Syntax: VBW 10HZ|100HZ|200HZ|1KHZ|2KHZ|10KHZ|100KHZ|1MHZ |10|100|200|1000|2000|10000|100000|1000000
    sampling_points=1001 #A larger number of sampling points are needed to image the entire span 1001,2001,5001
    
    full_osa.set_center_wavelength(center_wl)
    full_osa.set_span(span)
    full_osa.set_resolution(resolution)
    full_osa.set_video_bandwidth(vbw)
    full_osa.set_sampling_points(sampling_points)
        
    #for current in range(min_current, max_current, step_current):
    m1c=0
    m2c=0    
    
    write_current_func1(m1c)
    write_current_func2(m2c)    
    
    cnt=1
    
    m1start = [] #M1 supermode start currents.  This is from an older code and can be replaced by sm1l, sm2l, smwl, etc.  but is still coded in right now
    m1startw = [] #M1 supermode start wavelength.  This is from an older code and can be replaced by sm1l, sm2l, smwl, etc.  but is still coded in right now
    m2start = [] #M2 supermode start currents.  This is from an older code and can be replaced by sm1l, sm2l, smwl, etc.  but is still coded in right now
    m2startw = [] #M2 supermode start wavelength.  This is from an older code and can be replaced by sm1l, sm2l, smwl, etc.  but is still coded in right now
      
    if (saved_data == 0):
        time.sleep(1)    
              
        numb = 0
        snlow = 0
        snhigh = 0
        sm1l = np.zeros((80,251))  #supermode mirror 1 current on the left side of the supermode.  Size is determined by 50mA divideded by mirror current step size
        sm1r = np.zeros((80,251))  #supermode mirror 1 current on the right side of the supermode
        sm2l = np.zeros((80,251))  #supermode mirror 2 current on the left side of the supermode
        sm2r = np.zeros((80,251))  #supermode mirror 2 current on the right side of the supermode
        smwl = np.zeros((80,251))  #supermode wavelength on the left side
        smwr = np.zeros((80,251))  #supermode wavelength on the right side
        sn = 0 #supermode number
        m_step = 0.3 #step size to increase the mirror in mA
            
        old_peak = 0  
        peak = 0
        for cnt in range(170):  #60 steps of m_step step size.  this need to be enough to get to wrap-around.  We may need to increase it
            if (m2c >50 or (sn > 0 and demo == 'y')):
                break
            write_current_func1(m1c)
            write_current_func2(m2c)
            peak,peak_pow = full_osa.search_peak()
            while (peak < 1500):
                peak,peak_pow = full_osa.search_peak()
            print peak
            if((full_osa.identity() == 'MS9740' and peak_pow <= -40) or (full_osa.identity() == 'WS6' and (peak < 1500 or (old_peak != [] and abs(peak-old_peak) > 0.4 and abs(peak-old_peak) < 4.3) or (old_peak != [] and abs(peak-old_peak) > 5.6)))): 
                #if cnt == 0: continue 
                print("ERROR: peak not found")               
                print("failed peak = " + str(peak))
                peak = old_peak
            else:
                old_peak = peak
            m2start.append(m2c)
            m2startw.append(peak)
            if (cnt == 0): continue #this gets rid of the problem on the next line where we try to address cnt-1 which doen't exist yet               
            print(m2startw[cnt],m2startw[cnt-1])
            condition = abs(m2startw[cnt]-m2startw[cnt-1])  #check how much the peak has shifted.  We may want to remove the abs().  We would have to make the if statements more specific though 
            if (condition > 10 and full_osa.identity() == 'MS9740'): #if wrap around, stop
                print(str(m2startw[cnt]) + ' ' + str(m2startw[cnt-1]))
                full_osa.set_sampling_points(sampling_points)
                full_osa.set_center_wavelength(center_wl)
                full_osa.set_span(span)
                snhigh = sn
                continue
            if (condition>4.3):  #start supermode tracking
                full_osa.set_sampling_points(251) #reduce the sampling points due to span decrease
                full_osa.set_center_wavelength(min([m2startw[cnt],m2startw[cnt-1]])) #center the wavelength on the lower of the two wavelengths because the wavelengths will shift downward and peaks should remain within the span
                full_osa.set_span(span_short) #reduce span to only see the two supermodes
                sm1l[sn][0]=0 # the next six lines are the starting values of the supermode for this supermode number (sn)
                sm2l[sn][0]=m2c
                smwl[sn][0]=m2startw[cnt]
                sm1r[sn][0]=0
                sm2r[sn][0]=m2c-m_step
                smwr[sn][0]=m2startw[cnt-1]
                peak = m2startw[cnt]
                left_counter = 1
                right_counter = 0
                left_or_right = 'left'
                #m1c = m1c + 0.3
                numb = 0
                while (m1c < 50 and m2c < 50 ): #and numb < 50
                    numb = numb + 1
                    previous_peak = peak  #We need to store the current peak so that we can compare it to the next peak
                    write_current_func1(m1c)
                    write_current_func2(m2c)
                    peak,peak_pow = full_osa.search_peak()
                    print("peak = " + str(peak) + " power = " + str(peak_pow))
                    if(peak_pow <= -35 or peak < 1500 or (abs(peak-previous_peak) > 0.4 and abs(peak-previous_peak) < 4.3) or abs(peak-previous_peak) > 5.6): 
                        print("f6 peak = " + str(peak) + " m1c = " + str(m1c) + " m2c = " + str(m2c))
                        peak = previous_peak
                        if (left_or_right == 'left') :m1c = m1c + m_step
                        if (left_or_right == 'right') :m2c = m2c + m_step
                        continue
                    if ((left_or_right == 'left' and abs(peak - previous_peak) < 4.3) or (left_or_right == 'right' and abs(peak - previous_peak) > 4.3)): #Are we on the left or right of the supermode?
                        left_or_right = 'left'
                        sm1l[sn][left_counter]=m1c
                        sm2l[sn][left_counter]=m2c
                        smwl[sn][left_counter]=peak
                        #print('left side m1c= ' + str(m1c) + ' m2c= ' + str(m2c) + ' peak= ' + str(peak))
                        left_counter = left_counter+1
                        m1c = m1c + m_step
                    else:
                        left_or_right = 'right'
                        sm1r[sn][right_counter]=m1c
                        sm2r[sn][right_counter]=m2c
                        smwr[sn][right_counter]=peak
                        #print('right side m1c= ' + str(m1c) + ' m2c= ' + str(m2c) + ' peak= ' + str(peak))
                        right_counter = right_counter+1
                        m2c = m2c + m_step
                m1c=sm1l[sn][0] #go back to the starting point on the graph axis so we can search for the next supermode
                m2c=sm2l[sn][0]+m_step*5
                print("m2c = " + str(m2c))
                sn=sn+1 #advance to the next supermode number
                #raw_input('end')
                full_osa.set_sampling_points(sampling_points) #set sampling points and span to see entire bandwidth again
                full_osa.set_center_wavelength(center_wl)
                full_osa.set_span(span)
                
            m2c = m2c+m_step  #this step happens until we find the next supermode
     
        sm1l[:sn][:]=sm1l[(sn-1)::-1][:] #This is just reversing the order of the supermodes so that they all go in order of wavelength
        sm2l[:sn][:]=sm2l[(sn-1)::-1][:]
        smwl[:sn][:]=smwl[(sn-1)::-1][:]
        sm1r[:sn][:]=sm1r[(sn-1)::-1][:] 
        sm2r[:sn][:]=sm2r[(sn-1)::-1][:]
        smwr[:sn][:]=smwr[(sn-1)::-1][:]
                   
        m2c=0  #set mirror 2 current back to zero
        write_current_func2(m2c)
        old_peak = [] 
        for cnt in range(170):  #This entire loop is just like the last loop but now we are scanning mirror 1 instead of two.  I am not sure why I did mirror 2 first
            if (m1c > 50 or (sn > 2 and demo == 'y')):
                break            
            write_current_func1(m1c)
            write_current_func2(m2c)
            peak,peak_pow = full_osa.search_peak()
            while (peak < 1500):
                peak,peak_pow = full_osa.search_peak()
            print peak
            if((full_osa.identity() == 'MS9740' and peak_pow <= -40) or (full_osa.identity() == 'WS6' and (peak < 1500 or (old_peak != [] and abs(peak-old_peak) > 0.4 and abs(peak-old_peak) < 4.3) or (old_peak != [] and abs(peak-old_peak) > 5.6)))): 
                peak = old_peak
            else:
                old_peak = peak
            
            m1start.append(m1c)
            m1startw.append(peak)
            if (cnt == 0): continue
            print(str(m1startw[cnt]) + ' ' + str(m1startw[cnt-1]))
            condition = abs(m1startw[cnt]-m1startw[cnt-1])
            if (condition > 10 and full_osa.identity() == 'MS9740'): #if wrap-around, stop
                full_osa.set_sampling_points(sampling_points)
                full_osa.set_center_wavelength(center_wl)
                full_osa.set_span(span)
                snlow = sn
                continue
            if (condition > 4.3):
                full_osa.set_sampling_points(251)  #reduce the sampling points due to span decrease
                full_osa.set_center_wavelength(min([m1startw[cnt],m1startw[cnt-1]])) #center the wavelength on the lower of the two wavelengths because the wavelengths will shift downward and peaks should remain within the span
                full_osa.set_span(span_short)  #reduce span to only see the two supermodes
                sm1r[sn][0]=m1c
                sm2r[sn][0]=0
                smwr[sn][0]=m1startw[cnt]
                sm1l[sn][0]=m1c-m_step
                sm2l[sn][0]=0
                smwl[sn][0]=m1startw[cnt-1]
                peak = m1startw[cnt]
                right_counter = 1
                left_counter = 0
                left_or_right = 'right'
                numb = 0
                while (m1c < 50 and m2c < 50 ): #and numb < 50
                    numb = numb + 1                        
                    previous_peak = peak
                    write_current_func1(m1c)
                    write_current_func2(m2c)
                    peak,peak_pow = full_osa.search_peak()
                    if(peak_pow <= -35 or peak < 1500 or (abs(peak-previous_peak) > 0.4 and abs(peak-previous_peak) < 4.3)  or abs(peak-previous_peak) > 5.6): 
                        peak = previous_peak
                        if (left_or_right == 'left') :m1c = m1c + m_step
                        if (left_or_right == 'right') :m2c = m2c + m_step
                        continue
                    if ((left_or_right == 'left' and abs(peak - previous_peak) < 4.3) or (left_or_right == 'right' and abs(peak - previous_peak) > 4.3)):
                        left_or_right = 'left'
                        sm1l[sn][left_counter]=m1c
                        sm2l[sn][left_counter]=m2c
                        smwl[sn][left_counter]=peak
                        left_counter = left_counter+1
                        m1c = m1c + m_step
                    else:
                        left_or_right = 'right'
                        sm1r[sn][right_counter]=m1c
                        sm2r[sn][right_counter]=m2c
                        smwr[sn][right_counter]=peak
                        right_counter = right_counter+1
                        m2c = m2c + m_step
                m1c=sm1r[sn][0]+m_step+m_step
                m2c=sm2r[sn][0]
                sn=sn+1
                full_osa.set_sampling_points(sampling_points)
                full_osa.set_center_wavelength(center_wl)
                full_osa.set_span(span)
                
            m1c = m1c+m_step
        
        np.save(path_b1 + 'sm1l',sm1l)  # save the data in case we want to test the rest of the code from this point onward
        np.save(path_b1 + 'sm2l',sm2l)
        np.save(path_b1 + 'smwl',smwl)
        np.save(path_b1 + 'sm1r',sm1r)
        np.save(path_b1 + 'sm2r',sm2r)
        np.save(path_b1 + 'smwr',smwr)
        snarray = np.array([sn, snlow, snhigh])
        np.save(path_b1 + 'snarray',snarray)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        print("end time is" + timestamp)    
    
#    raw_input('end')
    
    if (saved_data == 1):  # this is for if we want to used saved data instead of new data.  Just change this to 1 and put in the correct file name
        sm1l=np.load(path_b1 + 'sm1l.npy')
        sm2l=np.load(path_b1 + 'sm2l.npy')
        smwl=np.load(path_b1 + 'smwl.npy')
        sm1r=np.load(path_b1 + 'sm1r.npy')
        sm2r=np.load(path_b1 + 'sm2r.npy')
        smwr=np.load(path_b1 + 'smwr.npy')
        
        snarray=np.load(path_b1 + 'snarray.npy')
        print("sm1l")
        print(sm1l[:,0])
        print("sm2l")
        print(sm2l[:,0])
        print("sm1r")
        print(sm1r[:,0])
        print("sm2r")
        print(sm2r[:,0])
    plt.close("all")    
    f10 = plt.figure(10)
    ax = Axes3D(f10)
      
    s = [sum(sm1l[c][:]>0)-1 for c in range(snarray[0])]  #this is to get rid of all the zeros at the end of the data.  There may be a better way to do this.  This variable stores the number of nonzero numbers in the supermode arrays
    s2 = [sum(sm1r[c][:]>0)-1 for c in range(snarray[0])]
    
    fit_sm1l = [0]*40
    fit_sm2l = [0]*40
    fit_sm1r = [0]*40
    fit_sm2r = [0]*40

    print(snarray)
    nonzero = []
    path_was_not_lost = 1
    for c in range(snarray[0]): 
        if ( sm1l[c][:s[c]] != [] and path_was_not_lost):
            nonzero.append(c)
            fit_sm1l[c] = (np.polyfit(sm1l[c][:s[c]],smwl[c][:s[c]],2))  #Using second order polynomial to fit the supermode curves.  Mirror current vs wavelength
            print("left supermode line " + str(c) + " start = " + str(smwl[c][0]) + "end = " + str(smwl[c][s[c]]))
        if ( sm2l[c][:s[c]] != [] ):        
            fit_sm2l[c] = (np.polyfit(sm2l[c][:s[c]],smwl[c][:s[c]],2))
        if ( sm1r[c][:s2[c]] != [] ): 
            fit_sm1r[c] = (np.polyfit(sm1r[c][:s2[c]],smwr[c][:s2[c]],2))
            print("right supermode line " + str(c) + " start = " + str(smwr[c][0]) + "end = " + str(smwr[c][s2[c]]))
        if ( sm2r[c][:s2[c]] != [] ): 
            fit_sm2r[c] = (np.polyfit(sm2r[c][:s2[c]],smwr[c][:s2[c]],2))
        path_was_not_lost = 1

    m1current = np.ones(300)*-1
    m2current = np.ones(300)*-1
    
    imgfilename4 = path_b1 + 'sml'  +'_'+ datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.png'
    imgfilename5 = path_b1 + 'smr'  +'_'+ datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.png'
    imgfilename6 = path_b1 + 'original_offsets'  +'_'+ datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.png'
    imgfilename7 = path_b1 + 'optimized_laspha'  +'_'+ datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.png'
    imgfilename8 = path_b1 + 'laspha_currents'  +'_'+ datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.png'
    imgfilename9 = path_b1 + 'laspha_scatter'  +'_'+ datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.png'
    imgfilename10 = path_b1 + '3d'  +'_'+ datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.png'
    imgfilename11 = path_b1 + 'smsr'  +'_'+ datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.png'
    imgfilename12 = path_b1 + 'peak_power_with_only_one_soa'  +'_'+ datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.png'
    imgfilename13 = path_b1 + 'osa_all_peaks'  +'_'+ datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.png'
    

    #***********************************************************************************************************************************************
    #This section is where the channels are found **************************************************************************************************
    #***********************************************************************************************************************************************
        
    [normal_looking_traces, scan_between, scan_below, scan_above] = checkit_all(sm1l,sm2l,sm1r,sm2r ,s,s2, 20)
    print ([scan_between, scan_below, scan_above, nonzero, nonzero[:-1]])
    found_total = 0
    for counter in range(300): #loop thorough the ITU channels
        found_fit = 0
        #Scan for the channel at the bottom (top?) edge of the supermode transition
        
        for c in nonzero[:-1]: #loop through the supermodes
            if (scan_between[c] == 0):
                continue
            if (fit_sm1l[c+1] == [] or fit_sm1l[c] == []):
                continue
            #if (ITU_channel[counter]>smwl[c+1][0] or ITU_channel[counter]<smwl[c+1][s[c+1]] or ITU_channel[counter]>smwr[c][0] or ITU_channel[counter]<smwr[c][s[c]]): #If a channel is within the range of both sides of the supermode channel ('both sides of the road')
            #    continue
            try:
                [a1,b1,d1] = fit_sm1l[c+1] #Store the fit parameters in separate variables for the left side of the road
                [a2,b2,d2] = fit_sm1r[c] #Store the fit parameters in separate variables for the right side of the road
                a=(a1+a2)/2 #average the parameters
                b=(b1+b2)/2
                d=(d1+d2)/2-ITU_channel[counter]
                if b**2-4*a*d<0: #I was using this for error checking.  I have to use the quadratic formula in the next step and sometimes I has negative numbers in the square root.  I am still not sure why yet
        #            print(b**2-4*a*d)
                    continue
                m1c_now = (-b-math.sqrt(b**2-4*a*d))/(2*a) #Use the quadratic formula to get the mirror current for a specific wavelength 
                
                [a1,b1,d1] = fit_sm2l[c+1]
                [a2,b2,d2] = fit_sm2r[c]
            except:
                continue
            a=(a1+a2)/2
            b=(b1+b2)/2
            d=(d1+d2)/2-ITU_channel[counter]
            if b**2-4*a*d<0: 
    #            print(b**2-4*a*d)
                continue
            m2c_now = (-b-math.sqrt(b**2-4*a*d))/(2*a)
            if c == 17 and (ITU_channel[counter] == 1565.9 or ITU_channel[counter] == 1566.31):
                print("yes I got here" + str(m1c_now) + " and " + str(m2c_now))
            if(m1c_now<50 and m1c_now>0 and m2c_now<50 and m2c_now>0):            
                m1current[counter] = m1c_now #quadratic formula
                m2current[counter] = m2c_now #quadratic formula
                found_fit = 1
                print("Found wavelength: " + str(ITU_channel[counter]) + ": between " + str(c) + " and " + str(c+1) + ":" + str(m1c_now) + ":" + str(m2c_now))
                found_total = found_total+1
                break
        # SCG _ADDITION
        found_mirr1_currs = []
        found_mirr2_currs = []
        found_wls = []
        # END         
        if found_fit == 1: continue
        #Scan for the channel at the top (bottom?) edge of the supermode transition
        for c in nonzero:
            if (scan_above[c] == 1 or demo == 'y'):
                continue
            try:
                [a1,b1,d1] = fit_sm1r[c] 
                [a2,b2,d2] = fit_sm2r[c]
            except:
                continue
            d1 = d1 - (ITU_channel[counter])
            d2 = d2 - (ITU_channel[counter])
            if b1**2-4*a1*d1>0 and b2**2-4*a2*d2>0: 
                m1c_now = (-b1-math.sqrt(b1**2-4*a1*d1))/(2*a1) #+ 0.5 #0.5mA is the offset off of the supermode transition line
                m2c_now = (-b2-math.sqrt(b2**2-4*a2*d2))/(2*a2) #- 0.5
                delta_lambda = 0.005
                for loops in range(10):
                    m1c_now = m1c_now - delta_lambda/(a1*m1c_now+b1)
                    m2c_now = m2c_now + delta_lambda/(a2*m1c_now+b2)
                if(m1c_now<50 and m1c_now>1 and m2c_now<50 and m2c_now>1): 
        #                print(ITU_channel[counter])
                    m1current[counter] = m1c_now #quadratic formula
                    m2current[counter] = m2c_now #quadratic formula
                    print("Found wavelength: " + str(ITU_channel[counter]) + ": below " + str(c) + ":" + str(m1c_now) + ":" + str(m2c_now))
                    found_total = found_total+1
                    found_fit = 1
                    break
        if found_fit == 1: continue
    #        print(nonzero)                
        
        for c in nonzero:
            if (demo == 'y'):
                continue
            try:
                [a1,b1,d1] = fit_sm1l[c] 
                [a2,b2,d2] = fit_sm2l[c]
            except:
                continue
            d1 = d1 - (ITU_channel[counter])
            d2 = d2 - (ITU_channel[counter])
        #        if b1**2-4*a1*d1<0: 
        #            print(b1**2-4*a1*d1)
        #            print("1")
        #            print(a1)
        #            print(b1)
        #            print(d1)
        #            continue
        #        if b2**2-4*a2*d2<0: 
        #            print(b2**2-4*a2*d2)
        #            print("2")
        #            continue
            if b1**2-4*a1*d1>0 and b2**2-4*a2*d2>0:
                m1c_now = (-b1-math.sqrt(b1**2-4*a1*d1))/(2*a1) #- 0.9 #0.5mA is the offset off of the supermode transition line
                m2c_now = (-b2-math.sqrt(b2**2-4*a2*d2))/(2*a2) #+ 0.9
                delta_lambda = 0.005
                for loops in range(10):
                    m1c_now = m1c_now + delta_lambda/(a1*m1c_now+b1)
                    m2c_now = m2c_now - delta_lambda/(a2*m1c_now+b2)
                if(m1c_now<50 and m1c_now>1 and m2c_now<50 and m2c_now>1):  
        #            print(ITU_channel[counter])
                    m1current[counter] = m1c_now #quadratic formula
                    m2current[counter] = m2c_now #quadratic formula
                    print("Found wavelength: " + str(ITU_channel[counter]) + " :above " + str(c) + ":" + str(m1c_now) + ":" + str(m2c_now))
                    found_mirr1_currs.append(m1c_now)
                    found_mirr2_currs.append(m2c_now)
                    found_wls.append(str(ITU_channel[counter]))
                    found_fit = 1
                    found_total = found_total+1
                    break
        if found_fit == 1: continue
        
        print("Did not find: " + str(ITU_channel[counter]))
    print(found_total)
    f4 = plt.figure(4) #plot of the supermodes as lines and also the ITU wavelengths as dots.  Code for this graph is the next two loops
    for c in nonzero:  
        if normal_looking_traces[c]==1:
            plt.plot(sm1l[c][:s[c]],sm2l[c][:s[c]])  #plot of the supermodes as lines and also the ITU wavelengths as dots. This line adds the lines.
    plt.plot(m1current[m1current>0],m2current[m1current>0],'p')    #plot of the supermodes as lines and also the ITU wavelengths as dots.  This line adds the dots. Code for this graph is the previous two loops
    plt.xlabel('Mirror 1 current (mA)')
    plt.ylabel('Mirror 2 current (mA)')
    f4.savefig(imgfilename4)
    
    f5 = plt.figure(5)  #same as previous plot, but with using the right side of the road instead of left.  Pretty similar
    for c in nonzero:
        if normal_looking_traces[c]==1:
            plt.plot(sm1r[c][:s2[c]],sm2r[c][:s2[c]])
    plt.plot(m1current[m1current>0],m2current[m1current>0],'p')
    plt.xlabel('Mirror 1 current (mA)')
    plt.ylabel('Mirror 2 current (mA)')
    f5.savefig(imgfilename5)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print("time is" + timestamp)    
    
    if (continue_measurements == '0'):
        print('Ended after mapping')
        return continue_measurements
        
    ax.plot(m1current[m1current>0],m2current[m1current>0],ITU_channel[m1current>0],'o')  #this is for the 3d plot
    f10.savefig(imgfilename10)
    
    #laspha_peak = []
    save_data2 = []
    best_laspha = np.ones(300)*-1  #initialization.  This is a way to get an array of zeros
    best_offset = np.ones(300)*-1 #initialization.  This is a way to get an array of tens.  Ten is not needed, but I just needed a large number
    good_peak = np.ones(300)*-1
    smsr = np.ones(300)*-1
    peak_power = np.ones(300)*-1
    offset = np.ones(300)*-1
    laspha_peak_offset = np.ones(300)*-1
    save_data3 = []
    osa_trace = []
    osa_trace_save = []
   
    f13 = plt.figure(13, facecolor='w', edgecolor='k')#, figsize=(8, 6), dpi=300
    for counter in range(300):  #This loop optimizes the laspha.  It is pretty simple and could be made more efficient.  I think the supermode code takes longer though so that code should mayber be optimized first
        if (m1current[counter]>50 or m2current[counter]>50 or m1current[counter]<0):  #for some reason I am getting currents greater than 50.  This line should not be necessary and there is a run-time bug somewhere
            save_data2.append([m1current[counter],m2current[counter],ITU_channel[counter],good_peak[counter],offset[counter],abs(offset[counter])<0.2,best_laspha[counter],smsr[counter],peak_power[counter]])
            save_data3.append([ITU_index[counter],ITU_channel[counter],m1current[counter],m2current[counter],best_laspha[counter]])
            continue
        
        #Set a reduced span and sampling
        full_osa.set_sampling_points(251)
        full_osa.set_center_wavelength(ITU_channel[counter])
        full_osa.set_span(2) 
        full_osa.set_resolution(0.03)
        full_osa.set_video_bandwidth(100000)
        
        write_current_func1(m1current[counter])
        write_current_func2(m2current[counter])
        good_peak[counter],peak_pow = full_osa.search_peak()
        offset[counter] = ITU_channel[counter]-good_peak[counter]
        for current_laspha in np.linspace(0.5,6.5,30):
            write_laspha_current(current_laspha)
            current_peak,peak_pow = full_osa.search_peak()
            laspha_peak_offset[counter] = current_peak-ITU_channel[counter]
            if (abs(current_peak-ITU_channel[counter])<abs(best_offset[counter]) or current_laspha == 0):
                best_offset[counter] = current_peak-ITU_channel[counter]
                best_laspha[counter] = current_laspha
                
        #enlarge span and sampling then acquire smsr and peak power***************************************************
        center_wl = 1555.0
        span = 70
        resolution = 0.03
        sampling_points=2001
        full_osa.set_video_bandwidth(200)
        full_osa.set_sampling_points(sampling_points)
        full_osa.set_center_wavelength(center_wl)
        full_osa.set_span(span)
        write_laspha_current(best_laspha[counter])
        full_osa.sweep_single()
        time.sleep(10)      
        smsr[counter] = full_osa.read_smsr()
        output = full_osa.readpeak()
        peak_power[counter] = output[0]['power']
        osa_trace = np.array(full_osa.read_trace_memory())
        if osa_trace_save == []: osa_trace_save.append(osa_trace[:,0])
        osa_trace_save.append(osa_trace[:,1])
        plt.plot(osa_trace[:,0],osa_trace[:,1])
        #***************************************************************
        
        save_data2.append([m1current[counter],m2current[counter],ITU_channel[counter],good_peak[counter],offset[counter],abs(offset[counter])<0.2,best_laspha[counter],smsr[counter],peak_power[counter]])
        save_data3.append([ITU_index[counter],ITU_channel[counter],m1current[counter],m2current[counter],best_laspha[counter]])
    
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Power (dBm)')
    f13.savefig(imgfilename13)    #OSA spectra all peaks
    print (np.size(ITU_channel[m1current>0]))
    print (np.size(offset[m1current>0]))
    f6 = plt.figure(6)  #Plot the original offsets
    plt.bar(ITU_channel[m1current>0],offset[m1current>0], width = 0.2)
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Original offsets from ITU (nm)')
    f6.savefig(imgfilename6)
    f7 = plt.figure(7)  #Plot the offsets after optimising the laser phase
    plt.bar(ITU_channel[m1current>0],best_offset[m1current>0], width = 0.2)
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Offsets from ITU after LasPha optimization (nm)')
    f7.savefig(imgfilename7)
    f8 = plt.figure(8)  #Plot the laser phase currents that were required
    plt.bar(ITU_channel[m1current>0],best_laspha[m1current>0], width = 0.2)
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Currents to optimize LasPha (mA)')
    f8.savefig(imgfilename8)
    f9 = plt.figure(9)  #Scatter plot of the laser phase currents that were required for each of the original offsets
    plt.plot(best_laspha[m1current>0],offset[m1current>0],'o')
    plt.xlabel('Current required on LasPha (mA)')
    plt.ylabel('Original offsets from ITU (nm)')
    f9.savefig(imgfilename9)
    f11 = plt.figure(11)  #Scatter plot of the laser phase currents that were required for each of the original offsets
    plt.plot(ITU_channel[m1current>0],smsr[m1current>0],'o')
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('SMSR (dB)')
    f11.savefig(imgfilename11)
    f12 = plt.figure(12)  #Scatter plot of the laser phase currents that were required for each of the original offsets
    plt.plot(ITU_channel[m1current>0],peak_power[m1current>0],'o')
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Peak power with only one SOA (dBm)')
    f12.savefig(imgfilename12)
    
    
    #Save the osa traces
    np.savetxt(path_b1 + 'OSA_traces' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.csv', osa_trace_save, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
        
    
    #Save the data
    h = ""
    for i in range(9):
        h = h + "\n" #Header lines
    h = h + 'Mirr1_current,M2 Current,Mapped Channel,Peak without LasPha,Offset without LasPha,Points within 0.2,LasPha_current' #,power
    np.savetxt(path_b1 + 'wavelength_search_data' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.csv', save_data2, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
    
    h = ""
    for i in range(9):
        h = h + "\n" #Header lines
    h = h + 'itu_index,itu_wavelength,Mirr1_current,Mirr2_current,LasPha_current' #,power
    np.savetxt(output_filename, save_data3, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
    return continue_measurements
    
def mirror_sweep_grid_fitter(input_mirror1_filename, 
                             input_mirror2_filename, 
                             output_filename, 
                             current_deviation=1.0, 
                             min_coverage=0.4):
    """Finds mirror currents for ITU grid by analyzing mirror sweep data files. Takes peak files from each mirror, plots current vs. wavelength and fits curves. For each ITU channel, finds current on fit curves for ITU wavelength for each mirror and records to output data file.
    
    :param input_mirror1_filename: Path to CSV filename with OSA peaks from mirror seach on mirror 1. Columns: current,wavelength,power,LasPha_current
    :type input_mirror1_filename: str
    :param input_mirror2_filename: Path to CSV filename with OSA peaks from mirror seach on mirror 2. Columns: current,wavelength,power,LasPha_current
    :type input_mirror2_filename: str
    :param output_filename: Path to output ITU CSV file. Columns: itu_index,itu_wavelength,Mirr1_current,Mirr2_current,LasPha_current
    :type output_filename: str
    :param current_deviation: Maximum allowed deviation from ITU reference. This is expected to improve with a later test using Laser Phase to get exactly on the ITU grid
    :type current_deviation: float
    :param min_coverage: Minimum factor of coverage over a fit line to be valid. For each fit line, if the number of actual data points recorded along the fit is less by factor than the number ideally, reject fit line.
    :type min_coverage: float
    """
    def fit_mirror_itu(data, current_deviation, itu_index_list, min_coverage):
        start_wavelength_array = []
        for item in data:
            if item["current"] == 0:
                start_wavelength_array.append(item["wavelength"])
                
        line_list = []
                
        for start_wavelength in start_wavelength_array:
            last_wavelength = start_wavelength
            x = [0]
            y = [start_wavelength]
            coverage_num = 0
            current_list = list(set(data["current"]))
            for current in current_list:
                for item in data:
                    if item["current"] == current and (last_wavelength - current_deviation < item["wavelength"] < last_wavelength + current_deviation):
                        x.append(current)
                        y.append(item["wavelength"])
                        last_wavelength = item["wavelength"]
                        coverage_num += 1
                        continue
            if (coverage_num / len(current_list)) > min_coverage :
                line_list.append([x, y])
            
        polyfit_list = []
        for line in line_list:
            polyfit_list.append(np.polyfit(line[0], line[1], 2))
            
        #target_wavelength = 1585.0
        #samplepoly = [  2.28171674e-03,  -2.17446512e-01,   1.59161978e+03]
        #samplepoly[2] = samplepoly[2] - target_wavelength
        #roots = np.roots(samplepoly)
        #print(type(roots[0]))
        itu_list = []
        
        for itu_index in itu_index_list:
            wavelength = itu_wavelength(itu_index)
            target_currents = []
            for polyfit in polyfit_list:
                mod_polyfit = polyfit.copy()
                mod_polyfit[2] =  polyfit[2] - wavelength
                roots = np.roots(mod_polyfit)
            #     print(roots)
            #     print(np.imag(roots))
            #     print(np.imag(roots[0]))
                for root in roots:
                    if np.imag(root) == 0 and np.real(root) > 0:
                        target_currents.append(np.real(root))
            if len(target_currents) == 0:
                itu_list.append(-1)
            else:
                itu_list.append(min(target_currents))
        return itu_list
            
    mirr1_data = np.genfromtxt(input_mirror1_filename, skip_header=9, delimiter=",", names=True)
    mirr2_data = np.genfromtxt(input_mirror2_filename, skip_header=9, delimiter=",", names=True)
    
    output_data = np.genfromtxt(output_filename, skip_header=9, delimiter=",", names=True)
    
    itu_index_list = output_data["itu_index"]
    mirr1_currents = fit_mirror_itu(mirr1_data, current_deviation, itu_index_list, min_coverage)
    mirr2_currents = fit_mirror_itu(mirr2_data, current_deviation, itu_index_list, min_coverage)
    
    h = itu_header()
    save_data = []
    # 'itu_index,itu_wavelength,Mirr1_current,Mirr2_current,LasPha_current'
    for index in range(len(itu_index_list)):
        if mirr1_currents[index] == -1 or mirr2_currents[index] == -1:
            save_data.append([itu_index_list[index], itu_wavelength(itu_index_list[index]), -1, -1, 0])
        else:
            save_data.append([itu_index_list[index], itu_wavelength(itu_index_list[index]), mirr1_currents[index], mirr2_currents[index], 0])
    np.savetxt(output_filename, save_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)

def verify_mirror_sweep_table(input_filename, 
                              output_filename, 
                              test_station, 
                              full_osa, 
                              wavemeter, 
                              connection_loss=3.5, 
                              laser_TEC=None, 
                              mirror1_offset=0.0, 
                              mirror2_offset=0.0, 
                              mirror1_ratio=1.0, 
                              mirror2_ratio=1.0):
    """Verify results from mirror sweep test. For each ITU grid entry filled out, record wavelength, power, and SMSR.
    
    :param input_filename: Path to CSV ITU filename from mirror search. Columns: itu_index,itu_wavelength,Mirr1_current,Mirr2_current,LasPha_current
    :type input_filename: str
    :param output_filename: Path to CSV output filename. Columns: itu_index,itu_wavelength,Mirr1_current,Mirr2_current,LasPha_current,wavemeter_power,wavemeter_wavelength,smsr
    :type output_filename: str
    :param test_station: Current device laser sections I/O
    :type test_station: LaserSections
    :param full_osa: OSA hooked to laser output
    :type full_osa: testsuite.instruments.MS9740.OSA
    :param wavemeter: Initialized wavemeter to get wavelength and power data
    :type wavemeter: instruments.HP86120B.OSA
    :param connection_loss: dB loss of connectors/splitters
    :type connection_loss: float
    :param laser_TEC: Laser TEC controller, used to monitor laser temp and shutdown if a temp runaway is detected
    :type laser_TEC: instruments.LDT5910B.TEC
    :param mirror1_offset: Offest to add to Mirror 1 current from input table. Used for debugging
    :type mirror1_offset: float
    :param mirror2_offset: Offest to add to Mirror 2 current from input table. Used for debugging
    :type mirror2_offset: float
    :param mirror1_ratio: Ratio to apply to Mirror 1 current before applying offset. Used for debugging
    :type mirror1_ratio: float
    :param mirror2_ratio: Ratio to apply to Mirror 2 current before applying offset. Used for debugging
    :type mirror2_ratio: float
    """
    wavetable_data = np.genfromtxt(input_filename, skip_header=9, delimiter=",", names=True)
    test_station.zero_all()
    test_station.gain1.write_static_current()
    test_station.soa1.write_static_current()
    test_station.soa2.write_static_current()
    test_station.phase1.write_static_current()
    
    save_data = []
    for wavetable_item in wavetable_data:
        if wavetable_item["Mirr1_current"] == -1:
            item = []
            item.append(wavetable_item["itu_index"])
            item.append(wavetable_item["itu_wavelength"])
            item.append(-1)
            item.append(-1)
            item.append(-1)
            item.append(-1)
            item.append(-1)
            item.append(-1)
            save_data.append(item)
        else:
            test_station.mirror1.write_current((wavetable_item["Mirr1_current"] * mirror1_ratio) + mirror1_offset)
            test_station.mirror2.write_current((wavetable_item["Mirr2_current"] * mirror2_ratio) + mirror2_offset)
            test_station.laser_phase.write_current(wavetable_item["LasPha_current"])
            
            time.sleep(0.2)
            full_osa.sweep_single()
            full_osa.wait_for_sweepcomplete()
            time.sleep(0.5)
            peakfound = False
            while not peakfound:
                try:
                    check_tec(laser_TEC, test_station)
                    peakdata = wavemeter.readpeak()
                    peakfound = True
                except socket.timeout:
                    pass # Loop through peak finder again
            
            wavemeter_power = peakdata[0]["power"]
            wavemeter_wavelength = peakdata[0]["wavelength"]
            SMSR = full_osa.read_smsr()
            
            item = []
            item.append(wavetable_item["itu_index"])
            item.append(wavetable_item["itu_wavelength"])
            item.append(wavetable_item["Mirr1_current"])
            item.append(wavetable_item["Mirr2_current"])
            item.append(wavetable_item["LasPha_current"])
            item.append(wavemeter_power)
            item.append(wavemeter_wavelength)
            item.append(SMSR)
            save_data.append(item)
            
    h = itu_header() + ',wavemeter_power,wavemeter_wavelength,smsr'
    np.savetxt(output_filename, save_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
    
def laser_phase_finder_etalon(input_filename, 
                              output_filename, 
                              test_station,  
                              laser_phase_min=0.0, 
                              laser_phase_max=10.0, 
                              laser_phase_step=0.1, 
                              debug_filename=None):
    """Initial procedure to find laser phase current via etalon. Sweeps laser phase current, recording photocurrent on etalon detector, writing maximum to file. Completely untested.
    
    :param input_filename: Path to CSV ITU filename. Columns: itu_index,itu_wavelength,Mirr1_current,Mirr2_current
    :type input_filename: str
    :param output_filename: Path to CSV output filename. Columns: itu_index,itu_wavelength,Mirr1_current,Mirr2_current,LasPha_current
    :type output_filename: str
    :param test_station: Current device laser sections I/O
    :type test_station: LaserSections
    :param laser_phase_min: Minimum laser phase current to sweep over
    :type laser_phase_min: float
    :param laser_phase_max: Maximum laser phase current to sweep over
    :type laser_phase_max: float
    :param laser_phase_step: Laser phase step current to sweep over
    :type laser_phase_step: float
    :param debug_filename: Path to CSV output debug filename with entire sweep results. Columns: itu_index,itu_wavelength,Mirr1_current,Mirr2_current,LasPha_current,photocurrent
    :type debug_filename: str
    """
    wavetable_data = np.genfromtxt(input_filename, skip_header=9, delimiter=",", names=True)
    test_station.zero_all()
    test_station.gain1.write_static_current()
    test_station.soa1.write_static_current()
    test_station.soa2.write_static_current()
    test_station.detector.write_static_voltage()
    
    save_data = []
    debug_data = []
    
    for wavetable_item in wavetable_data:
        test_station.mirror1.write_current(wavetable_item["Mirr1_current"])
        test_station.mirror1.write_current(wavetable_item["Mirr2_current"])
        
        photocurrent_list = []
        laser_phase_current_list = np.arange(laser_phase_min, laser_phase_max, laser_phase_step)
        for laser_phase in laser_phase_current_list:
            test_station.laser_phase.write_current(laser_phase)
            
            photocurrent = test_station.etalon_detector.read_current()
            photocurrent_list.append(photocurrent)
            debug_data.append([wavetable_item["itu_index"], wavetable_item["itu_wavelength"], wavetable_item["Mirr1_current"], wavetable_item["Mirr2_current"], laser_phase, photocurrent])
        
        laser_phase_setpoint = laser_phase_current_list[np.argmax(photocurrent_list)]
        save_data.append([wavetable_item["itu_index"], wavetable_item["itu_wavelength"], wavetable_item["Mirr1_current"], wavetable_item["Mirr2_current"], laser_phase_setpoint])
        
    h = itu_header()
    np.savetxt(output_filename, save_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
    if debug_filename is not None:
        h = itu_header() + ',photocurrent'
        np.savetxt(debug_filename, debug_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
        
def LIV_SOA(output_filename, 
            test_station, 
            gain_min=0.0, 
            gain_max=150.0, 
            gain_step=1.0, 
            output_img_filename=None):
    """Take LIV test on SOAs
    
    :param output_filename: Path to CSV output filename. Columns: gain_current,gain_voltage,soa1_current,soa2_current
    :type output_filename: str
    :param test_station: Current device laser sections I/O
    :type test_station: LaserSections
    :param gain_min: Minimum gain current to sweep over
    :type gain_min: float
    :param gain_max: Maximum gain current to sweep over
    :type gain_max: float
    :param gain_step: Gain step current to sweep over
    :type gain_step: float
    :param output_img_filename: Path to PNG plot.
    :type output_img_filename: str
    """
    def SOAliv_plot(x, yl, y2, yr, Ith, Vth, Rs,slopeeff1, slopeeff2, PmaxSOA1, PmaxSOA2, units, x_label, yl_label, yr_label, title, imagefilename):  # For LIV SOA only
       
        fig, ax1 = plt.subplots()
        ax1.plot(x, yl, 'b-')
        ax1.plot(x, y2, '-')
        ax1.set_xlabel(x_label)
        # Make the y-axis label and tick labels match the line color.
        ax1.set_ylabel(yl_label, fontsize = 12, color = 'b')
        ax1.set_title(title)
        ax1.grid(True)
        for tl in ax1.get_yticklabels():
            tl.set_color('b')
        ax1.axis([0, max(x), 0, PmaxSOA1*1.2])  # photocurrent 
        ax2 = ax1.twinx()    
        ax2.plot(x, yr, 'k-')
        ax2.set_ylabel(yr_label, color = 'k')
        for tl in ax2.get_yticklabels():
            tl.set_color('k')
        string = 'Ith = ' + str(Ith) + 'mA Vth = ' + str(Vth) + 'V Rs = ' + str(Rs) + 'ohms'  # string for insertion into plot
        ax1.text(0.05, .9, string,
            verticalalignment='top', horizontalalignment='left',
            transform=ax1.transAxes,
            color='black', fontsize=12)
        string2 = 'SlopeEff1 = ' + str(slopeeff1) + 'mA/mA SlopeEff2 = ' + str(slopeeff2) + 'mA/mA'
        ax1.text(0.05, .85, string2,
            verticalalignment='top', horizontalalignment='left',
            transform=ax1.transAxes,
            color='black', fontsize=12)
        string3 = 'PmaxSOA1 = ' + str(PmaxSOA1) + 'mA PmaxSOA2 = ' + str(PmaxSOA2) + 'mA'  # string for insertion into plot
        ax1.text(0.05, .8, string3,
            verticalalignment='top', horizontalalignment='left',
            transform=ax1.transAxes,
            color='black', fontsize=12)
        ax2.axis([0, max(x), 0, max(yr)*1.2])  # photocurrent 
    
        formatter = ticker.EngFormatter(unit = units, places = 1)
        formatter.ENG_PREFIXES[-6] = 'u'
        #ax1.yaxis.set_major_formatter(formatter)
        #fig.show()
        
        fig.savefig(imagefilename)
    
    test_station.zero_all()
    test_station.soa1.write_static_voltage()
    test_station.soa2.write_static_voltage()
    
    save_data=[]
    for current in np.arange(gain_min, gain_max, gain_step):
        test_station.gain1.write_current(current)
        save_data.append([current, test_station.gain1.read_voltage(), test_station.soa1.read_current(), test_station.soa2.read_current()])
        
    transpose_data = list(zip(*save_data))
    current = transpose_data[0]
    gain_voltage = transpose_data[1]
    soa1_current = transpose_data[2]
    soa2_current = transpose_data[3]
    
    ## Extract SOA current values only till 1 mA and look for threshold among those values as the laser is turned on by then
    ## This is to ensure that kinks that may appear at higher Gain Section biases don't affect threshold determination
    soa_t = []
    soa_i_a = np.array(soa1_current)
    soa1_i_a = np.array(soa1_current)
    soa2_i_a = np.array(soa2_current)
    
    for curs in soa1_i_a:
        if (np.absolute(curs) <= 0.8):
            soa_t.append(np.absolute(curs))
            
    SOA1 = -soa1_i_a
    SOA2 = -soa2_i_a
    
    # Calculate Parameters
    threshold_index = get_threshold_index(soa_t,gain_step) # get threshold array index
    Vth = np.around(gain_voltage[threshold_index],3)  # Calculate Voltage @ threshold
    Ith = current[threshold_index]*1000  # Calculate Current @ threshold in mA
    fit = np.polyfit(current[threshold_index:threshold_index + 10],gain_voltage[threshold_index:threshold_index + 10], 2, rcond=None, full=False, w=None, cov=False)
    fit2 = np.polyfit(current[threshold_index:threshold_index + 10],SOA1[threshold_index:threshold_index + 10], 2, rcond=None, full=False, w=None, cov=False) 
    fit3 = np.polyfit(current[threshold_index:threshold_index + 10],SOA2[threshold_index:threshold_index + 10], 2, rcond=None, full=False, w=None, cov=False)
    Rs = np.around(fit[1],3) # need to calculate this 
    slopeeff1 = np.around(fit2[1],3)
    slopeeff2 = np.around(fit3[1],3)
    PmaxSOA1 = np.around(np.amax(SOA1),3)           # Calculate Maximum Photocurrent in SOA 1
    PmaxSOA2 = np.around(np.amax(SOA2),3)           # Calculate Maximum Photocurrent in SOA 2
    
    threshold_from_soa = current[threshold_index]
    
    
    h = "Vth," + format(Vth) + '\n'
    h = h + "Ith," + format(Ith) + '\n'
    h = h + "Rs," + format(Rs) + '\n'
    h = h + "Slope_eff_1" + format(slopeeff1) + '\n'
    h = h + "Slope_eff_2" + format(slopeeff2) + '\n'
    h = h + "Pmax_soa1" + format(PmaxSOA1) + '\n'
    h = h + "Pmax_soa2" + format(PmaxSOA2) + '\n'
    h = h + "threshhold_soa" + format(threshold_from_soa) + '\n'
    h = ("\n" * 1) + "gain_current,gain_voltage,soa1_current,soa2_current"
    np.savetxt(output_filename, save_data, header=h, delimiter=',', comments='', fmt=FORMAT_STRING_PERCENT)
    # Add plotting
    if output_img_filename is not None:
        SOAliv_plot(current, SOA1, SOA2, gain_voltage, Ith, Vth, Rs, slopeeff1, slopeeff2, PmaxSOA1, PmaxSOA2, 'mA', 'Gain Section Current (mA)','Photocurrent (mA)', 'Gain Section Voltage (V)', 'LIV (Into SOA1 and SOA2)', output_img_filename)
    
def get_threshold_index(power_monitor, step):
    """Returns threshhold index. Used exclusively for LIV plots."""
    first_derivative = np.gradient(power_monitor, step)
    second_derivative = np.gradient(first_derivative, step)
    return np.argmax(second_derivative)    
    
def LIV_IS(output_filename, 
            test_station, 
            power_monitor, 
            gain_min=0.0, 
            gain_max=150.0, 
            gain_step=1.0, 
            output_img_filename=None):
    """Take LIV test on integrating sphere
    
    :param output_filename: Path to CSV output filename. Columns: gain_current,gain_voltage,onchip_detector,is_detector
    :type output_filename: str
    :param test_station: Current device laser sections I/O
    :type test_station: LaserSections
    :param gain_min: Minimum gain current to sweep over
    :type gain_min: float
    :param gain_max: Maximum gain current to sweep over
    :type gain_max: float
    :param gain_step: Gain step current to sweep over
    :type gain_step: float
    :param output_img_filename: Path to output PNG plot
    :type output_img_filename: str
    """
    
    def ISliv_plot(x, yl, yr, Ith, Vth, Rs,slopeeff, Pmax, units, x_label, yl_label, yr_label, title,imagefilename):  # For LIV SOA only
       
        fig, ax1 = plt.subplots()
        ax1.plot(x, yl, 'b-')
        #ax1.plot(x, y2, '-')
        ax1.set_xlabel(x_label)
        # Make the y-axis label and tick labels match the line color.
        ax1.set_ylabel(yl_label, fontsize = 12, color = 'b')
        ax1.set_title(title)
        ax1.grid(True)
        for tl in ax1.get_yticklabels():
            tl.set_color('b')
        ax1.axis([0, max(x), 0, Pmax*1.2])  # photocurrent 
        ax2 = ax1.twinx()    
        ax2.plot(x, yr, 'k-')
        ax2.set_ylabel(yr_label, color = 'k')
        for tl in ax2.get_yticklabels():
            tl.set_color('k')
        string = 'Ith = ' + str(Ith) + 'mA Vth = ' + str(Vth) + 'V Rs = ' + str(Rs) + 'ohms'  # string for insertion into plot
        ax1.text(0.05, .9, string,
            verticalalignment='top', horizontalalignment='left',
            transform=ax1.transAxes,
            color='black', fontsize=12)
        string2 = 'SlopeEff = ' + str(slopeeff) + 'mW/mA'
        ax1.text(0.05, .85, string2,
            verticalalignment='top', horizontalalignment='left',
            transform=ax1.transAxes,
            color='black', fontsize=12)
        string3 = 'Pmax = ' + str(Pmax) + 'mW'  # string for insertion into plot
        ax1.text(0.05, .8, string3,
            verticalalignment='top', horizontalalignment='left',
            transform=ax1.transAxes,
            color='black', fontsize=12)
        ax2.axis([0, max(x), 0, max(yr)*1.2])  # photocurrent 
    
        formatter = ticker.EngFormatter(unit = units, places = 1)
        formatter.ENG_PREFIXES[-6] = 'u'
        #ax1.yaxis.set_major_formatter(formatter)
        #fig.show()
        
        fig.savefig(imagefilename)
    
    test_station.zero_all()
    test_station.soa1.write_static_current()
    test_station.soa2.write_static_current()
    test_station.detector.write_static_voltage()
    
    save_data=[]
    for current in np.arange(gain_min, gain_max, gain_step):
        test_station.gain1.write_current(current)
        save_data.append([current, test_station.gain1.read_voltage(), test_station.detector.read_current(), power_monitor.read_value()])
        
    transpose_data = list(zip(*save_data))
    current = transpose_data[0]
    gain_voltage = transpose_data[1]
    detector = transpose_data[2]
    power_monitor = transpose_data[3]
        
    # Calculate Parameters
    threshold_index = get_threshold_index(power_monitor, gain_step) # get threshold array index
    Vth = np.around(gain_voltage[threshold_index],3)  # Calculate Voltage @ threshold
    Ith = current[threshold_index]  # Calculate Current @ threshold in mA
    fit = np.polyfit(current[threshold_index:threshold_index + 10],gain_voltage[threshold_index:threshold_index + 10],2, rcond=None, full=False, w=None, cov=False)
    fit2 =np.polyfit(current[threshold_index:threshold_index + 10],power_monitor[threshold_index:threshold_index + 10],2, rcond=None, full=False, w=None, cov=False) 
    #fit3 =polyfit(Current[threshold_index:threshold_index + 10],SOA2[threshold_index:threshold_index + 10],2, rcond=None, full=False, w=None, cov=False)
    Rs = np.around(fit[1],3) # need to calculate this 
    slopeeff = np.around(fit2[1],3)    
    Pmax = np.around(np.amax(power_monitor),3)           # Calculate Maximum Photocurrent in SOA 1
        
    h = "Vth," + format(Vth) + '\n'
    h = h + "Ith," + format(Ith) + '\n'
    h = h + "Rs," + format(Rs) + '\n'
    h = h + "Slope_eff" + format(slopeeff) + '\n'
    h = h + "Pmax" + format(Pmax) + '\n'
    h = ("\n" * 4) + "gain_current,gain_voltage,onchip_detector,is_detector"
    np.savetxt(output_filename, save_data, header=h, delimiter=',', comments='', fmt=FORMAT_STRING_PERCENT)
    # Add plotting
    if output_img_filename is not None:
        ISliv_plot(current, power_monitor, gain_voltage, Ith, Vth, Rs, slopeeff, Pmax, 'A', 'Gain Section Current (mA)', 'Power (mW)', 'Gain Section Voltage (V)', 'LIV (Integrating sphere)', output_img_filename) 
    
def IV_curve(output_filename, 
             input_function, 
             input_title, 
             output_function, 
             output_title, 
             input_min, 
             input_max, 
             input_step, 
             output_img_filename=None, 
             progress_callback=None, 
             plot_widget=None):
    """Take an IV curve over a generic function, saving CSV data and plot.
    
    :param output_filename: Path to CSV output filename. Columns are titles by paramaters input_title,output_title
    :type output_filename: str
    :param input_function: Function that takes a single input paramater to be swept over for IV
    :type input_function: function
    :param input_title: Title of input function, used to label plots and output column names
    :type input_title: str
    :param output_function: Function that returns a single float value to be recorded on each iteration of IV sweep
    :type output_function: function
    :param output_title: Title of output function, used to label plots and output column names
    :type output_title: str
    :param input_min: Minimum to input function to sweep over
    :type input_min: float
    :param input_max: Maximum to input function to sweep over
    :type input_max: float
    :param input_step: Step value for input function to sweep over
    :type input_step: float
    :param output_img_filename: Path to output PNG plot
    :type output_img_filename: str
    :param progress_callback: Function callback to track progress. Has parameters current_progress, max_progress
    :type progress_callback: function
    :param plot_widget: QT widget to display output plot when sweep is finished. Widget must have axes and fig properties
    :type plot_widget: matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg
    """
    # NOTE: This function does not zero the laser, either before or after measuring!
    if not os.path.exists(os.path.dirname(output_filename)):
        os.makedirs(os.path.dirname(output_filename))
    
    save_data = []
    iterator = np.arange(input_min, input_max, input_step)
    iterator_length = len(iterator)
    try:
        for index, input_value in enumerate(iterator):
            input_function(input_value)
            save_data.append([input_value, output_function()])
            if progress_callback is not None:
                progress_callback(index + 1, iterator_length)
    finally:
        h = ("\n" * 9) + input_title + ',' + output_title
        np.savetxt(output_filename, save_data, header=h, delimiter=',', comments='', fmt=FORMAT_STRING_PERCENT)
        if output_img_filename is not None:
            #fig = plt.gcf()
            #axes = plt.gca()
            plot_list = list(zip(*save_data)) # This takes the transpose of the data set
            plt.xlabel(input_title)
            plt.ylabel(output_title)
            plt.plot(plot_list[0], plot_list[1])
            plt.grid(True)
#             for tl in plt.yticklabels():
#                 tl.set_color('b')
            plt.savefig(output_img_filename)
            plt.close()
        if plot_widget is not None:
            fig = plot_widget.fig
            axes = plot_widget.axes
            plot_list = list(zip(*save_data)) # This takes the transpose of the data set
            axes.set_xlabel(input_title)
            axes.set_ylabel(output_title)
            axes.plot(plot_list[0], plot_list[1])
            plot_widget.draw()
            plt.close()
        
def IV_all_sections(output_folder, 
                    test_station, 
                    filename_suffix=''):
    """Take IV curves over all electrode. Sweep values are baked into this function, should be updated to avoid baking in paramaters.
    
    :param output_folder: Path to folder to store all IV sweep data files and plot image files
    :type output_folder: str
    :param test_station: Current device laser sections I/O
    :type test_station: LaserSections
    :param filename_suffix: Suffix to add to all IV data/plot files immediately before the filename extension. Usually used to append a timestamp
    :type filename_suffix: str
    """
    if output_folder[-1] != os.sep:
        output_folder = output_folder + os.sep
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    def iv_prep(test_station, electrode):
        test_station.set_output_on_all(False)
        electrode.set_output_on(True)
    
    iv_prep(test_station, test_station.mirror1)
    IV_curve(output_folder + 'Mirror1' + filename_suffix + '.csv',test_station.mirror1.write_current, 'mirror1_current', test_station.mirror1.read_voltage, 'mirror1_voltage', 0.0, 50.0, 1.0, output_folder + 'Mirror1' + filename_suffix + '.png')
    iv_prep(test_station, test_station.mirror2)
    IV_curve(output_folder + 'Mirror2' + filename_suffix + '.csv',test_station.mirror2.write_current, 'mirror2_current', test_station.mirror2.read_voltage, 'mirror2_voltage', 0.0, 50.0, 1.0, output_folder + 'Mirror2' + filename_suffix + '.png')
    iv_prep(test_station, test_station.gain1)
    IV_curve(output_folder + 'Gain1' + filename_suffix + '.csv',test_station.gain1.write_current, 'gain1_current', test_station.gain1.read_voltage, 'gain1_voltage', 0.0, 100.0, 1.0, output_folder + 'Gain1' + filename_suffix + '.png')
    iv_prep(test_station, test_station.soa1)
    IV_curve(output_folder + 'SOA1' + filename_suffix + '.csv',test_station.soa1.write_current, 'soa1_current', test_station.soa1.read_voltage, 'soa1_voltage', 0.0, 80.0, 1.0, output_folder + 'SOA1' + filename_suffix + '.png')
    iv_prep(test_station, test_station.soa2)
    IV_curve(output_folder + 'SOA2' + filename_suffix + '.csv',test_station.soa2.write_current, 'soa2_current', test_station.soa2.read_voltage, 'soa2_voltage', 0.0, 80.0, 1.0, output_folder + 'SOA2' + filename_suffix + '.png')
    iv_prep(test_station, test_station.laser_phase)
    IV_curve(output_folder + 'LasPha' + filename_suffix + '.csv',test_station.laser_phase.write_current, 'laser_phase_current', test_station.laser_phase.read_voltage, 'laser_phase_voltage', 0.0, 10.0, 0.1, output_folder + 'LasPha' + filename_suffix + '.png')
    iv_prep(test_station, test_station.phase1)
    IV_curve(output_folder + 'Phase1' + filename_suffix + '.csv',test_station.phase1.write_current, 'phase1_current', test_station.phase1.read_voltage, 'phase1_voltage', 0.0, 15.0, 0.1, output_folder + 'Phase1' + filename_suffix + '.png')
    iv_prep(test_station, test_station.modulator1)
    IV_curve(output_folder + 'Modulator1' + filename_suffix + '.csv',test_station.modulator1.write_voltage, 'mod1_voltage', test_station.modulator1.read_current, 'mod1_current', -4.0, 2.0, 0.1, output_folder + 'Modulator1' + filename_suffix + '.png')
    iv_prep(test_station, test_station.modulator2)
    IV_curve(output_folder + 'Modulator2' + filename_suffix + '.csv',test_station.modulator2.write_voltage, 'mod2_voltage', test_station.modulator2.read_current, 'mod2_current', -4.0, 2.0, 0.1, output_folder + 'Modulator2' + filename_suffix + '.png')
    iv_prep(test_station, test_station.detector)
    IV_curve(output_folder + 'Detector' + filename_suffix + '.csv',test_station.detector.write_voltage, 'detector_voltage', test_station.detector.read_current, 'detetctor_current', -3.0, 2.0, 0.1, output_folder + 'Detetctor' + filename_suffix + '.png')
    test_station.set_output_on_all(True)

def measure_eye_parameters(input_filename, 
                           output_filename, 
                           scope_img_path, #This one is a path to the SCOPE computer
                           scope, 
                           test_station, 
                           mod_voltage, 
                           measure_RIN=True, 
                           pause_current_set=False):
    """Measure eye paramaters for each valid ITU channel. This function only pulls the data from the scope and does some basic scope initialization, it does not communication with any other test hardware requires to do RF tests.
    
    :param input_filename: Path to ITU CSV input filename with all DC parameters. Columns: itu_index, itu_wavelength, Mirr1_current, Mirr2_current, LasPha_current, SOA1_current, SOA2_current, Photocurrent_Mod1, Photocurrent_Mod2, origphotocurrent1, origphotocurrent2, is_min, is_max, is_mid, onchip_min, onchip_max, onchip_mid
    :type input_filename: str
    :param output_filename: Path to CSV output filename. Columns: itu_index, itu_wavelength, Mirr1_current, Mirr2_current, LasPha_current, SOA1_current, SOA2_current, Photocurrent_Mod1, Photocurrent_Mod2, origphotocurrent1, origphotocurrent2, is_min, is_max, is_mid, onchip_min, onchip_max, onchip_mid, risetime, falltime, jitter, snr, er, eyecrossing, modulation_depth, poptavg, ptp, rin (if selected)
    :type output_filename: str
    :param scope_img_path: Path to save scope trace image. NOTE: This is a path relative to the scope!
    :type scope_img_path: str
    :param scope: Path to oscilloscope
    :type scope: testsuite.instruments.oscilloscopes
    :param test_station: Current device laser sections I/O
    :type test_station: LaserSections
    :param mod_voltage: Voltage to set both modulators to while measure scope parameters
    :type mod_voltage: float
    :param measure_RIN: Measure RIN on oscilloscope. Some scopes cannot measure RIN, so it is optional
    :type measure_RIN: bool
    :param pause_current_set: Pause program execution after setting each set of current and output target ITU wavelength.
    :type pause_current_set: bool
    """
    data = np.genfromtxt(input_filename, skip_header=9, delimiter=",", names=True)
    h = itu_header() + ",SOA1_current,SOA2_current,Photocurrent_Mod1,Photocurrent_Mod2,origphotocurrent1,origphotocurrent2,is_min,is_max,is_mid,onchip_min,onchip_max,onchip_mid"
    h = h + ",risetime,falltime,jitter,snr,er,eyecrossing,modulation_depth,poptavg,ptp"
    if measure_RIN:
        h = h + ",rin"
    save_data = []
    
    scope.cleardisplay()
    scope.autoscale()
    scope.select_eyemode()
    
    for itu_index in data["itu_index"]:
        if data[itu_index]["Mirr1_current"] == -1:
            output_item = []
            output_item.append(itu_index)
            output_item.append(itu_wavelength(itu_index))
            for i in range(15 + 9):
                output_item.append(-1)
            if measure_RIN:
                output_item.append(-1)
            save_data.append(output_item)
        else:
            test_station.set_output_on_all(True)
            test_station.zero_all()
            test_station.mirror1.write_current(data["Mirr1_current"][itu_index])
            test_station.mirror2.write_current(data["Mirr2_current"][itu_index])
            test_station.laser_phase.write_current(data["LasPha_current"][itu_index])
            test_station.soa1.write_current(data["SOA1_current"][itu_index])
            test_station.soa2.write_current(data["SOA2_current"][itu_index])
            test_station.phase1.write_current(data["is_mid"][itu_index])
            test_station.modulator1.write_voltage(mod_voltage)
            test_station.modulator2.write_voltage(mod_voltage)
            
            if pause_current_set:
                print("ITU Index: " + format(itu_index) + " Wavelength: " + format(itu_wavelength(itu_index)))
                raw_input("Press Enter to continue")
            
            output_item = []
            #itu_index,itu_wavelength,Mirr1_current,Mirr2_current,LasPha_current,SOA1_current,SOA2_current,Photocurrent_Mod1,Photocurrent_Mod2,origphotocurrent1,origphotocurrent2,is_min,is_max,onchip_min,onchip_max
            output_item.append(itu_index)
            output_item.append(itu_wavelength(itu_index))
            output_item.append(data["Mirr1_current"][itu_index])
            output_item.append(data["Mirr2_current"][itu_index])
            output_item.append(data["LasPha_current"][itu_index])
            
            output_item.append(data["SOA1_current"][itu_index])
            output_item.append(data["SOA2_current"][itu_index])
            output_item.append(data["Photocurrent_Mod1"][itu_index])
            output_item.append(data["Photocurrent_Mod2"][itu_index])
            output_item.append(data["origphotocurrent1"][itu_index])
            output_item.append(data["origphotocurrent2"][itu_index])
            
            output_item.append(data["is_min"][itu_index])
            output_item.append(data["is_max"][itu_index])
            output_item.append(data["is_mid"][itu_index])
            output_item.append(data["onchip_min"][itu_index])
            output_item.append(data["onchip_max"][itu_index])
            output_item.append(data["onchip_mid"][itu_index])
            
            scope.single_acquisition()
            
            output_item.append(scope.read_risetime())
            output_item.append(scope.read_falltime())
            output_item.append(scope.read_jitter())
            output_item.append(scope.read_snr())
            output_item.append(scope.read_er())
            output_item.append(scope.read_eyecrossing())
            output_item.append(scope.read_modulation_depth())
            output_item.append(scope.read_poptavg())
            output_item.append(scope.read_ptp())
            if measure_RIN:
                output_item.append(scope.read_rin())
            
            save_data.append(output_item)
            
            scope.save_eye_image(scope_img_path + "ITU" + format(itu_index) + "_scope_eye_image.jpg")
            np.savetxt(output_filename, save_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
            
# def mirror_search_debug(test_station, 
#                         input_filename, 
#                         output_filename, 
#                         osa):
#     data = np.genfromtxt(input_filename, skip_header=9, delimiter=",", names=True)
#     test_station.zero_all()
#     h = itu_header() + "peak1_wavelength,peak1_power,peak2_wavelength,peak2_power"
#     save_data = []
#     for itu_index in data["itu_index"]:
#         if data[itu_index]["Mirr1_current"] == -1:
#             output_item = []
#             output_item.append(itu_index)
#             output_item.append(itu_wavelength(itu_index))
#             for i in range(7):
#                 output_item.append(-1)
#             save_data.append(output_item)
#         else:
#             test_station.mirror1.write_current(data[itu_index]["Mirr1_current"])
#             test_station.mirror2.write_current(data[itu_index]["Mirr2_current"])
#             test_station.laser_phase.write_current(data[itu_index]["LasPha_current"])
#             
#             peaks = osa.readpeak()
#             
#             output_item = []
#             output_item.append(itu_index)
#             output_item.append(itu_wavelength(itu_index))
#             output_item.append(data["Mirr1_current"][itu_index])
#             output_item.append(data["Mirr2_current"][itu_index])
#             output_item.append(data["LasPha_current"][itu_index])
#             
#             if len(peaks) < 1:
#                 output_item.append(-1)
#                 output_item.append(-1)
#             else:
#                 output_item.append(peaks[0]["wavelength"])
#                 output_item.append(peaks[0]["power"])
#                 
#             if len(peaks) < 2:
#                 output_item.append(-1)
#                 output_item.append(-1)
#             else:
#                 output_item.append(peaks[1]["wavelength"])
#                 output_item.append(peaks[1]["power"])
#                 
#             save_data.append(output_item)
#             
#         np.savetxt(output_filename, save_data, header = h, delimiter = ',', comments = '', fmt = FORMAT_STRING_PERCENT)
