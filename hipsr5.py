# encoding: utf-8
"""
hipsr5.py
=============

Created by Danny Price on 2011-10-05.
Copyright (c) 2011 The HIPSR collaboration. All rights reserved.\n

Functions for creating HIPSR5 data files. The HIPSR5 data format is the
main storage format for data taken with HIPSR. It is based on HDF5, which
is superior to FITS in pretty much every way:\n
http://www.hdfgroup.org/HDF5/
"""

__version__ = "0.2"
__author__ = "Danny Price"

import os

# Data and math handling
import numpy as np, tables as tb


class Spectrum(tb.IsDescription):
    """ PyTables table descriptor: storage of spectral data """
    id = tb.Int32Col(pos=0)  # Unique ID
    timestamp = tb.Time64Col(pos=1)  # Timestamp (at BRAM read)
    xx = tb.UInt32Col(shape=8192, pos=2)  # XX Autocorrelation data
    yy = tb.UInt32Col(shape=8192, pos=3)  # YY Autocorrelation data
    re_xy = tb.Int32Col(shape=8192, pos=4)  # XY Cross correlation - real
    im_xy = tb.Int32Col(shape=8192, pos=5)  # XY Cross correlation - imag
    fft_of = tb.BoolCol(pos=6)  # FFT overflow flag
    adc_clip = tb.BoolCol(pos=7)  # ADC clipping flag


class FirmwareConfig(tb.IsDescription):
    """PyTables table descriptor: storage of basic setup parameters"""
    firmware = tb.StringCol(64, pos=0)  # Firmware name - e.g. hipsr_16.bof
    quant_xx_gain = tb.Int32Col(pos=1)  # Gain used in quantization - XX
    quant_yy_gain = tb.Int32Col(pos=1)  # Gain used in quantization - XX
    quant_xy_gain = tb.Int32Col(pos=1)  # Gain used in quantization - XX
    mux_sel = tb.Int32Col(pos=1)  # Digital noise source or the ADC?
    fft_shift = tb.Int32Col(pos=2)  # FFT shift
    acc_len = tb.Int32Col(pos=3)  # Number of accumulations per dump


class Observation(tb.IsDescription):
    """PyTables table descriptor: observation details"""
    telescope = tb.StringCol(32, pos=0)  # Telescope name (always Parkes for us)
    receiver = tb.StringCol(32, pos=1)  # Receiver name (MULTI for us)
    date = tb.Time64Col(pos=2)  # Date - only 32bits reqd for date but using 64
    project_id = tb.StringCol(32, pos=3)  # Project ID number, PXXX for Parkes
    project_name = tb.StringCol(255, pos=4)  # Project name
    observer = tb.StringCol(255, pos=5)  # Observer's name
    num_beams = tb.Int8Col(pos=6)  # Number of beams being used
    ref_beam = tb.Int8Col(pos=7)  # Reference beam
    acc_len = tb.Float32Col(pos=8)  # Accumulation length, in seconds
    bandwidth = tb.Int32Col(pos=9)  # Bandwidth (MHz) (-ve means inverted)
    dwell_time = tb.Float32Col(pos=10)  # Dwell time (sec)
    frequency = tb.Float32Col(pos=11)  # Central frequency (MHz)
    feed_rotation = tb.StringCol(64, pos=12)  # Feed rotation (e.g. STEPPED)
    feed_angle = tb.Float32Col(pos=13)  # Feed angle
    freq_switch = tb.BoolCol(pos=14)  # Frequency switching flag
    obs_mode = tb.StringCol(16, pos=15)  # Observation mode (e.g SCAN)
    scan_rate = tb.Float32Col(pos=16)  # Scan rate, (deg/min)


class Weather(tb.IsDescription):
    """PyTables table descriptor: weather details"""
    timestamp = tb.Time64Col(pos=0)  # Timestamp at telescope pointing
    temperature = tb.Float32Col(pos=1)  # Ambient temperature (K)
    pressure = tb.Float32Col(pos=2)  # Pressure (kPa)
    humidity = tb.Float32Col(pos=3)  # Humidity (%)
    wind_speed = tb.Float32Col(pos=4)  # Wind Speed (m/s)
    wind_direction = tb.Float32Col(pos=5)  # Wind Direction (deg)


class Pointing(tb.IsDescription):
    """PyTables table descriptor: telescope pointing details"""
    timestamp = tb.Time64Col(pos=0)  # Timestamp at telescope pointing
    source = tb.StringCol(255, pos=1)  # Name of source
    ra = tb.Float32Col(pos=2)  # Right Ascension (radians)
    dec = tb.Float32Col(pos=3)  # Declination (radians)


