#!/usr/bin/env python
# encoding: utf-8
"""
config.py
============

This is the main configuration file for the HIPSR wideband spectrometer server script.

"""

__author__    = "Danny Price"
__email__     = "danny.price@astro.ox.ac.uk" 
__license__   = "GNU GPL"
__version__   = "1.0 - Analytical Albatross"

project_id = 'PXXX'

data_dir    = '/data/hipsr'

tcs_port     = 59011             # BPSR is 50910
tcs_server   = '130.155.182.73'  # hipsr-srv0 eth0

plotter_port = 59012
plotter_host = '130.155.181.64'  # Danny's laptop at Parkes

katcp_port = 7147

boffile = 'hipsr_parkes_400_2012_Mar_15_2209.bof'
reprogram = True
reconfigure = True

roachlist = {
    "drake"   : "beam_01",
    "hendrix" : "beam_02",
    "reznor"  : "beam_03",
    "keenan"  : "beam_04",
    "mackaye" : "beam_05", 
    "albarn" : "beam_06", 
    "willis"  : "beam_07", 
    "waits"  : "beam_08", 
    "yorke"  : "beam_09",
    "cobain"   : "beam_10",
    "curtis"   : "beam_11",
    "barrett"  : "beam_12",
    "patton"   : "beam_13"
    }

fpga_config = {
    "acc_len" : 48828*2,
    "fft_shift" : -1,
    "quant_xx_gain" : -1,
    "quant_yy_gain" : -1,
    "quant_xy_gain" : -1,
    "mux_sel"       : 0
}
        
tcs_regex_esc = '\\n' # Escape for message from TCS
#tcs_regex_esc = '' # Escape for dummy TCS data
