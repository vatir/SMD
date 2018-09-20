#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 1 2013

@author: vatir
"""
if __name__ == '__main__':
    RelativePath = '.';exec(open('./SetupModulePaths.py').read());del RelativePath

from Standards import IRF, Time, Norm, Shift
from numpy import argmax, roll, arange, exp
from Fitting.Exp import FitExp, ExpByFitResults, Exp
from Fitting.Fit import FitFunc
from Fitting.Convolve import Convolve

import tables
FileHandle = tables.openFile("../RESULTS/Data.h5",mode="r+")

DataShift = -30 # Relative to Var: Shift

#DataSet = '/2013-09-02 exp 6 alexa high conc cp'; G = 1.0; BG = 'Water'
#DataSet = '/2013-09-02 exp 5 alexa high conc 200 pol'; G = 2.0; BG = 'Water'
#DataSet = '/2013-09-02 exp 3 alexa high conc 150 pol'; G = 1.5; BG = 'Water'
DataSet = '/2013-09-02 exp 4 alexa high conc 240 pol'; G = 1.0/1.5; BG = 'Water'
#DataSet = '/2013-09-01 exp 8 1 nm dna in buffer cp'; G = 1.0; BG = 'Buffer'
#DataSet = '/2013-09-04 exp 5 dna low count rate 200 pol'; G = 2.0; BG = 'Buffer'
#DataSet = '/2013-09-02 exp 12 buffer 200 pol'; G = 2.0; BG = 'Buffer'
#DataSet = '/2013-09-02 exp 13 buffer cp'; G = 1.0; BG = 'Buffer'
#DataSet = '/2013-09-03 exp 5 low count rate alexa 200 pol'; G = 2.0; BG = 'Buffer'
#DataSet = '/2013-09-03 exp 2 low count rate alexa cp'; G = 1.0; BG = 'Buffer'
#DataSet = '/2013-09-04 exp 6 dna low count rate cp'; G = 1.0; BG = 'Buffer'
#DataSet = '/2013-09-01 exp 5 1 nm dna in buffer 150 pol'; G = 2.0; BG = 'Buffer'
#DataSet = '/2013-09-06 exp 2 ncp high count rate 150 pol'; G = 2.0; BG = 'Buffer'


from DataContainer.StorageArray import ChannelizedArray
Length = len(Time)
Dtype = 'float64'
Data = ChannelizedArray(Length, 2, Dtype)
Data._Data = FileHandle.get_node(DataSet)._RawBinned.read()

AlignedRaw = ChannelizedArray(Length, 4, 'float64')
AlignedRawNonzero = dict()
for Index in Data.keys():
    Nonzero = Norm[Index].nonzero()

    AlignedRaw[Index][Nonzero] = Data[Index][Nonzero]/Norm[Index][Nonzero]
    AlignedRaw[Index] = roll(AlignedRaw[Index],(Shift+DataShift-argmax(AlignedRaw[Index])))
    
    AlignedRawNonzero[Index] = AlignedRaw[Index].nonzero()[0]
    Nonzero = AlignedRaw[Index].nonzero()[0]
    NonzeroLength = len(Nonzero)
    
    AlignedRaw[Index][arange(NonzeroLength)] = AlignedRaw[Index][Nonzero]
    AlignedRaw[Index][NonzeroLength:] = 0
    
Sum = "Channel_{Sum}"
AlignedRaw.ChangeColName("Channel_3", Sum)

AlignedRaw[Sum] = (AlignedRaw['Channel_1'] + AlignedRaw['Channel_2'])

"""
from numpy import inf
AvgIRF = IRF['Channel_1']
def FitRaw(Time, Amp, LifeTime, Offset, ScatterAmp, Start=0, End=len(AvgIRF)):
     
    if LifeTime == 0.0:
        return inf
    return Exp(Time, Amp, LifeTime)+ Exp(Time+12.5, Amp, LifeTime) + 1.0*AvgIRF[Start:End]*ScatterAmp + Offset

    
    #return Convolve(AvgIRF, Exp(Time, Amp, LifeTime))+Convolve(AvgIRF, Exp(Time+12.5, Amp, LifeTime)) + 1.0*AvgIRF*ScatterAmp
