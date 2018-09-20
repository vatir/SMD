import sys

exec(open("SetupModulePaths.py"))

# ------------------------------------------------
# Initial Setup Imports

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
# Adjustment Params
FWHM = 0.03  # ns
#Start= argmax(Time > 3.0)
Start=0
End= argmax(Time > 10.0)
Display = True
Plot = True
BHIter = 0  # Setting this to greater than 1 will turn on BasinHopping

# Use a brute force test within the Constrants to determine initial guess
# Number of locations to test for each param
BruteN = 0

#FitFuncTolerence = None
FitFuncTolerence = 10.0**-22.0 # Set to None for Default

#BG = 'Buffer'
#BG = 'Water'
from Testing import BG

#ScatterData = (AlignedNorm['Channel_1'] + AlignedNorm['Channel_2'])
ScatterData = AlignedIRF
SignalData  = AlignedRaw
BufferData  = AlignedBuffer

# ------------------------------------------------

# InitialResult = array([
#                       0.0,  # TimeStartOffset
#                       5.0, # LifeTime
#                       1.0,  # G
#                       0.5,  # BackgroundAmp
#                       0.0,  # BackgroundPos
#                       0.5,  # SignalAmp
#                       0.0,  # Offset
#                       0.0,  # Exp Lifetime 2
#                       0.0,  # Exp Amp 2
#                       ])
Constrants = None
SignalPeakTime = Time[argmax(SignalData['Channel_1'])]
from Testing import G

BGCenterOffset = DataShift*(Time[1]-Time[0])
print BGCenterOffset

Constrants = array([
                      (-0.2,0.5),  # TimeStartOffset
                      #(4.1,4.1), # LifeTime
                      (10.0**-6.0,5.0), # LifeTime
                      #(G,G),  # G
                      (1.0,2.0),  # G
                      #(10.0**-6.0,1.1),  # BackgroundAmp
                      (0.0,0.0),  # BackgroundAmp
                      #(-0.75,0.5),  # BackgroundPos
                      (-0.1+BGCenterOffset,0.08+BGCenterOffset),  # BackgroundPos
                      (10.0**-6.0,1.0), # SignalAmp
                      (-0.0,0.0),  # Offset
                      #(10.0**-6.0,10.0), # Exp Lifetime 2
                      #(4.1,4.1), # # Exp Lifetime 2
                      (0.0,0.0), # Exp Lifetime 2
                      #(0.0,0.3),  # Exp Amp 2
                      (0.0,0.0),  # Exp Amp 2
                      (0.0,0.0),  # BufferPos
                      (0.0,0.0),  # BufferAmp
                      #(0.0,1.0),  # BufferPos
                      #(0.0,1.0),  # BufferAmp
                      ])
# Constrants = array([
#                       (-0.2,0.2),  # TimeStartOffset
#                       #(4.1,4.1), # LifeTime
#                       (10.0**-6.0,5.0), # LifeTime
#                       (2.0,2.0),  # G
#                       (0.0,0.0),  # BackgroundAmp
#                       #(0.0,0.0),  # BackgroundAmp
#                       #(-0.75,0.5),  # BackgroundPos
#                       (-0.02,0.02),  # BackgroundPos
#                       (10.0**-6.0,2.0), # SignalAmp
#                       (0.0,0.0),  # Offset
#                       #(10.0**-6.0,10.0), # Exp Lifetime 2
#                       (0.0,0.0), # Exp Lifetime 2
#                       #(0.0,2.5),  # Exp Amp 2
#                       (0.0,0.0),  # Exp Amp 2
#                       ])

InitialResult = (diff(Constrants).T*random.rand(len(Constrants))+Constrants.T[0])[0]

# ------------------------------------------------

Scatter = ScatterData/sum(ScatterData)

if BG == 'Buffer':
    CurrentBackground = copy(BufferData)
    Buffer = ASBO
else:
    CurrentBackground = copy(Scatter)
    Buffer = zeros(len(Time))
    
Width = FWHM/(2.0*(2.0*log(2.0))**0.5)

LongTime = r_[-Time[::-1],Time]
Scatter = r_[zeros(len(Time)),Scatter]
Scatter = roll(Scatter,len(Time)-argmax(Scatter))

CutOff = 10.0
ScatterZero = Scatter[argmax(LongTime>CutOff)]
Scatter = Scatter - ScatterZero
Scatter[Scatter < 0.0] = 0.0
Scatter[LongTime>CutOff] = 0.0

