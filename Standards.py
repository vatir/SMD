#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 1 2013

@author: vatir
"""
Shift = 40

if __name__ == '__main__':
    RelativePath = '.';exec(open('./SetupModulePaths.py').read());del RelativePath

import tables

file_handle = tables.openFile("../RESULTS/Data.h5",mode="r+")

from re import search

from numpy import array

Data = list()
ChannelCount = 0

from TTSPCfromBH.DataCalc import ADCData

for g in file_handle.walk_groups():
    if g == file_handle.root:
        continue
    Result = search('(.*(mg water).*) \(Group\)',str(g))
    if Result == None or Result.group(1)=='':
        continue

    if g.TAC_Gain.read() == 3 and g.ChannelCount.read()==2:
        if g._DataType.read() == "ADCData": Data.append(ADCData(PyTablesGroup=g))
        ChannelCount += g.ChannelCount.read()

from DataContainer.StorageArray import ChannelizedArray
TotalNormInt = ChannelizedArray(len(Data[0].ADC_Intervals), 2, 'uint64')
TotalNormInt._Data = file_handle.get_node('/TotalNorm')._RawBinned.read()
TotalNormInt._SetItems()
TotalNorm = ChannelizedArray(len(Data[0].ADC_Intervals), 2, 'float64')

"""
Scatter Data:
(Removed) /2013-08-28 exp 4 mg water 150 degree light
(Removed) /2013-08-28 exp 5 mg water 150 degree light again last time objective dried out
(Removed) /2013-08-28 exp 6 mg water 150 degree light again
/2013-09-05 exp 4 mg water 150 pol
/2013-09-05 exp 5 mg water 240 pol
/2013-09-05 exp 6 mg water 200 pol
/2013-09-05 exp 7 mg water cp
"""

Data = array(Data[3:])

from numpy import sum, roll, argmax, diff

SummedScatter = ChannelizedArray(len(Data[0].ADC_Intervals), 2, 'float64')
NoTAC_Norm_SummedScatter = ChannelizedArray(len(Data[0].ADC_Intervals), 2, 'float64')
for D in Data:
    Temp = ChannelizedArray(len(Data[0].ADC_Intervals), 2, 'float64')
    for Index in NoTAC_Norm_SummedScatter.keys():
        Nonzero = D._RawBinned[Index].nonzero()
        Temp[Index][Nonzero] = (1.0*D._RawBinned[Index][Nonzero])
        Temp[Index] = roll(Temp[Index],(Shift-argmax(Temp[Index])))
        NoTAC_Norm_SummedScatter[Index] += Temp[Index]
NoTAC_Norm_SummedScatter._SetItems()

for D in Data:
    Temp = ChannelizedArray(len(Data[0].ADC_Intervals), 2, 'float64')
    for Index in SummedScatter.keys():
        Nonzero = (D._RawBinned[Index].nonzero() and TotalNormInt[Index].nonzero()) 
        Temp[Index][Nonzero] = (1.0*D._RawBinned[Index][Nonzero])
        Temp[Index][Nonzero] = Temp[Index][Nonzero]/(1.0*TotalNormInt[Index][Nonzero])
        Temp[Index] = roll(Temp[Index],(Shift-argmax(Temp[Index])))
        SummedScatter[Index] += Temp[Index]
SummedScatter._SetItems()

for Index in TotalNorm.keys():
    TotalNorm[Index] = (1.0*TotalNormInt[Index])/(1.0*sum(TotalNormInt[Index]))
    SummedScatter[Index] = (1.0*SummedScatter[Index])/(1.0*sum(SummedScatter[Index]))
    NoTAC_Norm_SummedScatter[Index] = (1.0*NoTAC_Norm_SummedScatter[Index])/(1.0*sum(NoTAC_Norm_SummedScatter[Index]))
TotalNorm._SetItems()
SummedScatter._SetItems()
NoTAC_Norm_SummedScatter._SetItems()

file_handle.close()

from numpy import arange
Aligned_SummedScatter = ChannelizedArray(len(Data[0].ADC_Intervals), 4, 'float64')
for Index in SummedScatter.keys():
    Nonzero = SummedScatter[Index].nonzero()[0]
    NonzeroLength = len(Nonzero)
    Temp = roll(SummedScatter[Index],(Shift-argmax(SummedScatter[Index])))
    Temp[arange(NonzeroLength)] = Temp[Nonzero]
    Temp[NonzeroLength:] = 0
    Aligned_SummedScatter[Index]=(1.0*Temp)/(1.0*sum(Temp))

# Outside usable data
Time = D.ADC_Intervals.copy()
DeltaT = Time[1]-Time[0]
IRF_UnNormed = NoTAC_Norm_SummedScatter.Copy
IRF = SummedScatter.Copy
Norm = TotalNorm.Copy
AlignedNorm = Aligned_SummedScatter.Copy

'/2013-09-02 exp 10 buffer 150 pol'
'/2013-09-02 exp 11 buffer 240 pol'
'/2013-09-02 exp 12 buffer 200 pol'
'/2013-09-02 exp 13 buffer cp'