#FuncToFit = partial(FitFunc, AvgIRF)
FitData = AlignedRaw['Channel_1']
Results = FitFunc(Time, FitData, FitRaw, LastIndex=argmax(Time > 10.0), VarGuesses = [max(FitData), 4.0, FitData[0], 2.0*10.0**8.0])
#print FitExp(Time, AlignedRaw[Sum], GateIndex=argmax(Time > 0.1), LastIndex=argmax(Time > 9.0))
print Results
"""

# AlignedRaw.ChangeColName("Channel_4", "Fit_{Sum}")
# AlignedRaw = AlignedRaw.DeleteCol('Channel_1')
# AlignedRaw = AlignedRaw.DeleteCol('Channel_2')
# AlignedRaw["Fit_{Sum}"] = FitRaw(Time, Results[0], Results[1], Results[2], Results[3])


Data._SetItems()
Data = Data.ViewAsType(Dtype)

from Common.Helpers import Smooth
Normed = ChannelizedArray(Length, 2, Dtype)
for Index in Data.keys():
    Nonzero = Norm[Index].nonzero()
    Normed[Index][Nonzero] = Data[Index][Nonzero]/Norm[Index][Nonzero]
    Normed[Index] = roll(Normed[Index],(Shift+DataShift-argmax(Normed[Index])))
    
    #Normed[Index] = Smooth(Normed[Index],100, 101)
    
    Normed[Index] = Normed[Index]/sum(Normed[Index])
    
    Nonzero = AlignedRawNonzero[Index] # Note this is using the AlignedRaw nonzeros due to normalization messing with the zeros
    NonzeroLength = len(Nonzero)
    Normed[Index][arange(len(Nonzero))] = Normed[Index][Nonzero]
    Normed[Index][NonzeroLength:] = 0.0
    
    #print FitExp(Time, Normed[Index], GateIndex=argmax(Time > 0.1), LastIndex=argmax(Time > 9.0))

Normed = Normed.AddCol()
Sum = "Channel_{Sum}"
Normed.ChangeColName(Normed.keys()[-1], Sum)

Normed[Sum] = (Normed['Channel_1'] + Normed['Channel_2'])/sum(Normed['Channel_1'] + Normed['Channel_2'])

"""
NormedResults = FitExp(Time, Normed[Sum], GateIndex=argmax(Time > 0.1), LastIndex=argmax(Time > 9.0), Print = True)

from numpy import inf
AvgIRF = (IRF['Channel_1']+IRF['Channel_2'])/2.0

def FitNormed(Time, Amp, LifeTime, Offset, ScatterAmp, Start=0, End=len(AvgIRF)):
    if LifeTime == 0.0:
        return inf
    IRF = AvgIRF[Start:End]
    return Convolve(IRF, Exp(Time, Amp, LifeTime)) + Convolve(IRF, Exp(Time+12.5, Amp, LifeTime)) + Offset + IRF*ScatterAmp

#FuncToFit = partial(FitFunc, AvgIRF)
FitData = Normed[Sum]
Results = FitFunc(Time, FitData, FitNormed, LastIndex=argmax(Time > 10.0), VarGuesses = [max(FitData), 4.0, FitData[0], max(FitData)/2.0])
#print FitExp(Time, AlignedRaw[Sum], GateIndex=argmax(Time > 0.1), LastIndex=argmax(Time > 9.0))
print Results

Normed = Normed.DeleteCol('Channel_1')
Normed = Normed.DeleteCol('Channel_2')
#Normed = Normed.DeleteCol(Sum)

Normed.ChangeColName("Channel_4", "Fit Results Exp_{Sum}")
Normed["Fit Results Exp_{Sum}"] = ExpByFitResults(Time, NormedResults)
Normed = Normed.DeleteCol("Fit Results Exp_{Sum}")

