#!/usr/bin/python
"""
Setup path to custom modules
"""

def AddSysPath(new_path):
    import sys, os
    # Standardize
    new_path = os.path.abspath(new_path)

    # MS-Windows does not respect case
    if sys.platform == 'win32':
        new_path = new_path.lower()

    # disallow bad paths
    do = -1
    if os.path.exists(new_path):
        do = 1
        
        # check against all paths currently available
        for x in sys.path:
            x = os.path.abspath(x)
            if sys.platform == 'win32':
                x = x.lower()
            if new_path in (x, x + os.sep):
                do = 0

        # add path if we don't already have it
        if do:
            sys.path.append(new_path)
            pass

from os import walk

try:
    vars()['RelativePath']
except:
    RelativePath = '.'

#import sys, os, os.path, inspect
#if '__file__' not in locals():
#    __file__ = inspect.getframeinfo(inspect.currentframe())[0]
#
#Dirs =  [x[0] for x in walk(os.path.dirname(os.path.abspath(__file__)))]
#for Directory in Dirs:
#    AddSysPath(Directory)

for Directory in [x[0] for x in walk(RelativePath)]:
    AddSysPath(Directory)