class ScanPointing(tb.IsDescription):
    """PyTables table descriptor: pointing details for scans"""
    timestamp = tb.Time64Col(pos=0)  # Timestamp at telescope pointing
    mb01_raj = tb.Float32Col(pos=1)  # Beam 01 RA (degrees)
    mb01_dcj = tb.Float32Col(pos=2)  # Beam 01 DEC (degrees)
    mb02_raj = tb.Float32Col(pos=3)  # Beam 02 RA
    mb02_dcj = tb.Float32Col(pos=4)  # Beam 02 DEC
    mb03_raj = tb.Float32Col(pos=5)  # .
    mb03_dcj = tb.Float32Col(pos=6)  # .
    mb04_raj = tb.Float32Col(pos=7)  # .
    mb04_dcj = tb.Float32Col(pos=8)
    mb05_raj = tb.Float32Col(pos=9)
    mb05_dcj = tb.Float32Col(pos=10)
    mb06_raj = tb.Float32Col(pos=11)
    mb06_dcj = tb.Float32Col(pos=12)
    mb07_raj = tb.Float32Col(pos=13)
    mb07_dcj = tb.Float32Col(pos=14)
    mb08_raj = tb.Float32Col(pos=15)
    mb08_dcj = tb.Float32Col(pos=16)
    mb09_raj = tb.Float32Col(pos=17)
    mb09_dcj = tb.Float32Col(pos=18)
    mb10_raj = tb.Float32Col(pos=19)
    mb10_dcj = tb.Float32Col(pos=20)
    mb11_raj = tb.Float32Col(pos=21)
    mb11_dcj = tb.Float32Col(pos=22)
    mb12_raj = tb.Float32Col(pos=23)
    mb12_dcj = tb.Float32Col(pos=24)
    mb13_raj = tb.Float32Col(pos=25)
    mb13_dcj = tb.Float32Col(pos=26)
    azimuth = tb.Float32Col(pos=27)  # Telescope azimuth
    elevation = tb.Float32Col(pos=28)  # Telescope elevation
    par_angle = tb.Float32Col(pos=29)  # Paraxial angle
    focus_tan = tb.Float32Col(pos=30)  # Lateral focus offset (mm) "Z"
    focus_axial = tb.Float32Col(pos=31)  # Axial docus offset (mm) "Y"
    focus_rot = tb.Float32Col(pos=32)  # Receiver rotation angle


def createSingleBeam(filename, path='./'):
    """ Create a new HDF5 file and populate with table structure for single beam
    
    returns pyTables h5 object
    
    Parameters
    ----------
    filename: string
      filename of the file to be created
    path:
      path to the file, defaults to current directory.
    """

    print('Creating new HDF5 file %s in %s' % (filename, path))
    h5 = tb.openFile(os.path.join(path, filename), mode='w')

    print('Creating data tables...')
    raw_data = h5.createGroup('/', 'raw_data', 'raw data (from FPGA)')
    h5.createTable(raw_data, 'beam_01', Spectrum, 'Multibeam receiver beam 01')

    config = h5.createTable('/', 'firmware_config', FirmwareConfig, 'Firmware config')

    obs = h5.createTable('/', 'observation', Observation, 'Observation Details')
    obs.attrs.units = {
        'feed_angle': 'deg',
        'acc_len': 's',
        'bandwidth': 'MHz',
        'dwell_time': 's'
    }

    pointing = h5.createTable('/', 'pointing', Pointing, 'Telescope pointing details')
    pointing.attrs.units = {
        'ra': 'deg',
        'dec': 'deg',
        'feed_angle': 'deg'
    }

    weather = h5.createTable('/', 'weather', Weather, 'Weather Details')
    weather.attrs.units = {
        'temperature': 'K',
        'pressure': 'kPa',
        'humidity': '%',
        'wind_speed': 'm/s',
        'wind_direction': 'deg'
    }

    scanPointing = h5.createTable('/', 'scan_pointing', ScanPointing, 'Telescope scan details')
    scanPointing.attrs.units = {
        'raj': 'deg',
        'dcj': 'deg',
        'focus_tan': 'mm',
        'focus_axial': 'mm',
        'focus_rot': 'deg',
        'par_angle': 'deg',
        'azimuth': 'deg',
        'elevation': 'deg'
    }

    h5.flush()

    return h5


def createMultiBeam(filename, path='./', num_beams=13):
    """ Create a new HDF5 file and populate with table structure for multibeam receiver
    
    returns pyTables h5 object
    
    Parameters
    ----------
    filename: string
      filename of the file to be created
    path: string
      path to the file, defaults to current directory.
    num_beams: int
      number of beams, should be 1, 7 or 13. Defaults to 13
    """

    print('Creating new HDF5 file %s in %s' % (filename, path))
    h5 = tb.openFile(os.path.join(path, filename), mode='w')

    print('Creating data tables...')
    raw_data = h5.createGroup('/', 'raw_data', 'raw data (from FPGA)')
    for id in range(1, num_beams + 1):
        # print('Creating multibeam receiver table %s of %s...'%(id,num_beams))

        h5.createTable(raw_data, 'beam_%02i' % id, Spectrum, 'Multibeam receiver beam %02s' % id)

    config = h5.createTable('/', 'firmware_config', FirmwareConfig, 'Firmware Configuration')

    obs = h5.createTable('/', 'observation', Observation, 'Observation Details')
    obs.attrs.units = {
        'feed_angle': 'deg',
        'acc_len': 's',
        'bandwidth': 'MHz',
        'dwell_time': 's'
    }

    pointing = h5.createTable('/', 'pointing', Pointing, 'Telescope pointing details')
    pointing.attrs.units = {
        'ra': 'deg',
        'dec': 'deg',
        'feed_angle': 'deg'
    }

    weather = h5.createTable('/', 'weather', Weather, 'Weather Details')
    weather.attrs.units = {
        'temperature': 'K',
        'pressure': 'kPa',
        'humidity': '%',
        'wind_speed': 'm/s',
        'wind_direction': 'deg'
    }

    scanPointing = h5.createTable('/', 'scan_pointing', ScanPointing, 'Telescope scan details')
    scanPointing.attrs.units = {
        'raj': 'deg',
        'dcj': 'deg',
        'focus_tan': 'mm',
        'focus_axial': 'mm',
        'focus_rot': 'deg',
        'par_angle': 'deg',
        'azimuth': 'deg',
        'elevation': 'deg'
    }

    h5.flush()

    return h5


if __name__ == "__main__":
    x = createMultiBeam('test.h5', num_beams=13)
    print x
    x.close()