#IRFI = InterpolatedUnivariateSpline(LongTime, Scatter)
IRFI = InterpolatedUnivariateSpline(LongTime, norm.pdf(LongTime,0.0,Width))

Buffer = r_[zeros(len(Time)),Buffer]
Buffer = roll(Buffer,len(Time)-argmax(Buffer))
BI = InterpolatedUnivariateSpline(LongTime, Buffer)

CurrentBackground = CurrentBackground/max(CurrentBackground)
CurrentBackgroundI = InterpolatedUnivariateSpline(Time, CurrentBackground)

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

# ------------------------------------------------

def SetZero(Channel):
    Channel = Channel - min(Channel[:argmax(Time>0.1)])
    Channel[Channel < 0.0] = 0.0
    return Channel

Channel1 = SignalData["Channel_1"]
Channel2 = SignalData["Channel_2"]

# Channel1 = SetZero(Channel1)
# Channel2 = SetZero(Channel2)

FitChannel1 = Channel1[Start:End]
FitChannel2 = Channel2[Start:End]

FitChannel1 = FitChannel1/sum(FitChannel1)
FitChannel2 = FitChannel2/sum(FitChannel2)

Channel1 = Channel1/sum(Channel1)
Channel2 = Channel2/sum(Channel2)

c1 = 1.0
c2 = 1.0
def objfunc(x, WithoutPenalties=True, Print=False):
    CurrentData = FitChannel1 + x[2]*FitChannel2
    CurrentData = CurrentData/max(CurrentData)
    Model, SignalR, BackgroundR = FitNormed(CurrentData,
                                            Time[Start:End],
                                            x[0],
                                            x[1],
                                            x[3],
                                            x[4],
                                            x[5],
                                            x[6],
                                            x[7],
                                            x[8],
                                            x[9],
                                            x[10],
                                            Start=Start, End=End)

    #Return = sum(((CurrentData - Model)**2.0)*CurrentData)/sum(CurrentData)#+((1.0-x[3])**2.0)/1000.0
    #Return = sum(((CurrentData - Model)**2.0)*CurrentData)*sum(CurrentData)/(len(CurrentData)-len(x))
    #Return = sum(((CurrentData - Model)**2.0))/(len(CurrentData)-len(x))
    #Return = sum(((log(CurrentData[NZI]) - log(Model[NZI]))**2.0)) + sum(((CurrentData - Model)**2.0)) - log(abs(max(CurrentData)-max(Model)))/len(CurrentData)
    global c1
    global c2
    
    NZI = ((CurrentData > 0) & (Model > 0))
    LogInternal = log(CurrentData[NZI]) - log(Model[NZI])
    #LogInternal = (CurrentData[NZI]) / (Model[NZI])
    #LogRes = (sum((LogInternal)**2.0*log(CurrentData[NZI])))/sum(log(CurrentData[NZI]))
    #LogResIndices = LogInternal.nonzero()
    #LogRes = sum((((LogInternal[LogResIndices])**2.0))*abs(LogInternal))
    #LogAdjust = sum(abs(LogInternal))
    #LogRes = sum(((LogInternal)**2.0))*log(sum(CurrentData[NZI]))
    LogRes = log(sum(((LogInternal)**2.0)))/2.0
    if LogRes < 0.0:
        LogRes = sum(((LogInternal)**2.0))
    
    #LogRes = 0.0
    
    #LogRes = sum(exp(LogInternal))
    #Res = sum(((CurrentData - Model)**2.0)*CurrentData)*LogAdjust*max(abs((CurrentData - Model)))
    #Res = sum(((CurrentData - Model)**2.0)*CurrentData)*sum(CurrentData)
    Res = sum(((CurrentData - Model)**2.0))
    if Print:
        print "Res: %s"%Res
        print "LogRes: %s"%LogRes
    #Res = sum((CurrentData - Model)**2.0)/sum((CurrentData - Model)**2.0)
    #PeakPenalty = ((max(CurrentData)-max(Model))**2.0)*len(CurrentData)*LogAdjust
    #PeakPenalty = ((max(CurrentData)-max(Model))**2.0)*100.0
#     PeakPosPenalty = ((argmax(CurrentData)-argmax(Model))**2.0)*len(CurrentData)/50.0

    #LogRes = 0.0
#     PeakPenalty = 0.0

    #DRMI = argmax(Time>FWHM*2.0)+argmax(CurrentData) # Location Twice the FWHM of the IRF from the peak
    #DecayPenalty = ((CurrentData[DRMI]-Model[DRMI])**2.0)*len(CurrentData)
    if WithoutPenalties:
        PeakPenalty = 0.0
        SignalSumPenalty = 0.0
        
