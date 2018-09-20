#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 4 2013

@author: vatir
"""

RelativePath = '.';exec(open('./SetupModulePaths.py').read());del RelativePath

import tables
file_handle = tables.openFile("../RESULTS/Data.h5",mode="r+")

from re import search


for g in file_handle.walk_groups():
    if g == file_handle.root:
        continue
    Result = search('(.*(ncp).*) \(Group\)',str(g))
    if Result == None or Result.group(1)=='':
        continue
    print Result.group(1)
    
    if g.TAC_Gain.read() == 3 and g.ChannelCount.read()==2:
        if g._DataType.read() == "ADCData":
            pass
        #print g._DataType.read()

file_handle.close()