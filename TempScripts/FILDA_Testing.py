# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 12:22:07 2013

@author: vatir
"""

from time import time
TotalTime = time()
#if __name__ == '__main__':
try:
    RelativePath = '..';exec(open("../SetupModulePaths.py").read());del RelativePath
except:
    exec(open("SetupModulePaths.py").read())

from TTSPCfromBH.DataCalc import ADCData
from TTSPCfromBH.NormCalc import Norm
from TTSPCfromBH.TTPhotonDataImport import Data
import numpy

#    try:
#        AL
#    except:

from DataContainer.StorageArray import ChannelizedArray
try:
    PlotArray
except:
    PlotArray = ChannelizedArray(4095, 3, 'float64')

RunName = "C1"
PlotArray.ChangeColName('Channel_1', RunName)
RunName = "C2"
PlotArray.ChangeColName('Channel_2', RunName)
RunName = "Both"
PlotArray.ChangeColName('Channel_3', RunName)
#RunName = "488 High 200"
#PlotArray.ChangeColName('Channel_4', RunName)
#RunName = "H2O 200"
#PlotArray.ChangeColName('Channel_5', RunName)

#FileName = 'exp 10 ncp low count rate 150 pol very long'
#FolderName = 'Single_Molecule_Data/local_data/September/04/'

#DataSet = '/2013-09-02 exp 6 alexa high conc cp'; G = 1.0; BG = 'Water'
#DataSet = '/2013-09-02 exp 5 alexa high conc 200 pol'; G = 2.0; BG = 'Water'
#DataSet = '/2013-09-02 exp 3 alexa high conc 150 pol'; G = 1.5; BG = 'Water'
#DataSet = '/2013-09-02 exp 4 alexa high conc 240 pol'; G = 1.0/1.5; BG = 'Water'
#DataSet = '/2013-09-01 exp 8 1 nm dna in buffer cp'; G = 1.0; BG = 'Buffer'
#DataSet = '/2013-09-04 exp 5 dna low count rate 200 pol'; G = 2.0; BG = 'Buffer'
#DataSet = '/2013-09-02 exp 12 buffer 200 pol'; G = 2.0; BG = 'Buffer'
#DataSet = '/2013-09-02 exp 13 buffer cp'; G = 1.0; BG = 'Buffer'
#DataSet = '/2013-09-03 exp 5 low count rate alexa 200 pol'; G = 2.0; BG = 'Buffer'
#DataSet = '/2013-09-03 exp 2 low count rate alexa cp'; G = 1.0; BG = 'Buffer'
#DataSet = '/2013-09-04 exp 6 dna low count rate cp'; G = 1.0; BG = 'Buffer'
#DataSet = '/2013-09-01 exp 5 1 nm dna in buffer 150 pol'; G = 2.0; BG = 'Buffer'
#DataSet = '/2013-09-06 exp 2 ncp high count rate 150 pol'; G = 2.0; BG = 'Buffer'

FileName = 'exp 10 buffer 150 pol'
FolderName = 'Single_Molecule_Data/local_data/September/02/'
#AL = Data(FolderName, FileName, PrintStats=True)

FileName = 'exp 2 ncp high count rate 150 pol'
FolderName = 'Single_Molecule_Data/local_data/September/06/'
AL = Data(FolderName, FileName, PrintStats=True)

FileName = 'exp 5 1 nm dna in buffer 150 pol'
FolderName = 'Single_Molecule_Data/local_data/September/01/'
#AL = Data(FolderName, FileName, PrintStats=True)

FileName = 'exp 10 ncp low count rate 150 pol very long'
FolderName = 'Single_Molecule_Data/local_data/September/04/'
#AL = Data(FolderName, FileName, PrintStats=True)

#AL = Data('Single_Molecule_Data/local_data/September/02/', 'exp 3 alexa high conc 150 pol', PrintStats=True)

#RunName = "DNA 1 nM 200"
#AL = Data('Single_Molecule_Data/local_data/September/01/', 'exp 7 1 nm dna in buffer 200 pol', PrintStats=True)
#RunName = "NCP 1 nM 200"
#AL = Data('Single_Molecule_Data/local_data/September/02/', 'exp 9 1 nm ncp 200 pol', PrintStats=True)
#RunName = "NCP High 200"
#AL = Data('Single_Molecule_Data/local_data/September/05/', 'exp 11 ncp high count rate 200 pol', PrintStats=True)
#RunName = "488 High 200"
#AL = Data('Single_Molecule_Data/local_data/September/02/', 'exp 5 alexa high conc 200 pol', PrintStats=True)
#RunName = "H2O 200"
#AL = Data('Single_Molecule_Data/local_data/September/05/', 'exp 6 mg water 200 pol', PrintStats=True)

def BinByMT(Dataset,Time,BinWidth,SyncTime, Length, Block = 2**23):
    EvenLength = int(round(Time/BinWidth))-(int(round(Time/BinWidth))%2)
    TotalMT = int(round(Time/SyncTime))
    BinWidthMT = int(round(TotalMT/EvenLength))
    Bins = numpy.zeros(EvenLength,dtype='uint64')
    
    NextBinEdge = BinWidthMT
    CurrentBinIndex = 0
    BinsEdges = numpy.array(numpy.linspace(BinWidthMT,TotalMT,EvenLength),dtype='uint64')
    
    if len(Dataset) > Block:
        for i in numpy.arange(0, len(Dataset), Block):
            DatasetBlock = Dataset[i:i+Block]
            Bins += numpy.r_[DatasetBlock.searchsorted(BinsEdges[:-1], 'left'), \
                DatasetBlock.searchsorted(BinsEdges[-1], 'right')]
    else:
        Bins += numpy.r_[Dataset.searchsorted(BinsEdges[:-1], 'left'), \
        Dataset.searchsorted(BinsEdges[-1], 'right')]
    if Length > (len(Bins)-1):
        return numpy.hstack([numpy.diff(Bins),numpy.zeros(Length - (len(Bins)-1),dtype='uint64')])
    else:
        return numpy.diff(Bins)

def BinAvgADCByMT(ADC, MT,Time,BinWidth,SyncTime, Length=None, Block = 2**23):
    EvenLength = int(round(Time/BinWidth))-(int(round(Time/BinWidth))%2)
    TotalMT = int(round(Time/SyncTime))
    BinWidthMT = int(round(TotalMT/EvenLength))
    Bins = numpy.zeros(EvenLength,dtype='uint64')
    
    NextBinEdge = BinWidthMT
    CurrentBinIndex = 0
    BinsEdges = numpy.array(numpy.linspace(BinWidthMT,TotalMT,EvenLength),dtype='uint64')
    
    if len(MT) > Block:
        for i in numpy.arange(0, len(MT), Block):
            DatasetBlock = MT[i:i+Block]
            Bins += numpy.r_[DatasetBlock.searchsorted(BinsEdges[:-1], 'left'), \
                DatasetBlock.searchsorted(BinsEdges[-1], 'right')]
    else:
        Bins += numpy.r_[MT.searchsorted(BinsEdges[:-1], 'left'), \
        MT.searchsorted(BinsEdges[-1], 'right')]
    
    if Length != None:
        if Length > (len(Bins)-1):
            return numpy.hstack([numpy.diff(Bins),numpy.zeros(Length - (len(Bins)-1),dtype='uint64')])
    else:
        return Bins



#MT = AL.MT[:500000]
#ADC = AL.ADC[:500000]
#ROUTE = AL.Route[:500000]

Route = AL.Route
#Gated = AL.ADC_in_ns()>1.42 # Gateing
Gated = AL.ADC_in_ns() > 0.0 # Gateing

Route = AL.Route[Gated]
MT = (AL.MT[Gated])[Route==1]
ADC = (AL.ADC_in_ns()[Gated])[Route==1]

RunName = "C1 NCP Low 150"
#RunName = "C2 NCP Low 150"
#RunName = "NCP Low 150"

#Chan1MT = MT[ROUTE==1]
#Chan1ADC = ADC[ROUTE==1]
Chan1MT = MT
Chan1ADC = ADC

SyncTime = AL.SyncTime

BinWidth = 2.0*10**-3.0
#BinWidth = 1.0*10**-3.0

#BinWidth = 1.0
Time = (MT[-1])*SyncTime # Total experiment time rounded to nearest fast FFT length
from time import time
StartTime = time()
Chan1Bins = BinAvgADCByMT(Chan1ADC,
                          Chan1MT,
                          Time,
                          BinWidth,
                          SyncTime
                          )

MT = (AL.MT[Gated])[Route==3]
ADC = (AL.ADC_in_ns()[Gated])[Route==3]

Chan2MT = MT
Chan2ADC = ADC

Chan2Bins = BinAvgADCByMT(Chan2ADC,
                          Chan2MT,
                          Time,
                          BinWidth,
                          SyncTime
                          )

print "Binning Time: %s" % (time()-StartTime)
'''
# Slow method for bin processing

#array(map(mean,array_split(arange(100000),arange(10,100000,10))))
from numpy import mean, array, array_split, isfinite, histogram, zeros

StartTime = time()

SAData1 = array_split(Chan1ADC,Chan1Bins)
print "array_split Time: %s" % (time()-StartTime)

Chan1PC = array(map(len,SAData1))
print "map(len) Time: %s" % (time()-StartTime)

Chan1LTM1 = array(map(mean,SAData1))
print "map(mean) Time: %s" % (time()-StartTime)

del SAData1

SAData2 = array_split(Chan2ADC,Chan2Bins)

Chan2PC = array(map(len,SAData2))

Chan2LTM1 = array(map(mean,SAData2))

del SAData2

#Chan1PC = Chan1PC[:len(Chan1LTM1)-1]
#Chan1PC = Chan1PC[Chan1PC != 0]

#Chan1LTM1 = mean(hsplit(Chan1ADC,Chan1Bins),-1)
#Chan1LTM1 = Chan1LTM1[isfinite(Chan1LTM1)
BadIndicies = (isfinite(Chan1LTM1) == False)
Chan1LTM1[BadIndicies] = zeros(count_nonzero(BadIndicies))

BadIndicies = (isfinite(Chan2LTM1) == False)
Chan2LTM1[BadIndicies] = zeros(count_nonzero(BadIndicies))

print "Averaging Time: %s" % (time()-StartTime)
from Common.Helpers import Smooth
from time import time

StartTime = time()
LPCH = max(max(Chan1PC),max(Chan2PC))
'''



BinCount = 10
#BinCount = 100
"""
H = histogram(Chan1LTM1, bins=BinCount)
LM1BinPoints = (H[1] + diff(H[1])[0]/2.0)[:-1]
HD = H[0]/(1.0*sum(H[0]))