#         PeakPenalty = ((max(CurrentData)-max(Model))**2.0)
#         SignalSumPenalty = (1.0-max(SignalR)-max(BackgroundR))**2.0
    else:
        PeakPenalty = ((max(CurrentData)-max(Model))**2.0)*(1.5**c1)
        SignalSumPenalty = ((1.0-max(SignalR)-max(BackgroundR)-x[6]-x[8])**2.0)*(1.5**c1)
        
    
    global OrigReturn
    try:
        Return = (LogRes + \
                 Res + \
                 PeakPenalty + \
                 SignalSumPenalty)\
                 /OrigReturn# + \
        return Return
    except:
        OrigReturn = LogRes + \
                     Res + \
                     PeakPenalty + \
                     SignalSumPenalty
        return 1.0

FuncDeltaList = []
def FixedObjFunc(f_new, x_new, f_old, x_old):
    global SmalledFuncDelta
    f_new = objfunc(x_new, WithoutPenalties=True, Print=True)
    f_old = objfunc(x_old, WithoutPenalties=True)
    FuncDeltaList.append(abs(f_new-f_old))
    
    if f_new < f_old:
        return "force accept"
    else:
        T = mean(FuncDeltaList) * 1.5
        print "New: %s : Old: %s" % (f_new, f_old)
        print "Exp: %s" % str(exp(-(f_new - f_old)/T))
        print "Temp: %s" % T
        if rand() < exp(-(f_new - f_old)/T):
            print "Accepted"
            return "force accept"
        else:
            print "Rejected"
            return False

def alUpdate(x):
    global c1
    global c2
    print c1
    c1 = c1 + 1
    c2 = c2 + 1 
             #DecayPenalty
#    Return = LogRes + \
#             Res + \
#             PeakPenalty# + \
#             #DecayPenalty
#            

# import numdifftools as n
# 
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

CurrentTime = time()
if BruteN > 1:
    InitialResult = optimize.brute(objfunc, Constrants, Ns=BruteN, finish=None, disp=Display)

StoredValues = list()

VarNames = [
            "TimeOffset",
            "LifeTime",
            "G",
            "BackgroundAmp",
            "BackgroundPos",
            "SignalAmp",
            "Offset",
            "Exp Lifetime 2",
            "Exp Amp 2",
            "BufferPos",
            "BufferAmp",
            ]

def Store(x, f, accepted): # Store Last Few Results
    print "----------I am Store-------------"
    for i, name in enumerate(VarNames):
        print "    %s : %s" % (name, x[i])
    print "ObjFunc Value: %s" % str(f)
    print "Accepted: %s" % str(accepted)
    StoredValues.append((x,f,accepted))
    print "----------End Store-------------"
    # Reset Penalties
    global c1
    global c2
    c1 = 1.0
    c2 = 1.0

# Methods = ['Nelder-Mead',
#             'Powell',
#             'CG',
#             'BFGS',
#             'L-BFGS-B',
#             'TNC',
#             'COBYLA',
#             'SLSQP'
#             ]

# Methods = ['SLSQP',
#            ]
# Methods = ['BFGS',
#            ]

Methods = ['L-BFGS-B',
           ]

print "!------------------------------!"
from Testing import DataSet
print DataSet
for i, name in enumerate(VarNames):
    print "    %s : %s" % (name, InitialResult[i])
print "Time: %s" % (time() - CurrentTime)
print "!------------------------------!"

Results = list()
Times = list()
MethodList = list()

for Method in Methods:
    CurrentTime = time()
    #Results.append(optimize.minimize(objfunc, InitialResult, method=Method, jac=JacReduce,hess=HessReduce, tol=None, bounds=Constrants, options={'disp':True}))
    #Results.append(optimize.minimize(objfunc, InitialResult, args = (i,), method=Method, jac=JacReduce, hess=HessReduce, tol=None, options={'disp':False}))
    #Results.append(optimize.minimize(objfunc, InitialResult, method=Method, bounds=Constrants, tol=10.0**-22.0, options={'disp':True}))
    
    if BHIter > 1:
        Results.append(
        optimize.basinhopping(
            objfunc,
            InitialResult,
            niter=BHIter,
            T=10.0,
            stepsize=0.5,
            minimizer_kwargs={
                              "method":Method,
                              "tol":FitFuncTolerence,
                              "bounds":Constrants,
                              "options":({'disp':Display}),
                              "callback":alUpdate,
                              },
            callback=Store,
            interval=50,
            disp=Display,
            niter_success=None,
            accept_test = FixedObjFunc
            )
        )
    else:
        Results.append(
           optimize.minimize(
                             objfunc,
                             InitialResult,
                             method=Method,
                             bounds=Constrants,
                             tol=FitFuncTolerence,
                             options={'disp':Display}
                             )
                       )

    Times.append(time()-CurrentTime)
    MethodList.append(Method)
    print str(Method)
    print "Objective Func: %s" % Results[-1].fun
    #print "Variable Results: %s" % Results[-1].x
    for i, name in enumerate(VarNames):
        print "    %s : %s" % (name, Results[-1].x[i])
    print "Time: %s" % (time() - CurrentTime)
    print "!------------------------------!"
    
