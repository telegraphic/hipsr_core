# encoding: utf-8
"""
hipsr_reprogram.py
==============================

Reprogram roach boards - threaded.

Created by Danny Price on 2011-10-05.
Copyright (c) 2012 The HIPSR collaboration. All rights reserved.
"""

# Python metadata
__author__    = "Danny Price"
__license__   = "GNU GPL"
__version__   = "0.1"
 
import sys, os, socket, random, select, re, time
import threading, Queue
import numpy as np

import hipsr_core.katcp_wrapper as katcp_wrapper
import hipsr_core.config as config

class FpgaProgrammer(threading.Thread):
    """ Thread worker function for reprogramming roach boards """
    def __init__(self, queue, flavor):
        "Constructor."
        threading.Thread.__init__(self)
        self.queue  = queue
        self.flavor = flavor
        self.data = []
    
    def run(self):
        """ Thread run method. Fetch data from roach"""
        while True:
            # Get input queue info (FPGA object)
            fpga = self.queue.get()
            try:
                time.sleep(random.random()/100) # Spread out
                msg = "\tProgramming %s"%fpga.host
                print msg
                fpga.progdev(config.fpga_config[self.flavor]["firmware"])
                time.sleep(1)
                if fpga.is_connected():
                    registers = fpga.listdev()
                    if len(registers) == 0:
                        print "Warning: %s doesn't appear to be programmed. Attempting to reprogram...."%fpga.host
                        try:
                            fpga.progdev(config.fpga_config[self.flavor]["firmware"])
                            time.sleep(1)
                        except:
                            print "programming timed out. There's probably something up"
            except:
                print "Warning: couldn't grab data from %s"%fpga.host
            # Signal to queue task complete
            self.queue.task_done()

class FpgaConfigurer(threading.Thread):
    """ Thread worker function for reprogramming roach boards """
    def __init__(self, queue, flavor):
        "Constructor."
        threading.Thread.__init__(self)
        self.queue = queue
        self.flavor = flavor
        self.data = []
    
    def run(self):
        """ Thread run method. Fetch data from roach"""
        while True:
            # Get input queue info (FPGA object)
            fpga = self.queue.get()
            time.sleep(1)

            try:
                if fpga.is_connected():
                    registers = fpga.listdev()
                    if len(registers) == 0:
                        print "\tWarning: %s doesn't appear to be programmed. Attempting to reprogram...."%fpga.host
                        fpga.progdev(config.fpga.config[self.flavor]["firmware"])
                        time.sleep(1)

                    try:
                        for key in config.fpga_config[self.flavor].keys():
                            if key != "firmware":
                                fpga.write_int(key, config.fpga_config[self.flavor][key])

                        fpga.write_int('master_reset',    0)
                        fpga.write_int('master_reset',    1)
                        fpga.write_int('sync_pps_arm',    0)
                        fpga.write_int('sync_pps_arm',    1)

                        print "\t%s configured"%fpga.host
                        time.sleep(1)
                    except KeyError:
                        print "\tWarning: Key Error raised. One or more software registers cannot be programmed."
                        print "\tFPGA: %s, Current key: %s"%(fpga.host, key)
                    except RuntimeError:
                        print "\tWarning: Runtime Error raised. One or more software registers cannot be programmed."
                        print "\tFPGA: %s, Current key: %s"%(fpga.host, key)
                    except:
                        print "\tWarning: programming exception raised. There's probably something up"
                        raise


            except:
                print "Error configuring %s"%fpga.host

            # Signal to queue task complete
            self.queue.task_done()


def runThreads(fpgalist, threadqueue):
    """ Spawns multiple threads, with each thread retrieving from a single board.
    A queue is used to block until all threads have completed.   
    """
    # Run threads using queue
    for fpga in fpgalist:
      threadqueue.put(fpga)
    # Make sure all threads have completed
    threadqueue.join()


def reprogram(flavor):
    """ Reprogram FPGAs"""
    threadqueue = Queue.Queue()
    print("Connecting to ROACH boards...")
    roachlist = config.roachlist
    fpgalist  = [katcp_wrapper.FpgaClient(roach, config.katcp_port, timeout=10) for roach in roachlist]
    for i in range(len(fpgalist)):
        t = FpgaProgrammer(threadqueue, flavor)
        t.setDaemon(True)
        t.setName("thread-%s"%fpgalist[i].host)
        t.start()
    runThreads(fpgalist, threadqueue)


def reconfigure(flavor):
    """ Reconfigure FPGAs"""
    threadqueue = Queue.Queue()
    print("Connecting to ROACH boards...")
    roachlist = config.roachlist
    fpgalist  = [katcp_wrapper.FpgaClient(roach, config.katcp_port, timeout=10) for roach in roachlist]
    for i in range(len(fpgalist)):
       t = FpgaConfigurer(threadqueue, flavor)
       t.setDaemon(True)
       t.setName("thread-%s"%fpgalist[i].host)
       t.start()
    runThreads(fpgalist, threadqueue)


def snap(fpga, snap_id, bytes=4096, fmt='uint32'):
    """Retrieve & unpack data from a snap block"""
    fpga.write_int(snap_id+'_ctrl', 0, blindwrite=True)
    fpga.write_int(snap_id+'_ctrl', 1, blindwrite=True)
    packed = fpga.read(snap_id+'_bram', bytes)
    data = np.fromstring(packed, dtype=fmt).byteswap()
    return data


def stitch(array1,array2):
    """ Stitch together even and odd values.
    Example
    -------
    a1=[0 2 4], a2 =[1 3 5]
    stitch(a1,a2) = [0 1 2 3 4 5]
    """
    # Create a 2xN numpy array, transpose then ravel into 1D
    data = np.array([array1,array2])
    return np.array(data.transpose().ravel())


