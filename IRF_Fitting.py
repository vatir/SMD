# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 16:01:48 2013

@author: vatir
"""

if __name__ == '__main__':
    RelativePath = '.';exec(open('./SetupModulePaths.py').read());del RelativePath

from Standards import Time
from StandardBufferSetup import AlignedBuffer, AlignedIRF
from Fitting.Exp import Exp
from Fitting.Convolve import RawConvolveFFT
from scipy.stats import norm
from DataContainer.StorageArray import ChannelizedArray
from numpy import r_, zeros, argmax, roll, log, pi, sqrt, exp
from scipy.interpolate import InterpolatedUnivariateSpline


AlignedIRF = AlignedIRF/max(AlignedIRF)
AlignedBuffer = AlignedBuffer/max(AlignedBuffer)
AlignedIRF = r_[zeros(len(Time)),AlignedIRF]
AlignedBuffer = r_[zeros(len(Time)),AlignedBuffer]

CenterOffset = 100

LongTime = r_[-Time[::-1],Time]

AlignedBuffer = roll(AlignedBuffer,CenterOffset+len(Time)-argmax(AlignedBuffer))

AlignedIRF = roll(AlignedIRF,len(Time)-argmax(AlignedIRF))
IRFZero = AlignedIRF[argmax(LongTime>2.5)]
AlignedIRF0 = AlignedIRF - IRFZero
AlignedIRF0[AlignedIRF0 < 0.0] = 0.0
AlignedIRF0[LongTime>2.5] = 0.0


FWHM = 0.060
Width = FWHM/(2.0*(2.0*log(2.0))**0.5)
StartTime = 0.004

GIRF = norm.pdf(LongTime,StartTime,Width)
GIRF = exp(-(LongTime-StartTime)**2.0/(2.0*Width**2.0))/sqrt(2.0*pi)
GIRF = GIRF/sum(GIRF)

Decay = r_[zeros(len(Time)),Exp(Time, 1.0, 4.1)]
Convolved = RawConvolveFFT(Decay, AlignedIRF, None)
Convolved0 = RawConvolveFFT(Decay, AlignedIRF0, None)
GConvolved = RawConvolveFFT(Decay, GIRF, None)

TimeOffset = 0.0

IRFI = InterpolatedUnivariateSpline(LongTime, AlignedIRF)
IRFIV = IRFI(LongTime-TimeOffset)
IRFIV = IRFIV/sum(IRFIV)
IRFIVConv = RawConvolveFFT(Decay, IRFIV, None)

Plotting = ChannelizedArray(len(LongTime), 1, 'float64')

Plotting.ChangeColName("Channel_1", "Convolved")
Plotting['Convolved'] = roll(Convolved/max(Convolved),4095)

Plotting = Plotting.AddCol('Gauss')
Plotting['Gauss'] = GIRF/max(GIRF)

Plotting = Plotting.AddCol('GConv')
Plotting['GConv'] = roll(GConvolved/max(GConvolved),4095)

#Plotting = Plotting.AddCol('Scatter')
#Plotting['Scatter'] = AlignedIRF/max(AlignedIRF)

Plotting = Plotting.AddCol('IRFIV')
Plotting['IRFIV'] = IRFIV/max(IRFIV)

Plotting = Plotting.AddCol('IRFIV Conv')
Plotting['IRFIV Conv'] = roll(IRFIVConv/max(IRFIVConv),4095)

Plotting = Plotting.AddCol('IRF0')
Plotting['IRF0'] = AlignedIRF0/max(AlignedIRF0)

Plotting = Plotting.AddCol('IRF0 Conv')
Plotting['IRF0 Conv'] = roll(Convolved0/max(Convolved0),4095)

from Display import ForkDisplay
plt, fig = ForkDisplay(LongTime, 
            Plotting, 
            Title="Aligned Raw Data", 
            YAxis="Intensity (Counts)")
            