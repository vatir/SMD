from Standards import IRF, Time, Norm, Shift
from Testing import AlignedRaw, Normed, Sum
# ------------------------------------------------
from Fitting.Convolve import Convolve
AvgIRF = (IRF['Channel_1'] + IRF['Channel_2'])/2.0
#AvgIRF = IRF['Channel_1']
#AvgIRF = IRF['Channel_2']
from Fitting.Exp import Exp

from numpy import array, argmax, inf, roll, r_, zeros
def FitNormed(Data, Time, Amp, ScatterAmp, Offset, Roll=0, Start=0, End=len(AvgIRF)):
    LifeTime = 4.1
    TempIRF = roll(AvgIRF, int(Roll))[Start:End]
    #IRF = r_[TempIRF[:int(0.15*len(TempIRF))],zeros(len(TempIRF)-int(0.15*len(TempIRF)))]
    IRF = TempIRF/sum(TempIRF)
    #Scatter = roll(TempIRF,(argmax(Data)-argmax(TempIRF)))
    Scatter = TempIRF
    Scatter = Scatter/max(Scatter)
    Convolved = Convolve(IRF, Exp(Time, 1.0, LifeTime)) + Convolve(IRF, Exp(Time+12.5, 1.0, LifeTime))
    #Convolved = Exp(Time, 1.0, LifeTime) + Exp(Time+12.5, 1.0, LifeTime)
    #Convolved = Convolve(IRF, Exp(Time, 1.0, LifeTime))
    #Convolved = Exp(Time, 1.0, LifeTime)
    #return Convolved + Scatter*ScatterAmp + Offset
    return Amp*Convolved/max(Convolved) + Scatter*ScatterAmp + Offset

# ------------------------------------------------
from numpy import array, argmax, inf, roll
from scipy import optimize

Start=argmax(Time > 0.1)
End=len(AvgIRF)
Start=0
End= argmax(Time > 10.0)


Data = Normed[Sum]/max(Normed[Sum])
#Data = Normed["Channel_1"]/max(Normed["Channel_1"])
#Data = Normed["Channel_2"]/max(Normed["Channel_2"])
#Data = AlignedRaw[Sum]/max(AlignedRaw[Sum])
#Data = AlignedRaw["Channel_1"]/max(AlignedRaw["Channel_1"])

import numdifftools as n
from numpy import log

Return = 10.0**10.0
def objfunc(x, Roll):
    #print x
#    global Return
    #Penalty = 1.0
#    if x[1] == 0.0:
#        Penalty = 10.0**5.0
#        return Return*Penalty
#    if x[0]+x[2] == 1.0:
#        Penalty = 10.0**5.0
#        return Return*Penalty
#    if x[0]+x[2] != 1.0:
#        Penalty = 10.0**5.0
#        return Return*Penalty
    Model = FitNormed(Data[Start:End], Time[Start:End], x[0], x[1], x[2], Roll, Start=Start, End=End)
    Return = sum(((Data[Start:End] - Model)**2.0))
    return Return

InitialGuess = array([
                      1.0,  # Amp
                      0.0,  # ScatterAmp
                      0.0   # Offset
                      ])

# Jac = n.Jacobian(objfunc, vectorized = True, romberg_terms=2)
# JacReduce = lambda x:array(Jac(x)[0])
# 
# Hess = n.Hessian(objfunc, vectorized = True)
# HessReduce = lambda x:array(Hess(x)[0])

"""
'Nelder-Mead',
'Powell',
'CG',
'BFGS',
'Newton-CG',
'Anneal',
'L-BFGS-B',
'TNC',
'COBYLA',
'SLSQP',
'dogleg',
'trust-ncg',
"""

Method = 'TNC'
Method = 'Anneal'
Method = 'L-BFGS-B'
Method = 'Newton-CG'
Method = 'Nelder-Mead'
Method = 'BFGS'
Method = 'CG'
Method = 'SLSQP'
Method = 'Powell'
# Constrants = array([
#                   (0.0,1.0),            # Amp
#                   (0.1,10.0),                     # LifeTime
#                   (0.0,1.0) # ScatterAmp
#                   ])
#InitialResult = optimize.brute(objfunc, Constrants, Ns=6)

#InitialResult = [ 0.68905324,  3.6148668,   0.79468868]
InitialResult = [ 0.5, 0.5, 0.0, 0.0]
print "!------------------------------!"
print InitialResult
print "!------------------------------!"
Results = list()

# Methods = ['Nelder-Mead',
#             'Powell',
#             'CG',
#             'BFGS',
#             'L-BFGS-B',
#             'TNC',
#             'COBYLA',
#             'SLSQP'
#             ]
Methods = ['Nelder-Mead',
            'Powell',
            #'CG',
            'BFGS',
            'L-BFGS-B',
            #'TNC',
            #'COBYLA',
            'SLSQP'
            ]
Methods = ['BFGS',
           ]

from numpy import arange
Times = list()
Rolls = list()
MethodList = list()
from time import time
for i in arange(-8,5,1):
    for Method in Methods:
        CurrentTime = time()
        #Results.append(optimize.minimize(objfunc, InitialResult, method=Method, jac=JacReduce,hess=HessReduce, tol=None, bounds=Constrants, options={'disp':True}))
        Results.append(optimize.minimize(objfunc, InitialResult, args = (i,), method=Method, tol=None, options={'disp':False}))
        Times.append(time()-CurrentTime)
        Rolls.append(i)
        MethodList.append(Method)
        print str(Method)
        print str(i)
        print Results[-1].fun
        print Results[-1].x
        print "!------------------------------!"
    
print "!------------------------------!"
Vars = []
LowestFuncValue = inf
for i, Result in enumerate(Results):
    if Result.fun < LowestFuncValue:
        LowestFuncValue = Result.fun
        Vars = Result.x
        RollValue = Rolls[i]
        MethodValue = MethodList[i]
        BestTime = Times[i]
    print "Roll Value: %s" % Rolls[i]
    print MethodList[i]
    print Result.x
    print Result.fun
    print "Time: %s" % Times[i]
    print "!------------------------------!"
print "Best Values: %s" % Vars
print "Best Roll Value: %s" % RollValue
print "LowestFuncValue: %s" % LowestFuncValue
print "Method: %s" % MethodValue
print "Time: %s" % BestTime
# ------------------------------------------------
from DataContainer.StorageArray import ChannelizedArray
PlotArray = ChannelizedArray(len(Time), 2, 'float64')
PlotArray.ChangeColName('Channel_1', 'Data')
PlotArray.ChangeColName('Channel_2', 'Fit')
PlotArray['Data'] = Data
PlotArray['Fit'] = FitNormed(Data, Time, Vars[0], Vars[1], Vars[2], RollValue, Start=0, End=len(Time))

Plot = True

if Plot:
    from Display import ForkDisplay
    print "\nPlotting: Aligned Data:"
    ForkDisplay(Time, 
                PlotArray, 
                Title="Fit Data : %s" % time(), 
                YAxis="Intensity (Normalized)")