def squashData(data, numchans=256):
    """ Averages channels, reduces down to an amount suitable for plotting.  """   
    if(len(data) > numchans):
        yvals = np.sum(data.reshape([numchans, len(data)/numchans]), axis=1)/len(data)*numchans
    else:
        yvals = data
    return yvals.astype('float32')


def squashSpectrum(spectra):
    """ Applies squashData four times """
    #squashed = {"xx"    : 10*np.log10(squashData(spectra["xx"])), 
    #            "yy"    : 10*np.log10(squashData(spectra["yy"])), 
    #            "re_xy" : squashData(spectra["re_xy"]), 
    #            "im_xy" : squashData(spectra["im_xy"]) }
    
    #keys = ["xx","yy","re_xy","im_xy"]
    keys = ["xx", "yy"] # No need to do stokes for now
    squashed = {}
    for key in keys:
        val = squashData(spectra[key])
        val[np.isnan(val)] = 0   # JSON does not support nan
        val[np.isinf(val)] = 0   # JSON does not support inf
        squashed[key] = val
    return squashed


def getSpectrum_400_8192(fpga):
    """Retrieves HIPSR spectral data from roach board.
    
    Returns spectral data as a dictionary of numpy arrays
    
    Parameters
    ----------
    fpga: katcp_wrapper.FpgaClient object
      fpga katcp socket thing that does the talking
    """
    bytes=4096*4
    if fpga.is_connected() :
        # grab the snap data and unpack
        data_xx0 = snap(fpga, 'snap_xx0', bytes, 'uint32')
        data_xx1 = snap(fpga, 'snap_xx1', bytes, 'uint32')
        data_yy0 = snap(fpga, 'snap_yy0', bytes, 'uint32')
        data_yy1 = snap(fpga, 'snap_yy1', bytes, 'uint32')
        
        data_re_xy0 = snap(fpga, 'snap_re_xy0', bytes, 'int32')
        data_re_xy1 = snap(fpga, 'snap_re_xy1', bytes, 'int32')
        data_im_xy0 = snap(fpga, 'snap_im_xy0', bytes, 'int32')
        data_im_xy1 = snap(fpga, 'snap_im_xy1', bytes, 'int32')

        #Sew these back together
        data_xx = stitch(data_xx0, data_xx1)
        data_yy = stitch(data_yy0, data_yy1)
        data_re_xy = stitch(data_re_xy0, data_re_xy1)
        data_im_xy = stitch(data_im_xy0, data_im_xy1)
        
        fft_of   = fpga.read_int('o_fft_of')
        acc_cnt  = fpga.read_int('o_acc_cnt') 
        adc_clip = fpga.read_int('o_adc0_clip')
        
        # grab the NAR snap data too
        xx_cal_on  = snap(fpga, 'nar_snap_x_on',  64, 'uint32')
        xx_cal_off = snap(fpga, 'nar_snap_x_off', 64, 'uint32')
        yy_cal_on  = snap(fpga, 'nar_snap_y_on',  64, 'uint32')
        yy_cal_off = snap(fpga, 'nar_snap_y_off', 64, 'uint32')

        #reverse data: np.array(data_xx)[::-1]
        dataDict = {
            "id" : acc_cnt, 
            "xx": data_xx, 
            "yy" : data_yy, 
            "re_xy" : data_re_xy, 
            "im_xy" : data_im_xy, 
            "fft_of" : fft_of,
            "adc_clip" : adc_clip,
            "timestamp" : 0,
            "xx_cal_on"  : xx_cal_on,
            "xx_cal_off" : xx_cal_off,
            "yy_cal_on"  : yy_cal_on,
            "yy_cal_off" : yy_cal_off
            }
        return dataDict
    else:
        raise Exception('FPGA-data-grabber')

def getSpectrum_200_16384(fpga):
    """Retrieves HIPSR spectral data from roach board.

    Returns spectral data as a dictionary of numpy arrays

    Parameters
    ----------
    fpga: katcp_wrapper.FpgaClient object
      fpga katcp socket thing that does the talking
    """
    bytes=4096*4*4
    if fpga.is_connected() :
        # grab the snap data and unpack
        data_xx = snap(fpga, 'snap_xx', bytes, 'uint32')
        data_yy = snap(fpga, 'snap_yy', bytes, 'uint32')

        fft_of   = fpga.read_int('o_fft_of')
        acc_cnt  = fpga.read_int('o_acc_cnt')
        adc_clip = fpga.read_int('o_adc0_clip')

        # grab the NAR snap data too
        xx_cal_on  = snap(fpga, 'nar_snap_x_on',  64, 'uint32')
        xx_cal_off = snap(fpga, 'nar_snap_x_off', 64, 'uint32')
        yy_cal_on  = snap(fpga, 'nar_snap_y_on',  64, 'uint32')
        yy_cal_off = snap(fpga, 'nar_snap_y_off', 64, 'uint32')

        #reverse data: np.array(data_xx)[::-1]
        dataDict = {
            "id" : acc_cnt,
            "xx": data_xx,
            "yy" : data_yy,
            "fft_of" : fft_of,
            "adc_clip" : adc_clip,
            "timestamp" : 0,
            "xx_cal_on"  : xx_cal_on,
            "xx_cal_off" : xx_cal_off,
            "yy_cal_on"  : yy_cal_on,
            "yy_cal_off" : yy_cal_off
        }
        return dataDict
    else:
        raise Exception('FPGA-data-grabber')


def getSpectrum(fpga, flavor='hipsr_400_8192'):
    """ Helper function to select which flavor of getSpectrum should be used """
    if flavor == 'hipsr_400_8192':
        return getSpectrum_400_8192(fpga)

    elif flavor == 'hipsr_200_16384':
        return getSpectrum_200_16384(fpga)


