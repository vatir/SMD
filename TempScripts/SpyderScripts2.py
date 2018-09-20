#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 14:31:56 2013

@author: vatir
"""
def ExpToFit(Time,Amp,Lifetime):
    if array(Lifetime == 0).any():
        return zeros(len(Time))
    try:
        if len(Amp) == 1:
            Amp = Amp[0]
            Lifetime = Lifetime[0]
            raise ValueError
        Results = ones(len(Time))
        for Amp,Lifetime in transpose([Amp,Lifetime]):
            Results += Amp*exp(-Time/(1.0*Lifetime))
        return Results
    except:
        return Amp*exp(-Time/(1.0*Lifetime))

def AddIRF(IRF,Decay,Shift=0):
	return Decay*cumsum(roll(IRF,-Shift))

def AddIRF2(IRF,Decay):
	return IRF*cumsum(Decay)

from Display import ADCPlot
from DataContainer.StorageArray import ChannelizedArray
from numpy import sum

SummedScatter = ChannelizedArray(len(Data[0].ADC_Intervals), 2, 'float64')
for D in Data:
	print "-------------------------"
	Temp = ChannelizedArray(len(Data[0].ADC_Intervals), 2, 'float64')
	for i in range(D.ChannelCount):
		Nonzero = D._RawBinned['Channel_'+str(i+1)].nonzero()
		Temp['Channel_'+str(i+1)][Nonzero] = (1.0*D._RawBinned['Channel_'+str(i+1)][Nonzero])
		Temp['Channel_'+str(i+1)] = roll(Temp['Channel_'+str(i+1)],(50-argmax(Temp['Channel_'+str(i+1)])))
		Temp['Channel_'+str(i+1)] = Temp['Channel_'+str(i+1)]/max(Temp['Channel_'+str(i+1)])
		SummedScatter['Channel_'+str(i+1)] += Temp['Channel_'+str(i+1)]/sum(Temp['Channel_'+str(i+1)])
	D._RawBinned = Temp.Copy
	
#	Plots.append(ADCPlot(D.ADC_Intervals, 
#					Temp, 
#					Title= str(D.DateCollected) + " Raw Normalization Data " + str(D.Filename), 
#					YAxis="Intensity (Counts)", InSpyder=True))

print "-------------------------"	
#plot(D.ADC_Intervals,convolve(SummedScatter['Channel_1'],exp(-1.0*D.ADC_Intervals/(4.0)),mode='same'))
SummedScatterTemp = SummedScatter['Channel_1'].copy()
#SummedScatterTemp[3500:] = 0.0
#SummedScatterTemp = SummedScatterTemp - SummedScatterTemp[0]
#SummedScatterTemp -= average(SummedScatterTemp[SummedScatterTemp[2400:2600].nonzero()])
#if (SummedScatterTemp < 0).any():
#	SummedScatterTemp = SummedScatterTemp - min(SummedScatterTemp)
SummedScatterTemp = SummedScatterTemp/sum(SummedScatterTemp)
DeltaT = diff(D.ADC_Intervals)[0]
#plot(D.ADC_Intervals,DeltaT*convolve(exp(-1.0*D.ADC_Intervals/(4.0)),SummedScatterTemp,mode='full')[:4095])

plot(D.ADC_Intervals,DeltaT*AddIRF(SummedScatterTemp,exp(-1.0*D.ADC_Intervals/(4.0))))
plot(D.ADC_Intervals,DeltaT*AddIRF2(SummedScatterTemp,exp(-1.0*D.ADC_Intervals/(4.0))))
#[plot(D.ADC_Intervals,DeltaT*AddIRF(SummedScatterTemp,exp(-1.0*D.ADC_Intervals/(4.0)),Shift=i)) for i in range(-50,50,10)];

#for k in arange(0.0,1.0,0.1):
#	temp = [exp(abs(-1.0*i/(4.0)**float(k))) for i in D.ADC_Intervals]
#	temp = temp/sum(temp)
#	plot(temp)
#plot(D.ADC_Intervals,DeltaT*array(FFT_FIR(SummedScatterTemp,exp(-1.0*D.ADC_Intervals/(4.0)))))

#plot(D.ADC_Intervals,DeltaT*Convolve(SummedScatterTemp,exp(-1.0*D.ADC_Intervals/(4.0)))[:4095])
"""
#def FFT_FIR(IRF,Decay):
#	h = zeros(2**13)
#	x = zeros(2**13)
#	#h[-1*len(IRF):] = IRF
#	h[-1*len(IRF):] = IRF
#	x = r_[zeros(2**13-2*len(Decay)),Decay,Decay[::-1]]
#	h = r_[zeros(2**13-2*len(IRF)),IRF,IRF[::-1]]
#	return map(norm,fft.irfft(fft.rfft(h)*fft.rfft(x)))[:4095]

#def FFT_FIR(IRF,Decay):
#	#x = r_[Decay,Decay[::-1]]
#	#h = r_[IRF,IRF[::-1]]
#	x = Decay
#	h = IRF
#	return map(norm,fft.ifft((fft.fft(h))*fft.fftshift(fft.fft(x))))[:4095]

#def Convolve(IRF,Decay):
#	temp = list()
#	for i in arange(len(IRF)):
#		temp.append(Decay[i]*sum(IRF[:i]))
#	return array(temp)

#def Convolve(IRF,Decay):
#	temp = list()
#	SummedIRF = IRF[0]
#	for i in arange(len(IRF)):
#		temp.append(Decay[i]*SummedIRF)
#		SummedIRF += IRF[i]
#	return array(temp)
"""
