# encoding: utf-8
"""
astroCoords.py
==============

Some useful functions for converting in between Right Ascension (hours,mins,secs)
and Declination (degrees,mins,secs) to degrees and radians. These functions are
all named in the same format: a2b(), where a is the original data, and b is the new
data format.

All of this type of basic stuff can be done with pyEphem or similar, but I wanted
something super simple.

Created by Danny Price on 2011-05-01.
Copyright (c) 2011 The University of Oxford. All rights reserved.

Module listing
~~~~~~~~~~~~~~

"""

import sys, os
import numpy as np



#### FROM DEGREES #####

def deg2rahms(degrees):
  """ Convert number in degrees to right ascension HH,MM,SS.SS
  Returns in list (hours,mins,secs)
  Parameters
  ----------
  degrees: float
  degrees to be converted (from 0 to 360)
  """
  hours = degrees / 360 * 24
  mins = (hours - int(hours)) * 60.0
  secs = (mins - int(mins)) * 60
  
  return [int(hours), int(mins), secs]

def deg2decdms(degrees):
  """ Convert number in degrees to declination degs, arcmins, arcsecs
  Returns in list (hours,mins,secs)
  Parameters
  ----------
  degrees: float
  degrees to be converted (from 0 to 360)
  """
  degs = int(degrees)
  arcmins = (degrees - degs) * 60.0
  arcsecs = (arcmins - int(arcmins)) * 60
  
  return [int(degs), int(arcmins), arcsecs]

def deg2rad(degrees):
  """Converts from degrees to radians.
  This is just a numpy call...
  
  Parameters
  ----------
  degrees: float
  degrees to be converted (from 0 to 360)
  
  """
  return np.deg2rad(degrees)



#### FROM RADIANS #####

def rad2rahms(radians):
  """ Convert number in radians to right ascension H,M,SS.SS
  Returns tuple (hours,mins,secs)
  Parameters
  ----------
  radians: float
  radians to be converted (from 0 to 2 pi)
  """
  degrees = radians * 180.0 / np.pi
  hours = degrees / 360 * 24
  mins = (hours - int(hours)) * 60.0
  secs = (mins - int(mins)) * 60
  
  return [int(hours), int(mins), secs]

def rad2decdms(radians):
  """ Convert number in radians to declination degs, arcmins, arcsecs
  Returns in list (hours,mins,secs)
  
  Parameters
  ----------
  radians: float
  radians to be converted (from 0 to 2 pi)
  """
  degrees = np.rad2deg(radians)
  degs = int(degrees)
  arcmins = (degrees - degs) * 60.0
  arcsecs = (arcmins - int(arcmins)) * 60
  
  return [int(degs), int(arcmins), arcsecs]
  
def rad2deg(radians):
  """Converts from radians to degrees.
  This is just a numpy call...
  
  Parameters
  ----------
  radians: float
  radians to be converted (from 0 to 2 pi)
  """
  return np.rad2deg(radians)



#### FROM RIGHT ASCENSION (H,M,S) #####

def rahms2deg(h,m,s):
  """Converts list (hours,minutes,seconds) to degrees
  Value returned in range (0,360)
  
  Parameters
  ----------
  h: int
  hour angle to be converted (from 0 to 24)
  h: int
  minutes to be converted (from 0 to 60)
  s: float
  seconds to be converted (from 0.0 to 60.0)
  """
  degrees = (float(h)+float(m)/60+float(s)/3600) * 15
  return degrees

def rahms2rad(h,m,s):
  """Converts list (hours,minutes,seconds) to radians
  Value returned in range (0,2pi)
  
  Parameters
  ----------
  h: int
  hour angle to be converted (from 0 to 24)
  h: int
  minutes to be converted (from 0 to 60)
  s: float
  seconds to be converted (from 0.0 to 60.0)
  """
  degrees = (float(h)+float(m)/60+float(s)/3600) * 15
  radians = np.deg2rad(degrees)
  return radians
    

#### FROM DECLINATION (D,M,S) #####

def decdms2deg(deg, min, sec):
  """Converts degrees, minutes seconds into degrees
  i.e. a floating point number in range (0,360)
  
  Parameters
  ----------
  deg: int
  degrees to be converted (from 0 to 360)
  min: int
  minutes to be converted (from 0 to 60)
  sec: float
  seconds to be converted (from 0.0 to 60.0)
  """
  degrees = (float(deg)+float(min)/60+float(sec)/3600)
  return degrees

def decdms2rad(deg, min, sec):
  """Converts degrees, minutes seconds into radians
  i.e. a floating point number in range (0,2pi)
  
  Parameters
  ----------
  deg: int
  degrees to be converted (from 0 to 360)
  min: int
  minutes to be converted (from 0 to 60)
  sec: float
  seconds to be converted (from 0.0 to 60.0)
  """
  degrees = (float(deg)+float(m)/60+float(s)/3600)
  radians = np.deg2rad(degrees)
  return degrees


#### FROM STRINGS HH:MM:SS.ss #####

def rastring2deg(rastring):
    """Converts a string of right ascension to degrees
    Value returned in range (0,360)
    
    Todo: More sophisticated string parser
    
    Parameters
    ----------
    rastring: string
    right ascension in 24 hour string: HH:MM:SS.ss
    """
    try:
        rastring = rastring.strip()
        (h,m,s)  = rastring.split(':')
        (h,m,s) = (int(h), int(m), float(s))
        deg = rahms2deg(h,m,s)
        return deg
    except:
        print "coords: couldn't convert %s"%rastring
        return 0


def rastring2rad(rastring):
    """Converts a string of right ascension to degrees
    Value returned in range (0,2pi)
    
    Todo: More sophisticated string parser
    
    Parameters
    ----------
    rastring: string
    right ascension in 24 hour string: HH:MM:SS.ss
    """
    try:
        rastring = rastring.strip()
        (h,m,s) = rastring.split(':')
        (h,m,s) = (int(h), int(m), float(s))
        rad = rahms2rad(h,m,s)
        return rad
    except:
        print "coords: couldn't convert %s"%rastring
        return 0


#### FROM STRINGS DD:MM:SS.ss #####

def decstring2deg(decstring):
    """Converts a string of declination to degrees
    Value returned in range (0,360)
    
    Todo: More sophisticated string parser
    
    Parameters
    ----------
    decstring: string
    declination in DD:MM:SS.ss
    """
    
    try:
        decstring = decstring.strip()
        (d,m,s) = decstring.split(':')
        (d,m,s) = (int(d), int(m), float(s))
        deg = decdms2deg(d,m,s)
        return deg
    except:
        print "coords: couldn't convert %s"%decstring
        return 0

def decstring2rad(decstring):
    """Converts a string of declination to radians
    Value returned in range (0,360)
    
    Todo: More sophisticated string parser
    
    Parameters
    ----------
    decstring: string
    declination in DD:MM:SS.ss
    """
    
    try:
        decstring = decstring.strip()
        (d,m,s) = decstring.split(':')
        (d,m,s) = (int(d), int(m), float(s))
        rad = decdms2rad(d,m,s)
        return rad
    except:
        print "coords: couldn't convert %s"%decstring
        return 0



def main():

  # A quick example
  ra_in_deg, dec_in_deg = (167.374, 38.612)

  print "b RA: ", deg2rahms(ra_in_deg)
  print "b DEC: ", deg2decdms(dec_in_deg)



if __name__ == '__main__':
  main()