Normed.ChangeColName("Channel_5", "Fit Results_{Sum}")
Normed["Fit Results_{Sum}"] = FitNormed(Time, Results[0], Results[1], Results[2], Results[3])
"""

FileHandle.close()

if __name__ == '__main__':
    Plot = True
    
    if Plot:
        from Display import ForkDisplay
        Plots = list()
#        print "\nPlotting: IRF:"
#        Plots.append(ForkDisplay(arange(len(Time)), 
#                        IRF, 
#                        Title="IRF", 
#                        YAxis="Intensity (Counts)"))
#           
#         print "\nPlotting: Norm Data:"
#         Plots.append(ForkDisplay(Time, 
#                         Norm, 
#                         Title="Norm Data", 
#                         YAxis="Intensity (Counts)"))
#         
#         print "\nPlotting: Raw Data:"
#         Plots.append(ForkDisplay(Time, 
#                         Data, 
#                         Title="Raw Data", 
#                         YAxis="Intensity (Counts)"))
#          
#         print "\nPlotting: Normed Data:"
#         Plots.append(ForkDisplay(Time, 
#                         Normed, 
#                         Title="Normed Data", 
#                         YAxis="Intensity (Normalized)"))
#          
        
        print "\nPlotting: Aligned Data:"
        Plots.append(ForkDisplay(Time, 
                        AlignedRaw, 
                        Title="Aligned Raw Data", 
                        YAxis="Intensity (Counts)"))
        
        from DataContainer.StorageArray import ChannelizedArray
        PlotArray = ChannelizedArray(len(Time), 3, 'float64')
        PlotArray.ChangeColName('Channel_3', 'r(t)')
        PlotArray["Channel_1"] = (AlignedRaw['Channel_1']/sum(AlignedRaw['Channel_1']))
        PlotArray["Channel_2"] = (AlignedRaw['Channel_2']/sum(AlignedRaw['Channel_2']))
        NZI = (AlignedRaw['Channel_1'] + AlignedRaw['Channel_2']) != 0
        PlotArray['r(t)'][NZI] = (PlotArray["Channel_1"][NZI]-PlotArray["Channel_2"][NZI])/((PlotArray["Channel_1"][NZI]+G*PlotArray["Channel_2"][NZI]))
        PlotArray["Channel_1"] = (AlignedRaw['Channel_1'])/max(AlignedRaw['Channel_1'])
        PlotArray["Channel_2"] = (AlignedRaw['Channel_2'])/max(AlignedRaw['Channel_1'])

        print "\nPlotting: Anisotropy Data"
        Plots.append(ForkDisplay(Time, 
                        PlotArray, 
                        Title="Anisotropy", 
                        YAxis="Intensity (Counts)"))
        '''
        from Standards import IRF, Time, Norm, Shift, AlignedNorm
        from scipy.interpolate import Rbf, InterpolatedUnivariateSpline, interp1d
        from numpy import linspace
        from time import time
        
        TimeI = interp1d(range(4095), Time)
        NewIndex = linspace(0,4094,num=4095*10)
        LargeTime = TimeI(NewIndex)
        IRF = (AlignedNorm['Channel_1'] + AlignedNorm['Channel_2'])/max(AlignedNorm['Channel_1'] + AlignedNorm['Channel_2'])
        CurrentTime = time()
        IRFIUS = InterpolatedUnivariateSpline(Time, IRF)
        print "IUS Spline Generated in: %s" % (time() - CurrentTime)
        CurrentTime = time()
        IRFIUS(Time+0.001)
        print "IUS Result Generated in: %s" % (time() - CurrentTime)

#         CurrentTime = time()
#         IRFRBF = Rbf(Time, IRF)
#         print "RBF Spline Generated in: %s" % (time() - CurrentTime)
        
        import matplotlib.pylab as plt
        plt.plot(Time, IRF, label = "Raw", marker="+")
        plt.plot(LargeTime, IRFIUS(LargeTime), label = "IUS")
        plt.plot(Time, IRFIUS(Time-5.0), label = "IUS Test")
        #plt.plot(LargeTime, IRFRBF(LargeTime), label = "RBF")
        plt.ylim(0.0,1.1)
        plt.legend(loc='best')
        plt.show()
        '''
        
        from Fitting.Convolve import Convolve, ConvolveFFT, GConvolveFFT, RawConvolveFFT
        from numpy import r_, zeros
        
        LongTime = r_[-Time[::-1],Time]
        Testing = ChannelizedArray(len(LongTime), 3, 'float64')

        Testing.ChangeColName('Channel_1', 'Raw')
        Testing.ChangeColName('Channel_2', 'Gauss')
        Testing.ChangeColName('Channel_3', 'IUS')
        
        from numpy import log
        from scipy.stats import norm
        from Standards import AlignedNorm
        IRF = (AlignedNorm['Channel_1'] + AlignedNorm['Channel_2'])
        CenteredIRF = r_[zeros(len(Time)),IRF]
        CenteredIRF = roll(CenteredIRF,len(Time)-argmax(CenteredIRF))
        CenteredIRF = CenteredIRF/max(CenteredIRF)
        Testing['Raw'] = Smooth(CenteredIRF,30.0, 11)
        Testing['Raw'] = Testing['Raw']/max(Testing['Raw'])
        from scipy.interpolate import InterpolatedUnivariateSpline
        CurrentScatterI = InterpolatedUnivariateSpline(LongTime, CenteredIRF)
        Testing['IUS'] = CurrentScatterI(LongTime)
        
        FWHM = 0.040  # ns
        Width = FWHM/2.0*(2.0*log(2.0))**0.5
        LongTime = r_[-Time[::-1],Time]
        
        IRF = norm.pdf(LongTime, Time[0], Width)
        IRF = IRF/max(IRF)
        Testing['Gauss'] = IRF
        
        print "\nPlotting: Aligned Data:"
        Plots.append(ForkDisplay(LongTime, 
                        Testing, 
                        Title="Convolution Testing", 
                        YAxis="Intensity (Counts)"))
        
        Decay = r_[zeros(len(Time)),Exp(Time, 1.0, 4.1)+Exp(Time+12.5, 1.0, 4.1)]
        import matplotlib.pylab as plt
        plt.plot(Time, RawConvolveFFT(Testing['Gauss'], Decay, len(Time)))
        plt.plot(Time, RawConvolveFFT(Testing['Raw'], Decay, len(Time)))
        plt.show()
#         from time import time
#         
#         CurrentTime = time() 
#         Testing['FFT'] = ConvolveFFT(NormIRF, Decay)
#         Testing['FFT'] = Testing['FFT']/max(Testing['FFT'])
#         print "FFT (Time) :%s" % (time() - CurrentTime)
#         print Testing['FFT']
# 
#         Testing = Testing.AddCol("GFFT")
#         CurrentTime = time()
#         Testing['GFFT'] = GConvolveFFT(Decay, Time, 5.0, 0.04)
#         Testing['GFFT'] = Testing['GFFT']/max(Testing['GFFT'])
#         print "GFFT (Time) :%s" % (time() - CurrentTime)
#         print Testing['GFFT']
# 
#         CurrentTime = time()
#         Testing['Traditional'] = Convolve(NormIRF, Decay)
#         Testing['Traditional'] = Testing['Traditional']/max(Testing['Traditional'])
#         print "Traditional (Time) :%s" % (time() - CurrentTime)
#         print Testing['Traditional'] 
#         
#         print "\nPlotting: Aligned Data:"
#         Plots.append(ForkDisplay(Time, 
#                         Testing, 
#                         Title="Convolution Testing", 
#                         YAxis="Intensity (Counts)"))

"""                        
        AvgIRF = (IRF['Channel_1']+IRF['Channel_2'])/2.0
        AvgIRF = IRF['Channel_1']
        def FitNormed(Data, Time, Amp, LifeTime, ScatterAmp, Roll, Start=0, End=len(AvgIRF)):
            TempIRF = roll(AvgIRF, int(Roll))
            IRF = TempIRF[Start:End]/sum(TempIRF[Start:End])
            Scatter = roll(TempIRF[Start:End],(argmax(Data)-argmax(TempIRF[Start:End])))
            Scatter = Scatter/max(Scatter)
            #Convolved = Convolve(IRF, Exp(Time, 1.0, LifeTime)) + Convolve(IRF, Exp(Time+12.5, 1.0, LifeTime))
            Convolved = Convolve(IRF, Exp(Time, 1.0, LifeTime))
            return Amp*Convolved/max(Convolved) + Scatter*ScatterAmp
            #return Exp(Time, Amp, LifeTime)  + Offset + IRF*ScatterAmp + Exp(Time+12.5, Amp, LifeTime)        
