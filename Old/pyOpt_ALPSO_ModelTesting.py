from Standards import IRF, Time, Norm, Shift
from Testing import AlignedRaw, Normed, Sum
# ------------------------------------------------
from Fitting.Convolve import Convolve
AvgIRF = (IRF['Channel_1'] + IRF['Channel_2'])/2.0
from Fitting.Exp import Exp

def FitNormed(Time, Amp, LifeTime, Offset, ScatterAmp, Start=0, End=len(AvgIRF)):
    IRF = AvgIRF[Start:End]
    return Convolve(IRF, Exp(Time, Amp, LifeTime)) + Convolve(IRF, Exp(Time+12.5, Amp, LifeTime)) + Offset + IRF*ScatterAmp

def FuncMin(Time, Amp, LifeTime, Offset, ScatterAmp, Start=0, End=len(AvgIRF)):
    return sum((Time-FitNormed(Time, Amp, LifeTime, Offset, ScatterAmp, Start, End))**2.0)
# ------------------------------------------------
Start=0
End=1950

from numpy import inf
import pyOpt

Start=0
End=len(AvgIRF)

Data = AlignedRaw[Sum]

def objfunc(x):
    #print x
    fail = 0
    Model = FitNormed(Time, x[0], x[1], x[2], x[3], Start=Start, End=End)
    f = sum(Data - Model)**2.0
    g = [0.0]
    
    return f,g,  fail

opt_prob = pyOpt.Optimization('Minimize Chi**2',objfunc)

opt_prob.addVar('Amp','c',lower=0.0,upper=1.5*max(Data),value=1.0*max(Data))
opt_prob.addVar('LifeTime','c',lower=0.000000001,upper=30.0,value=15.0)
opt_prob.addVar('Offset','c',lower=0.0,upper=1.0*Data[0],value=0.0)
opt_prob.addVar('ScatterAmp','c',lower=0.0,upper=0.5*max(Data)/max(AvgIRF),value=0.1*max(Data)/max(AvgIRF))
opt_prob.addObj('Minimize Chi**2', value=0.0, optimum=0.0)

print opt_prob

#optimizer = pyOpt.SDPEN()
min_func = pyOpt.ALPSO()

min_func.setOption('printOuterIters', 1000)
min_func.setOption('printInnerIters', 1000)
min_func.setOption('SwarmSize', 1000)

[fstr, xstr, inform] = min_func(opt_prob, disp_opts=True)

print "!------------------------------!"
print opt_prob.solution(0)
print "!------------------------------!"
print fstr
print "!------------------------------!"
print xstr
print "!------------------------------!"
print inform
print "!------------------------------!"

# ------------------------------------------------
from DataContainer.StorageArray import ChannelizedArray
PlotArray = ChannelizedArray(len(Time), 2, 'float64')
PlotArray.ChangeColName('Channel_1', 'Data')
PlotArray.ChangeColName('Channel_2', 'Fit')
PlotArray['Data'] = Data
PlotArray['Fit'] = FitNormed(Time, xstr[0], xstr[1], xstr[2], xstr[3], Start=0, End=len(Time))

Plot = True

if Plot:
    from Display import ForkDisplay
    print "\nPlotting: Aligned Data:"
    ForkDisplay(Time, 
                PlotArray, 
                Title="Aligned Raw Data", 
                YAxis="Intensity (Counts)")
