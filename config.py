#!/usr/bin/env python
# encoding: utf-8
"""
config.py
============

This is the main configuration file for the HIPSR wideband spectrometer server script.

"""

###########
# v1 - Analytical Albatross (Oct 2012)
# v2 - Ballistic Bandicoot  (Apr 2013)
# v3 - Cartesian Cockatoo   (Sep 2013)
# v4 - Dirac-Delta Dingo    (Jan 2014)
# v5 - Epsilon>0 Echidna    (May 2014)

__author__    = "Danny Price"
__email__     = "danny.price@astro.ox.ac.uk" 
__license__   = "GNU GPL"
__version__   = "5.0 - Epsilon>0 Echidna"

project_id    = 'PXXX'
data_dir      = '/data/hipsr'
tcs_port      = 59011             # BPSR is 50910
tcs_server    = '130.155.182.73'  # hipsr-srv0 eth0
plotter_port  = 59012
plotter_host  = '127.0.0.1'  # Plotting on localhot
katcp_port    = 7147
tcs_regex_esc = '\\n' # Escape for message from TCS
reprogram     = True
reconfigure   = True

###############
# Roach to beam mappings
# Last checked on 17th April 2013
# Note: Curtis is noise diode master ROACH

roachlist = {
    "drake"    : "beam_01",
    "hendrix"  : "beam_02",
    "reznor"   : "beam_03",
    "keenan"   : "beam_04",
    "mackaye"  : "beam_05", 
    "albarn"   : "beam_06", 
    "willis"   : "beam_07", 
    "waits"    : "beam_08", 
    "yorke"    : "beam_09",
    "cobain"   : "beam_10",
    "patton"   : "beam_11",
    "barrett"  : "beam_12",
    "curtis"   : "beam_13"
    }


############
# FPGA Flavors
############
fpga_config = {}

############
# hipsr_400_8192
# Last modified 17th April 2013
# FPGA clock:         200 MHz
# Dump rate:          2 s
# Diode switching:    128 Hz
# Vector accumulator: 4096 long (8192/2, as even / odd are parallel streams)
# 200e6 / 4096 = 48828.125

n_sec             = 2
acc_len           = 48828*n_sec
nar_acc_len       = acc_len * 4096 / 8
n_cycles_per_dump = 128*n_sec
sq_wv_period      = 8 * nar_acc_len / n_cycles_per_dump 

# "firmware"              : 'hipsr_400_8192_2014_Jan_27_2354.bof',
hipsr_400_8192 = {
    "firmware"              : 'hipsr_400_8192_2014_May_29_1735.bof',
    "acc_len"               : acc_len,
    "fft_shift"             : -1,
    "quant_xx_gain"         : -1,
    "quant_yy_gain"         : -1,
    "quant_xy_gain"         : -1,
    "mux_sel"               : 0,
    "nar_sq_wave_period"    : sq_wv_period, 
    "nar_quant_yy_gain"     : 2**12-1,
    "nar_quant_xx_gain"     : 2**12-1,
    "nar_fft_shift"         : -1,
    "nar_acc_len"           : nar_acc_len
}


hipsr_200_16384 = {
    "firmware"              : 'hipsr_200_16384_devel_2014_May_24_2311.bof',
    "acc_len"               : acc_len / 4,
    "fft_shift"             : -1,
    "quant_xx_gain"         : -1,
    "quant_yy_gain"         : -1,
    "mux_sel"               : 0,
    "nar_sq_wave_period"    : sq_wv_period,
    "nar_quant_yy_gain"     : 2**12-1,
    "nar_quant_xx_gain"     : 2**12-1,
    "nar_fft_shift"         : -1,
    "nar_acc_len"           : nar_acc_len
}

fpga_config["hipsr_400_8192"]  = hipsr_400_8192
fpga_config["hipsr_200_16384"] = hipsr_200_16384
