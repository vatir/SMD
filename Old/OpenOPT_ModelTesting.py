from Standards import IRF, Time, Norm, Shift
from Testing import AlignedRaw, Normed
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
End=len(AvgIRF)

from numpy import inf
from FuncDesigner import oovars
from openopt import NLP
from openopt import NLLSP

Amp, LifeTime, Offset, ScatterAmp = oovars('Amp', 'LifeTime', 'Offset', 'ScatterAmp')

#print FuncMin(Time, 1.0, 1.0, 1.0, 1.0, Start, End)

objfunc = FuncMin(Time, Amp, LifeTime, Offset, ScatterAmp, Start, End)

startPoint = dict()
startPoint['Amp'] = 1.0
startPoint['LifeTime'] = 1.0
startPoint['LifeTime'] = 1.0
startPoint['ScatterAmp'] = 1.0

p = NLLSP(objfunc, startPoint)

# p.constraints = [
#                  (2*c+a-10)**2 < 1.5 + 0.1*b, (a-10)**2<1.5,
#                  a[0]>8.9, a+b > [ 7.97999836, 7.8552538 ],
#                  a < 9,
#                  (c-2)**2 < 1,
#                  b < -1.02,
#                  c > 1.01,
#                  (b + c * log10(a).sum() - 1) ** 2==0
#                  ]

r = p.solve('ralg')
RAmp, RLifeTime, ROffset, RScatterAmp = r(Amp, LifeTime, Offset, ScatterAmp)
print(RAmp, RLifeTime, ROffset, RScatterAmp)

# ------------------------------------------------
Plot = False

if Plot:
    from Display import ForkDisplay
    print "\nPlotting: Aligned Data:"
    ForkDisplay(Time, 
                AlignedRaw, 
                Title="Aligned Raw Data", 
                YAxis="Intensity (Counts)")
