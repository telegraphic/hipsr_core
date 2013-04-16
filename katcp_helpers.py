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

import lib.katcp_wrapper as katcp_wrapper
import lib.helpers as h
import lib.config as config

class FpgaProgrammer(threading.Thread):
    """ Thread worker function for reprogramming roach boards """
    
    def __init__(self, queue):
      "Constructor."
      threading.Thread.__init__(self)
      self.queue = queue
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
            
            fpga.progdev(config.boffile)
            time.sleep(1)
            
            if fpga.is_connected():
              registers = fpga.listdev()
              if len(registers) == 0:
                  print "Warning: %s doesn't appear to be programmed. Attempting to reprogram...."%fpga.host
                  try:
                      fpga.progdev(boffile)
                      time.sleep(1)
                  except:
                      print "programming timed out. There's probably something up"
            
        except:
            print "Warning: couldn't grab data from %s"%fpga.host
        
        
        # Signal to queue task complete
        self.queue.task_done()

class FpgaConfigurer(threading.Thread):
    """ Thread worker function for reprogramming roach boards """
    
    def __init__(self, queue):
      "Constructor."
      threading.Thread.__init__(self)
      self.queue = queue
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
                  fpga.progdev(config.boffile)
                  time.sleep(1)
                  
              try:
                fpga.write_int('acc_len',         config.fpga_config["acc_len"]) # About 2s
                fpga.write_int('quant_xx_gain',   config.fpga_config["quant_xx_gain"])
                fpga.write_int('quant_yy_gain',   config.fpga_config["quant_yy_gain"])
                fpga.write_int('quant_xy_gain',   config.fpga_config["quant_xy_gain"])
                fpga.write_int('fft_shift',       config.fpga_config["fft_shift"])
        
                fpga.write_int('master_reset',    0)
                fpga.write_int('master_reset',    1)
                fpga.write_int('sync_pps_arm',    0)
                fpga.write_int('sync_pps_arm',    1)
                print "\t%s configured"%fpga.host
                time.sleep(1)
              except:
                print "\tWarning: programming timed out. There's probably something up"
             
            
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

def reprogram():
    """ Reprogram FPGAs"""
    threadqueue = Queue.Queue()
    print("Connecting to ROACH boards...")
    roachlist = config.roachlist
    fpgalist  = [katcp_wrapper.FpgaClient(roach, config.katcp_port, timeout=10) for roach in roachlist]

    for i in range(len(fpgalist)):
       t = FpgaProgrammer(threadqueue)
       t.setDaemon(True)
       t.setName("thread-%s"%fpgalist[i].host)
       t.start()
    
    runThreads(fpgalist, threadqueue)

def reconfigure():
    """ Reconfigure FPGAs"""
    threadqueue = Queue.Queue()
    print("Connecting to ROACH boards...")
    roachlist = config.roachlist
    
    fpgalist  = [katcp_wrapper.FpgaClient(roach, config.katcp_port, timeout=10) for roach in roachlist]
    
    for i in range(len(fpgalist)):
       t = FpgaConfigurer(threadqueue)
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
        """ Applies squashData four times"""
    
        squashed = {"xx"    : 10*np.log10(squashData(spectra["xx"])), 
                    "yy"    : 10*np.log10(squashData(spectra["yy"])), 
                    "re_xy" : 10*np.log10(squashData(spectra["re_xy"])), 
                    "im_xy" : 10*np.log10(squashData(spectra["im_xy"])) }
    
        return squashed

    def getSpectrum(fpga):
        """Retrieves HIPSR spectral data from roach board.
    
        Returns spectral data as a dictionary of numpy arrays
    
        Parameters
        ----------
        fpga: katcp_wrapper.FpgaClient object
          fpga katcp socket thing that does the talking
        """
        global timestamp
        bytes=4096*4

        if(fpga.is_connected()):
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
        
            fft_of  = fpga.read_int('o_fft_of')
            acc_cnt = fpga.read_int('o_acc_cnt') 
            adc_clip = fpga.read_int('o_adc0_clip')

            #reverse data: np.array(data_xx)[::-1]
            dataDict = {
                "id" : acc_cnt, 
                "xx": data_xx, 
                "yy" : data_yy, 
                "re_xy" : data_re_xy, 
                "im_xy" : data_im_xy, 
                "fft_of" : fft_of,
                "adc_clip" : adc_clip,
                "timestamp" : 0
                }
        
            return dataDict
        else:
            raise Exception('FPGA-data-grabber')

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
    """ Applies squashData four times"""
    
    squashed = {"xx"    : 10*np.log10(squashData(spectra["xx"])), 
                "yy"    : 10*np.log10(squashData(spectra["yy"])), 
                "re_xy" : 10*np.log10(squashData(spectra["re_xy"])), 
                "im_xy" : 10*np.log10(squashData(spectra["im_xy"])) }
    
    return squashed

def getSpectrum(fpga):
    """Retrieves HIPSR spectral data from roach board.
    
    Returns spectral data as a dictionary of numpy arrays
    
    Parameters
    ----------
    fpga: katcp_wrapper.FpgaClient object
      fpga katcp socket thing that does the talking
    """
    global timestamp
    bytes=4096*4

    if(fpga.is_connected()):
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
        
        fft_of  = fpga.read_int('o_fft_of')
        acc_cnt = fpga.read_int('o_acc_cnt') 
        adc_clip = fpga.read_int('o_adc0_clip')

        #reverse data: np.array(data_xx)[::-1]
        dataDict = {
            "id" : acc_cnt, 
            "xx": data_xx, 
            "yy" : data_yy, 
            "re_xy" : data_re_xy, 
            "im_xy" : data_im_xy, 
            "fft_of" : fft_of,
            "adc_clip" : adc_clip,
            "timestamp" : 0
            }
        
        return dataDict
    else:
        raise Exception('FPGA-data-grabber')

#START OF MAIN:
if __name__ == '__main__':
    reprogram()
    reconfigure()
