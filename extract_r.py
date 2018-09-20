# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 18:53:01 2013

@author: vatir
"""
from time import time
from Standards import Time
from Testing import AlignedRaw, DataShift
from StandardBufferSetup import AlignedBuffer, AlignedIRF, ASBO
from Fitting.Exp import Exp
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.stats import norm
from numpy import log, argmax, r_, zeros, array, inf, roll, random, diff, copy, mean, exp
from scipy import optimize
from Fitting.Convolve import RawConvolveFFT
from numpy.random import rand
# ------------------------------------------------
def FitNormed(
              Data,
              Time,
              StartTime,
              LifeTime,
              BackgroundAmp,
              BackgroundPos,
              SignalAmp,
              Offset,
              L2,
              A2,
              BufferPos,
              BufferAmp,
              Start=0,
              End=len(Time)
              ):

    #Decay = r_[zeros(len(Time)),Exp(Time, 1.0, LifeTime)]
    #EXP1 = Exp(Time, 1.0, LifeTime)
    EXP1 = Exp(Time, 1.0, LifeTime)+Exp(Time+12.5, 1.0, LifeTime)
    #EXP2 = Exp(Time, 1.0, L2)+Exp(Time+12.5, 1.0, L2)
    #Decay = r_[zeros(len(Time)),SignalAmp*EXP1+A2*EXP2]
    Decay = r_[zeros(len(Time)),EXP1]
    
    LongTime = r_[-Time[::-1],Time]
    #IRFIV = norm.pdf(LongTime,StartTime,Width)
    IRFIV = IRFI(LongTime-StartTime)
    IRFIV = IRFIV/sum(IRFIV)
    Convolved = RawConvolveFFT(Decay, IRFIV, len(Time))
    
    #CenteredIRF = r_[zeros(len(Time)), Scatter[Start:End]]
    #CenteredIRF = roll(CenteredIRF,len(Time)-argmax(CenteredIRF))
    #CenteredIRF = CenteredIRF/sum(CenteredIRF)
    #Convolved = RawConvolveFFT(Decay, CenteredIRF, len(Time))
    BGIV = CurrentBackgroundI(Time-BackgroundPos)
    BGIV = BGIV/max(BGIV)
    
    BIV = BI(Time-BufferPos)*BufferAmp
    
    SignalR = SignalAmp*Convolved
    #BackgroundAmp = 1.0-max(SignalR[Start:End])
    BackgroundAmp = abs(1.0-(SignalR+BIV)[argmax(BGIV)]-Offset)
    BackgroundR = BGIV*BackgroundAmp
    Result = SignalR + BackgroundR + Offset + BIV

    #return Result/max(Result)
    return Result, SignalR, BackgroundR

try:
    FitNormed
    Channel1
    Channel2
except:
    from ModelTesting import *

from DataContainer.StorageArray import ChannelizedArray
PlotArray = ChannelizedArray(len(Time),3, 'float64')
PlotArray.ChangeColName('Channel_1', 'r(t)_1')
PlotArray.ChangeColName('Channel_2', 'r(t)_2')
PlotArray.ChangeColName('Channel_3', 'r(t)_{Avg}')

#Vars=[0.0676060977225,
#    4.06009692902,
#    1.00602234087,
#    0.0,
#    -0.14037043243,
#    0.672045359399,
#    0.0,
#    0.0,
#    0.0,
#    0.0,
#    0.0]
Vars = [0.00442966076867,
    4.09174860001,
    1.8570495301,
    0.0,
    -0.136748200432,
    0.64733705373,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0]

Data = Channel1 + Vars[2]*Channel2
Data = Data/max(Data)

I, Temp, Temp2 = FitNormed(Data, Time, Vars[0], Vars[1], Vars[3], Vars[4], Vars[5], Vars[6], Vars[7], Vars[8], Vars[9], Vars[10], Start=0, End=len(Time))

Inz = I.nonzero()

Channel1 = Channel1/max(Channel1)
Channel2 = Channel2/max(Channel2)

PlotArray['r(t)_1'][Inz] = (((Channel2[Inz]*3.0)/I[Inz])-1.0)/(2.0)
PlotArray['r(t)_2'][Inz] = -((Channel1[Inz]*3.0)/I[Inz])+1.0

PlotArray['r(t)_1'] = PlotArray['r(t)_1']-mean(PlotArray['r(t)_1'][200:2000])
PlotArray['r(t)_2'] = PlotArray['r(t)_2']-mean(PlotArray['r(t)_2'][200:2000])

PlotArray['r(t)_1'] = PlotArray['r(t)_1']/max(PlotArray['r(t)_1'][:2000])
PlotArray['r(t)_2'] = PlotArray['r(t)_2']/max(PlotArray['r(t)_2'][:2000])

Length = argmax(Time>10.0)
PlotArray['r(t)_1'][Length:] = 0.0
PlotArray['r(t)_2'][Length:] = 0.0
PlotArray['r(t)_{Avg}'] = (PlotArray['r(t)_1']+PlotArray['r(t)_2'])/2.0

from Common.Helpers import Smooth
k = 10
PlotArray['r(t)_1'] = Smooth(PlotArray['r(t)_1'],k,31)
PlotArray['r(t)_2'] = Smooth(PlotArray['r(t)_2'],k,31)
PlotArray['r(t)_{Avg}'] = Smooth(PlotArray['r(t)_{Avg}'],k,31)

from Display import ForkDisplay
ForkDisplay(Time, 
            PlotArray, 
            Title="Anisotropy", 
            YAxis="Intensity (Counts)")
            
