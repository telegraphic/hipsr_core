#!/usr/bin/env python
# encoding: utf-8
"""
config_diode.py
===============

Configuration for the diode calibration routine.

"""

############
# FPGA setup
# Last modified 17th April 2013
# FPGA clock:         200 MHz
# Dump rate:          0.1 s
# Diode switching:    160 Hz

nar_acc_len       = 2500000     # Equals 10 Hz
sq_wv_period      = 1250000     # Equals 160 Hz

fpga_config = {
    "nar_sq_wave_period"    : sq_wv_period, 
    "nar_quant_yy_gain"     : -1,
    "nar_quant_xx_gain"     : -1,
    "nar_fft_shift"         : -1,
    "nar_acc_len"           : nar_acc_len
}
