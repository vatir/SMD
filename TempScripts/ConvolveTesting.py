# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 14:39:58 2013

@author: vatir
"""

Time = D.ADC_Intervals

Tau = 4.0
Decay = exp(-Time/Tau)
#plot(Time,Decay)
IRF = exp((-(Time)**2.0)/2.0)/((2*pi)**0.5)/sum(exp((-(Time)**2.0)/2.0)/((2*pi)**0.5))
IRF = SummedScatterTemp

#Responce = zeros(len(IRF))
#for t in arange(len(IRF)):
#	for tprime in arange(t):
#		L = IRF[tprime]
#		F = Decay[t-tprime]
#		Responce[t] += L*F

#plot(Time,convolve(IRF,Decay)[:4095])
#
#plot(Time,fft.irfft(fft.rfft(r_[zeros(4095),IRF])*fft.rfft(r_[zeros(4095),Decay]))[:4095])
def Convolve(IRF, Decay):
	length = len(Decay)
	return fft.irfft(fft.rfft(r_[zeros(length),IRF])*fft.rfft(r_[zeros(length),Decay]))[:length]

def Smooth(x,beta,window_len=11):
	 """ kaiser window smoothing """
	 # extending the data at beginning and at the end
	 # to apply the window at the borders
	 s = numpy.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
	 w = numpy.kaiser(window_len,beta)
	 y = numpy.convolve(w/w.sum(),s,mode='valid')
	 return y[(window_len-1)/2:len(y)-(window_len-1)/2]

plot(Time,Convolve(IRF,Decay))	
#plot(Time,Smooth(Convolve(IRF,Decay),100))
semilogy(Time,IRF)

#[semilogy(Time,smooth(IRF,beta)) for beta in arange(1,100,5)];
#plot(Time,smooth(IRF,30))
