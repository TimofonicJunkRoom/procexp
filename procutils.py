import os
import signal
from ctypes import *


lib = cdll.LoadLibrary("libc.so.6")
s = create_string_buffer('\000' * 1024)

class FileError(Exception):
  pass
  
  
def readFullFileFast(path):
  
  try:
    f = lib.open(path,0)
    if f == -1: raise FileError    
      
    total = ""
      
    eof = lib.read(f, s, 1024)
    if eof == -1: raise FileError    
    if eof > 0:
      total = total + s.raw[:eof]
    
    while eof > 0:
      eof = lib.read(f, s, 1024)
      if eof == -1: raise FileError
      if eof > 0:
        total = total + s.raw[:eof]
 
    lib.close(f)
    return total
  except FileError:
    lib.close(f)
    raise
  
  except:
    import traceback
    print "Unhandled exception"
    print traceback.format_exc()
    raise

def readFullFileSlow(path):
  with open(path,"rb") as f:
    return f.read()
    f.close()
    return text
    
def readFullFile(path):
  return readFullFileFast(path)
  if False:
    res_fast = readFullFileFast(path)
    res_slow = readFullFileSlow(path)
    
    if res_fast != res_slow:
      print "================ DIFF ================", path
      print res_fast
      print "--------------------------------------"
      print res_slow
    return res_slow

def killProcess(process):
  try:
    os.kill(int(process), signal.SIGTERM)
  except OSError:
    pass
  
def killProcessHard(process):
  os.kill(int(process), signal.SIGKILL)