Vars = []
LowestFuncValue = inf
for i, Result in enumerate(Results):
    if Result.fun < LowestFuncValue:
        LowestFuncValue = Result.fun
        Vars = Result.x
        MethodValue = MethodList[i]
        BestTime = Times[i]

for i in StoredValues:
    print i

print "Final Values:" 
for i, name in enumerate(VarNames):
    print "    %s : %s" % (name, Vars[i])

print "!------------------------------!"
print DataSet
print "LowestFuncValue: %s" % LowestFuncValue
print "Method: %s" % MethodValue
print "Time: %s" % BestTime

# ------------------------------------------------
from DataContainer.StorageArray import ChannelizedArray
PlotArray = ChannelizedArray(len(Time), 6, 'float64')
PlotArray.ChangeColName('Channel_1', 'Data')
PlotArray.ChangeColName('Channel_2', 'Data_{Fit}')
PlotArray.ChangeColName('Channel_3', 'Lifetime_1')
PlotArray.ChangeColName('Channel_4', 'Lifetime_2')
PlotArray.ChangeColName('Channel_5', 'Background')
PlotArray.ChangeColName('Channel_6', 'Fit')

CurrentData = FitChannel1 + Vars[2]*FitChannel2
CurrentData = CurrentData/max(CurrentData)
PlotArray['Data_{Fit}'][:len(CurrentData)] = CurrentData[:len(CurrentData)]

Data = Channel1 + Vars[2]*Channel2
Data = Data/max(Data)

PlotArray['Data'] = Data
PlotArray['Fit'], Temp, PlotArray['Background'] = FitNormed(Data, Time, Vars[0], Vars[1], Vars[3], Vars[4], Vars[5], Vars[6], Vars[7], Vars[8], Vars[9], Vars[10], Start=0, End=len(Time))


# PlotArray['Data'] = PlotArray['Data']
# PlotArray['Fit'] = PlotArray['Fit']
Temp, PlotArray['Lifetime_1'], Temp2 = FitNormed(Data, Time, Vars[0], Vars[1], 0.0, Vars[4], Vars[5], Vars[6], Vars[7], 0.0, 0.0, 0.0, Start=0, End=len(Time))
Temp, PlotArray['Lifetime_2'], Temp2 = FitNormed(Data, Time, Vars[0], Vars[1], 0.0, Vars[4], 0.0, Vars[6], Vars[7], Vars[8], 0.0, 0.0, Start=0, End=len(Time))
#PlotArray['Background'], Temp, Temp2 = FitNormed(Data, Time, Vars[0], Vars[1], Vars[3], Vars[4], 0.0, Vars[6], Vars[7], Vars[8], Start=0, End=len(Time))

for key in PlotArray.keys():
    if (PlotArray[key] <= 0.0).any():
        N = 10.0**-3.0
        #PlotArray[key][PlotArray[key] <= 0.0] = min(PlotArray[key][PlotArray[key] <= 0.0])
        PlotArray[key][PlotArray[key] <= N] = N

if Plot:
    from Display import ForkDisplay
    ForkDisplay(Time, 
                PlotArray, 
                Title="Fit Data : %s" % time(), 
                YAxis="Intensity (Normalized)"
                )
    ForkDisplay(Time, 
                PlotArray, 
                Title="Fit Data : %s" % time(), 
                YAxis="Intensity (Normalized)",
                Log=True
                )
#     ForkDisplay(Time, 
#                 PlotArray, 
#                 Title="Fit Data : %s" % time(), 
#                 YAxis="Intensity (Normalized)", 
#                 Residuals = ((PlotArray['Data'],PlotArray['Fit']),),
#                 Corr = True)

