'''
Created on Nov 4, 2013

@author: vatir
'''
import numpy
import scipy.optimize
debug_level = 10

def ExpByFitResults(Time,Results):
        return Results[0]*numpy.exp(-Time/(1.0*Results[1]))

def Exp(Time, Amp, Lifetime):
        return Amp*numpy.exp(-Time/(1.0*Lifetime))

def ExpToFit(Time,Amp,Lifetime):
    if numpy.array(Lifetime == 0).any():
        return numpy.zeros(len(Time))
    try:
        if len(Amp) == 1:
            Amp = Amp[0]
            Lifetime = Lifetime[0]
            raise ValueError
        Results = numpy.ones(len(Time))
        for Amp,Lifetime in numpy.transpose([Amp,Lifetime]):
            Results += Amp*numpy.exp(-Time/(1.0*Lifetime))
        return Results
    except:
        return Amp*numpy.exp(-Time/(1.0*Lifetime))

def ExpToFitWithFlatInputs(*args):
    Amp = (args[1:])[::2]
    Lifetime = (args[1:])[1::2]
    return ExpToFit(args[0],numpy.array(Amp),numpy.array(Lifetime))

def FitExp(x_axis,data, GateIndex = 0,VarianceCutoff = 0.01, LastIndex=None, N = 1, Print = True):
    '''
    FitExp(x_axis, data, GateIndex = 0,VarianceCutoff = 0.01,LastIndex=True, N = 1, Print = True)
    
    GateIndex: Cut off the begining up to GateIndex
    LastIndex: Cut off after LastIndex (expecting an int)
    VarianceCutoff: If the variance of any of the variables is larger than value of the results * VarianceCutoff then return zeroes
    N: Number of exp to sum together
    '''
    
    if LastIndex == None:
        LastIndex = len(x_axis)
        
    x_axis = x_axis[GateIndex:LastIndex]
    data = data[GateIndex:LastIndex]
    
    try:
        CurveFitResults = scipy.optimize.curve_fit(ExpToFitWithFlatInputs, x_axis, data, p0=numpy.ones(2*N))
    except RuntimeError:
        if debug_level >= 2:
            print "Fit Failed!!!\n"
        return numpy.ones(len(data))

    if ((debug_level >= 2)&(Print == True)):
        try:
            print "Amplitude: " + str(CurveFitResults[0][0])
            print "Amplitude (Variance): " + str(CurveFitResults[1][0,0])
            print "Lifetime: " + str(CurveFitResults[0][1])
            print "Lifetime (Variance): " + str(CurveFitResults[1][1,1]) + "\n"

        except:
            print "Fit Failed!!!\n"
            return numpy.ones(len(data))

    if (abs(CurveFitResults[1].diagonal()) > abs(CurveFitResults[0])*VarianceCutoff).any():
        print "Variance in lifetime too high (Function has returned zero array)!!!!!!!!!!!!!!\n"
        return numpy.ones(len(data))
    else:
        return CurveFitResults[0]

if __name__ == '__main__':
    pass