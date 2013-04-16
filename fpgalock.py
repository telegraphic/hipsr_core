"""
fpgalock.py
-----------

Simple lock system to stop FPGA from being reprogrammed / configured when in use.

Main functionality is through the @checklock decorator, which will block any decorated
function from being run if the user's UID does not match the UID of a lock file.

Example usage:

    from fpgalock import *
    
    @checklock
    def check_me_first():
        print "foo"

By adding the @checklist decorator, check_me_first will not run if the lock check fails.
Instead, a LockError exception will be thrown. 
"""

import sys, time, os, pwd
from stat import *

LOCK_FILE_NAME = "fpga.lock"

class LockError(Exception):
    """ Error raised when FPGAs are locked. 
    
    Blocks reprogramming and changing registers. """
    def __init__(self, err_type='lock'):        
        
        self.to_print = ""
        
        if err_type == 'lock':
            try:
                st = os.stat(LOCK_FILE_NAME)
                self.uid = pwd.getpwuid( st[ST_UID] ).pw_name 
                self.timestamp = time.asctime(time.localtime(st[ST_MTIME]))
                self.to_print += "FPGAs are locked.\n"
                self.to_print += "Current FPGA lock: %s "%self.uid
                self.to_print += "on %s"%self.timestamp
            except:
                raise
                
        if err_type == 'remove':
            self.to_print += "ERROR: cannot remove lock."
            
        if err_type == 'create':
            self.to_print += "ERROR: cannot create lock."

    def __str__(self):
        return self.to_print

def blocklock():
    """ Function which raises a lock error. """
    raise LockError('lock')

def removelock():
    if os.path.isfile(LOCK_FILE_NAME):
        try:
            os.remove(LOCK_FILE_NAME)
        except:
            raise LockError('remove')
    else:
        print "WARNING: no lock was found."
        
def createlock():
    try:
        lock_file = open(LOCK_FILE_NAME, "w")
        lock_file.close()
    except:
        raise LockError('create')

def checklock(fn):
    """ Decorator which blocks functions if the FPGA is locked. 
    
    An error is returned if lock was by a different user. At runtime,
    the error will be raised, blocking the function from being called."""
    if os.path.isfile(LOCK_FILE_NAME):
        st  = os.stat(LOCK_FILE_NAME)
        uid = st[ST_UID]
        if uid == os.getuid():
            return fn
        else:          
            return blocklock # Do not want to immediately raise
    else:
        return fn

@checklock
def locked_fn():
    print "This function runs only when unlocked."

if __name__ == '__main__':
    
    # Simple tests
    createlock()
    locked_fn()
    removelock()