#         def FitNormed(Data, Time, Amp, LifeTime, ScatterAmp, Start=0, End=len(AvgIRF)):
#             IRF = roll(AvgIRF[Start:End],(argmax(AvgIRF[Start:End]))-argmax(AvgIRF[Start:End]))
#             IRF = IRF/sum(IRF)
#             return Convolve(IRF, Exp(Time, Amp, LifeTime))  + IRF*ScatterAmp + Convolve(IRF, Exp(Time+12.5, Amp, LifeTime))        
        
        ScatterAmp = 0.2
        Roll = -0.0
        
        Data = ChannelizedArray(len(Time), 2, 'float64')
        Data['Channel_1'] = Normed["Channel_1"]/max(Normed["Channel_1"])
        Data['Channel_2'] = FitNormed(Data['Channel_1'], Time, 2.49755603e-03, 2.82970585e+00, 2.29805850e-03, -7.0, Start=0, End=len(AvgIRF))

        print "\nPlotting: Aligned Data:"
        Plots.append(ForkDisplay(Time, 
                        Data, 
                        Title="Aligned Raw Data", 
                        YAxis="Intensity (Counts)"))

        def Fit(Time, Amp, LifeTime, ScatterAmp, Roll, Start=0, End=len(AvgIRF)):
            TempIRF = roll(AvgIRF, int(Roll))
            IRF = TempIRF[Start:End]/sum(TempIRF[Start:End])
            Scatter = TempIRF[Start:End]
            Scatter = Scatter/max(Scatter)
            #Convolved = Convolve(IRF, Exp(Time, 1.0, LifeTime)) + Convolve(IRF, Exp(Time+12.5, 1.0, LifeTime))
            Convolved = Convolve(IRF, Exp(Time, 1.0, LifeTime))
            return Amp*Convolved/max(Convolved) + Scatter*ScatterAmp
            #return Exp(Time, Amp, LifeTime)  + Offset + IRF*ScatterAmp + Exp(Time+12.5, Amp, LifeTime)

