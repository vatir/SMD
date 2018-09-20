import numpy
import scipy.optimize
debug_level = 10


def FitFunc(x_axis,data, FuncToFit, GateIndex = 0,VarianceCutoff = 0.01,LastIndex=None, NumberofVars = 2, Print = True, VarGuesses = None):
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
    
    if VarGuesses == None:
        VarGuesses = numpy.ones(NumberofVars)
    else:
        NumberofVars = len(VarGuesses)
    
    
    try:
        from functools import partial
        PartialFuncToFit = partial(FuncToFit, Start = GateIndex, End=LastIndex) 
        CurveFitResults = scipy.optimize.curve_fit(PartialFuncToFit, x_axis, data, p0=VarGuesses)
    except RuntimeError as e:
        print e
        if debug_level >= 2:
            print "Fit Failed!!!\n"
        return numpy.ones(NumberofVars)

    if ((debug_level >= 2)&(Print == True)):
        try:
            #print CurveFitResults
            for var in range(NumberofVars):
                print "Var "+str(var)+": " + str(CurveFitResults[0][var])
                print "Var "+str(var)+" (Variance): "+ str(CurveFitResults[1].diagonal()[var])

        except:
            print "Fit Failed!!!\n"
            return numpy.ones(NumberofVars)

    if (abs(CurveFitResults[1].diagonal()) > abs(CurveFitResults[0])*VarianceCutoff).any():
        print "Variance in lifetime too high (Function has returned zero array)!!!!!!!!!!!!!!\n"
        return CurveFitResults[0]
        return numpy.ones(NumberofVars)
    else:
        return CurveFitResults[0]

if __name__ == '__main__':
    pass