LM1 = ChannelizedArray(BinCount, 1, 'float64')

LM1['Channel_1'] = HD

from Display import ForkDisplay, ADCPlot
ForkDisplay(LM1BinPoints, 
            LM1,
            Title="FLDA", 
            YAxis="Probability")


ar = zeros((LPCH,BinCount))

for i in arange(LPCH):
    print i
    #ar[i] = Smooth(histogram(Chan1LTM1[Chan1PC[:len(Chan1LTM1)-1]==i], bins=4095)[0],50, 301)
    ar[i] = histogram(Chan1LTM1[Chan1PC==i], bins=BinCount)[0]

#for i in arange(4095):
#    ar[:,i] = Smooth(ar[:,i],10, 11)

print "Loop Time: %s" % (time()-StartTime)

#PlotArray['C1'] = HD[0]
#
#from Display import ForkDisplay, ADCPlot
#ForkDisplay(AL.ADC_Intervals(), 
#            PlotArray,
#            Title="FLDA", 
#            YAxis="Probability")

PCH = ChannelizedArray(LPCH, 1, 'float64')

H = histogram(Chan1PC, bins=LPCH)
PCBinPoints = (H[1] + diff(H[1])[0]/2.0)[:-1]
HD = H[0]/(1.0*sum(H[0]))

