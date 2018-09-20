from numpy.fft import irfft, rfft
from numpy import r_, zeros, arange, array, argmax, roll, log

# def Convolve(IRF, Decay):
#     length = len(Decay)
#     return irfft(rfft(r_[zeros(length),IRF])*rfft(r_[zeros(length),Decay]))[:length]

# def Convolve(IRF,Decay):
#     temp = list()
#     SummedIRF = IRF[0]
#     for i in arange(len(IRF)):
#         temp.append(Decay[i]*SummedIRF)
#         SummedIRF += IRF[i]
#     return array(temp)

def Convolve(IRF,Decay):
    IRF = roll(IRF,-argmax(IRF))
#     from matplotlib.pylab import plot
#     plot(IRF)
    result = list()
    Length = len(Decay)
    for tk in arange(Length):
        SummedIRF = 0.0
        for t in arange(tk):
            #if t-tk > -50:
            SummedIRF += Decay[tk]*IRF[t-tk]
        result.append(SummedIRF)
    return array(result)

def ConvolveFFT(IRF, Decay):
    length = len(Decay)
    CenteredIRF = r_[zeros(length),IRF]
#     print argmax(CenteredIRF)
#     print CenteredIRF
    CenteredIRF = roll(CenteredIRF,length-argmax(CenteredIRF))
#     from matplotlib.pylab import plot
#     plot(CenteredIRF)
    return irfft(rfft(CenteredIRF)*rfft(r_[zeros(length),Decay]))[:length]

def GConvolveFFT(Decay, Time, Center, FWHM):
    length = len(Decay)
    from scipy.stats import norm
    Width = FWHM/2.0*(2.0*log(2.0))**0.5
    CenteredIRF = norm.pdf(r_[Time,Time+Time[-1]],Center+Time[-1],Width)
    CenteredIRF = CenteredIRF/sum(CenteredIRF)
#     from matplotlib.pylab import plot
#     plot(CenteredIRF)
    return irfft(rfft(CenteredIRF)*rfft(r_[zeros(length),Decay]))[:length]

def RawConvolveFFT(IRF, Decay, Length=None):
    return irfft(rfft(IRF)*rfft(Decay))[:Length]
