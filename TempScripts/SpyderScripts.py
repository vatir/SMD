#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 17:51:44 2013

@author: vatir
"""

RelativePath = '..';exec(open('../SetupModulePaths.py').read());del RelativePath

import tables
file_handle = tables.openFile("../../RESULTS/Data.h5",mode="r+")
print "Opened file (r+)"

from re import search

from numpy import array

Data = list()
ChannelCount = 0

from TTSPCfromBH.DataCalc import ADCData
from TTSPCfromBH.NormCalc import Norm

for g in file_handle.walk_groups():
	if g == file_handle.root:
		continue
	Result = search('(.*(mg water).*) \(Group\)',str(g))
	if Result == None or Result.group(1)=='':
		continue

	if g.TAC_Gain.read() == 3 and g.ChannelCount.read()==2:
		print Result.group(1)
		print g._DataType.read()
		if g._DataType.read() == "ADCData": Data.append(ADCData(PyTablesGroup=g))
		ChannelCount += g.ChannelCount.read()

TotalNorm = file_handle.get_node('/TotalNorm')._RawBinned.read()

Data = array(Data[3:])

from DataContainer.StorageArray import ChannelizedArray
#AllRawData = ChannelizedArray(len(Data[0].ADC_Intervals), ChannelCount, 'uint64')
#TotalNorm = ChannelizedArray(len(Data[0].ADC_Intervals), 2, 'uint64')
#k = 1
#for D in Data:
#	for i in range(D.ChannelCount):
#		AllRawData['Channel_'+str(k)] = D.RawData()['Channel_'+str(i+1)]
#		TotalNorm['Channel_'+str(i+1)] += D.RawData()['Channel_'+str(i+1)]
#		k += 1

"""
Scatter Data:
/2013-08-28 exp 4 mg water 150 degree light
/2013-08-28 exp 5 mg water 150 degree light again last time objective dried out
/2013-08-28 exp 6 mg water 150 degree light again
/2013-09-05 exp 4 mg water 150 pol
/2013-09-05 exp 5 mg water 240 pol
/2013-09-05 exp 6 mg water 200 pol
/2013-09-05 exp 7 mg water cp
"""

"""
Room Light:
/2013-05-29 gain 3 room light 60 sec
/2013-08-23 exp 2 gain 3 room light
/2013-08-27 exp 7 room light 3 gain
/2013-08-29 exp 1 room light 3 gain
/2013-08-30 exp 2 room light
/2013-08-30 exp 8 room light confirm
/2013-09-02 exp 2 room light lower count rate
/2013-09-03 exp 1 room right
"""
from Display import ADCPlot

Plots = list()

for D in Data:
	print "----------------------------"
	print sum(D.RawData()['Channel_1'])
	Temp = ChannelizedArray(len(Data[0].ADC_Intervals), 2, 'float64')
	for i in range(D.ChannelCount):
		Nonzero = D.RawData()['Channel_'+str(i+1)].nonzero() and TotalNorm['Channel_'+str(i+1)].nonzero()
		print sum(Nonzero)
		Temp['Channel_'+str(i+1)][Nonzero] = (1.0*D.RawData()['Channel_'+str(i+1)][Nonzero])/(1.0*TotalNorm['Channel_'+str(i+1)][Nonzero])
		print sum(Temp['Channel_'+str(i+1)])
	Plots.append(ADCPlot(D.ADC_Intervals, 
					Temp, 
					Title= str(D.DateCollected) + " Raw Normalization Data " + str(D.Filename), 
					YAxis="Intensity (Counts)", InSpyder=True))
	D._RawBinned = Temp.Copy
	print sum(D.RawData()['Channel_1'])
#Plots.append(ADCPlot(D.ADC_Intervals, 
#				TotalNorm, 
#				Title= "Total Norm", 
#				YAxis="Intensity (Counts)", InSpyder=True))

Show = False
if Show:
	for Plot in Plots:
			Plot.show()

Save = False
if Save:
	for i, Plot in enumerate(Plots):
		Plot.savefig(str(i)+'.png', dpi=300)