PCH['Channel_1'] = HD

from Display import ForkDisplay, ADCPlot
ForkDisplay(PCBinPoints, 
            PCH,
            Title="PCH", 
            YAxis="Probability")
"""
#plot(AL.ADC_Intervals(), HD)
#if 'Channel_1' in PlotArray.keys():
#    PlotArray.ChangeColName('Channel_1', RunName)
#else:
#PlotArray = PlotArray.AddCol(RunName)
#try:
#    PlotArray = PlotArray.DeleteCol('Channel_1')
#except:
#    pass

#PlotArray['C1'] = HD
#
#from Display import ForkDisplay, ADCPlot
#ForkDisplay(AL.ADC_Intervals(), 
#            PlotArray,
#            Title="FILDA", 
#            YAxis="Probability")


#SPlotArray = ChannelizedArray(4095, 3, 'float64')
#RunName = "C1"
#SPlotArray.ChangeColName('Channel_1', RunName)
#RunName = "C2"
#SPlotArray.ChangeColName('Channel_2', RunName)
#RunName = "Both"
#SPlotArray.ChangeColName('Channel_3', RunName)
#
#for k in PlotArray.keys():
#    SPlotArray[k] = Smooth(PlotArray[k],100, 101)
#    
#ForkDisplay(AL.ADC_Intervals(), 
#            SPlotArray,
#            Title="FILDA", 
#            YAxis="Probability")
print "Grand Total Time: %s" % (time()-TotalTime)