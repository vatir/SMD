#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 1 2013

@author: vatir
"""
from Standards import Time
from Standards import Shift

if __name__ == '__main__':
    RelativePath = '.';exec(open('./SetupModulePaths.py').read());del RelativePath

import tables

file_handle = tables.openFile("../RESULTS/Data.h5",mode="r+")

from numpy import array

Data = list()
ChannelCount = 0

BufferExps = ['/2013-09-02 exp 10 buffer 150 pol',
            '/2013-09-02 exp 11 buffer 240 pol',
            '/2013-09-02 exp 12 buffer 200 pol',
            '/2013-09-02 exp 13 buffer cp'
            ]

from TTSPCfromBH.DataCalc import ADCData

Data = list()
for Exp in BufferExps:
    group = file_handle.get_node(Exp)
    Data.append(ADCData(PyTablesGroup=group))

from DataContainer.StorageArray import ChannelizedArray
TotalNormInt = ChannelizedArray(len(Data[0].ADC_Intervals), 2, 'uint64')
TotalNormInt._Data = file_handle.get_node('/TotalNorm')._RawBinned.read()
TotalNormInt._SetItems()
TotalNorm = ChannelizedArray(len(Data[0].ADC_Intervals), 2, 'float64')

file_handle.close()

from numpy import sum, roll, argmax

SummedBuffer = ChannelizedArray(len(Data[0].ADC_Intervals), 2, 'float64')
NoTAC_Norm_SummedBuffer = ChannelizedArray(len(Data[0].ADC_Intervals), 2, 'float64')
for D in Data:
    Temp = ChannelizedArray(len(Data[0].ADC_Intervals), 2, 'float64')
    for Index in NoTAC_Norm_SummedBuffer.keys():
        Nonzero = D._RawBinned[Index].nonzero()
        Temp[Index][Nonzero] = (1.0*D._RawBinned[Index][Nonzero])
        Temp[Index] = roll(Temp[Index],(Shift-argmax(Temp[Index])))
        NoTAC_Norm_SummedBuffer[Index] += Temp[Index]
NoTAC_Norm_SummedBuffer._SetItems()

import matplotlib.pylab as plt

#Target = argmax(Time > 0.4)
#Target = argmax(Time > 5.0)

for D in Data:
    Temp = ChannelizedArray(len(Data[0].ADC_Intervals), 2, 'float64')
    for Index in SummedBuffer.keys():
        Nonzero = (D._RawBinned[Index].nonzero() and TotalNormInt[Index].nonzero())
        Temp[Index][Nonzero] = (1.0*D._RawBinned[Index][Nonzero])
        #Temp[Index][Nonzero] = Temp[Index][Nonzero]/(1.0*TotalNormInt[Index][Nonzero])
        Temp[Index] = roll(Temp[Index],(Shift-argmax(Temp[Index])))
        SummedBuffer[Index] += Temp[Index]/sum(Temp[Index])
        #plt.plot(Time, Temp[Index]/(Temp[Index][Target]))
        #plt.plot(Time, Temp[Index]/sum(Temp[Index]))
SummedBuffer._SetItems()

from numpy import arange
Aligned_SummedBuffer = ChannelizedArray(len(Data[0].ADC_Intervals), 4, 'float64')
for Index in SummedBuffer.keys():
    Nonzero = SummedBuffer[Index].nonzero()[0]
    NonzeroLength = len(Nonzero)
    Temp = roll(SummedBuffer[Index],(Shift-argmax(SummedBuffer[Index])))
    Temp[arange(NonzeroLength)] = Temp[Nonzero]
    Temp[NonzeroLength:] = 0
    Aligned_SummedBuffer[Index]=(1.0*Temp)/(1.0*sum(Temp))

from Standards import AlignedNorm
from Common.Helpers import Smooth

SummedBuffer = Aligned_SummedBuffer['Channel_1']+Aligned_SummedBuffer['Channel_2']
SummedBuffer = SummedBuffer / sum(SummedBuffer)

SummedIRF = AlignedNorm['Channel_1']+AlignedNorm['Channel_2']
SummedIRF[:argmax(Time>0.1)] = 0.0
SummedIRF =SummedIRF /sum(SummedIRF)

Diff = SummedBuffer-SummedIRF
Diff[Diff < 0] = 0.0
Diff = Diff/sum(Diff)
SmoothedDiff = Smooth(Diff, 5.0, 25)
SmoothedDiff[:argmax(Time > 0.2)] = 0.0
SmoothedDiff = SmoothedDiff/sum(SmoothedDiff)

# Outside usable data

# All of these are single channel and normalized
from numpy import copy
AlignedUnSmoothedBuffer = copy(Diff) # Note Diff is Smoothed
AlignedBuffer = copy(SummedBuffer)
AlignedIRF = copy(SummedIRF)
ASBO = SmoothedDiff