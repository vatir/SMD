from Standards import IRF, Time, Norm, Shift
from Testing import AlignedRaw, Normed
# ------------------------------------------------
from Fitting.Convolve import Convolve
AvgIRF = (IRF['Channel_1'] + IRF['Channel_2'])/2.0
from Fitting.Exp import Exp
from numpy import inf

def FitNormed(Time, Amp, LifeTime, Offset, ScatterAmp, Start=0, End=len(AvgIRF)):
    if LifeTime == 0.0:
        return inf
    global AvgIRF
    IRF = AvgIRF[Start:End]
    return Convolve(IRF, Exp(Time, Amp, LifeTime)) + Convolve(IRF, Exp(Time+12.5, Amp, LifeTime)) + Offset + IRF*ScatterAmp

import pyOpt

Start=0
End=len(AvgIRF)

def objfunc(x):
    print x
    fail = 0
    Model = FitNormed(Time, x[0], x[1], x[2], x[3], Start=Start, End=End)
    f = sum(Time - Model)**2.0
    g = []
    
    return f,g,  fail

opt_prob = pyOpt.Optimization('Minimize Chi**2',objfunc)



opt_prob.addVar('Amp','c',lower=0.0,upper=42.0,value=1.0)
opt_prob.addVar('LifeTime','c',lower=0.0,upper=42.0,value=2.0)
opt_prob.addVar('Offset','c',lower=0.0,upper=42.0,value=3.0)
opt_prob.addVar('ScatterAmp','c',lower=0.0,upper=42.0,value=4.0)

opt_prob.addObj('Minimize Chi**2', value=0.0, optimum=0.0)

print opt_prob

slsqp = pyOpt.SLSQP()

slsqp.setOption('IPRINT', -1)
[fstr, xstr, inform] = slsqp(opt_prob, disp_opts=True, sens_type='FD')

print opt_prob.solution(0)


# ------------------------------------------------
Plot = False

if Plot:
    from Display import ForkDisplay
    print "\nPlotting: Aligned Data:"
    ForkDisplay(Time, 
                AlignedRaw, 
                Title="Aligned Raw Data", 
                YAxis="Intensity (Counts)")