#         def Fit(Time, Amp, LifeTime, ScatterAmp, Start=0, End=len(AvgIRF)):
#             IRF = AvgIRF[Start:End]
#             IRF = IRF/sum(IRF)
#             return Convolve(IRF, Exp(Time, Amp, LifeTime))  + IRF*ScatterAmp + Convolve(IRF, Exp(Time+12.5, Amp, LifeTime))               

        TestCases = arange(0.0,1.0,0.1)
        Length = len(TestCases)
        Data = ChannelizedArray(len(Time), Length, 'float64')
        for i, Amp in enumerate(TestCases):
            Data.ChangeColName('Channel_' + str(i+1), "Amp " + str(Amp))
            Data["Amp " + str(Amp)] = Fit(Time, Amp, 4.1, ScatterAmp, Roll, Start=0, End=len(AvgIRF))

        print "\nPlotting: Aligned Data:"
        Plots.append(ForkDisplay(Time, 
                        Data, 
                        Title="Aligned Raw Data", 
                        YAxis="Intensity (Counts)"))
             
        TestCases = arange(1.0,10.0,1.0)
        Length = len(TestCases)
        Data = ChannelizedArray(len(Time), Length, 'float64')
        for i, LifeTime in enumerate(TestCases):
            Data.ChangeColName('Channel_' + str(i+1), "LifeTime " + str(LifeTime))
            Data["LifeTime " + str(LifeTime)] = Fit(Time, 1., LifeTime, Roll, ScatterAmp, Start=0, End=len(AvgIRF))

        print "\nPlotting: Aligned Data:"
        Plots.append(ForkDisplay(Time, 
                        Data, 
                        Title="Aligned Raw Data", 
                        YAxis="Intensity (Counts)"))

        # IRF Shape Testing
        from numpy import log
        from scipy.stats import norm
        NormName = "Norm_{Dist}"
        IRF = IRF.AddCol(Sum)
        IRF["Channel_1"] = IRF["Channel_1"]/max(IRF["Channel_1"])
        IRF["Channel_2"] = IRF["Channel_2"]/max(IRF["Channel_2"])
        IRF[Sum] = (IRF["Channel_1"]+IRF["Channel_2"])/max(IRF["Channel_1"]+IRF["Channel_2"])
        IRF = IRF.DeleteCol("Channel_1")
        IRF = IRF.DeleteCol("Channel_2")

        for FWHM in arange(0.01,0.05,0.01):
            ChannelName = str(NormName) + " %s" % FWHM
            IRF = IRF.AddCol(ChannelName)
            #FWHM = 0.040  # ns
            Width = FWHM/2.0*(2.0*log(2.0))**0.5
            
            NormDist = norm.pdf(Time,Time[argmax(IRF[Sum])],Width)
            IRF[ChannelName] = NormDist/max(NormDist)
        
        
        
        print "\nPlotting: IRF:"
        Plots.append(ForkDisplay(Time, 
                        IRF, 
                        Title="IRF", 
                        YAxis="Intensity (Counts)"))

"""