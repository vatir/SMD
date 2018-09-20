# -*- coding: utf-8 -*-
"""
Created on Mon Feb 03 16:04:03 2014

@author: Koan
"""

try:
    RelativePath = '..';exec(open("../SetupModulePaths.py").read());del RelativePath
except:
    exec(open("SetupModulePaths.py").read())

from multiprocessing import freeze_support

def ParseChunk(BinChunk, ADC):
    import numpy as np
    k = np.zeros(len(BinChunk),dtype='f8')
    Start = BinChunk[0]
    for i in range(1,len(BinChunk)):
        End = BinChunk[i]
        k[i] = np.mean(ADC[Start:End])
        Start = BinChunk[i]
    return k[1:]
   
def MPChunk(SubArrays, ADC):
    import numpy as np
    import multiprocessing as mp
    results = []
    import sys
    sys.argv = ['C:/Users/Koan/Documents/PyProjects/SMD/CODE/TempScripts/']
    mp.set_executable('C:/Anaconda/pythonw.exe')
    N = mp.cpu_count()
    mp_pool = mp.Pool(processes=N)
    for n in range(N):
        results.append(mp_pool.apply_async(ParseChunk, (SubArrays[n], ADC)))

    Final = np.array([],dtype='f8')
    for result in results:
        k = result.get()
        Final = np.r_[Final,k]

    mp_pool.close()
    return Final

def MeanAll(ADC, Bins):

    StartTime = time()
    import numpy as np
    import multiprocessing as mp
    #mp.set_executable('C:/Anaconda/pythonw.exe')
    # Probably should be in this method

    # End Bins editting
    N = mp.cpu_count()
    SubArrays = np.array_split(Bins,N)
    '''
    # Attempt at subdividing the ADC array to reduce IPC transfer

    ADCSub = []
    for i in range(len(SubArrays)):
        if i == 0:
            Start = 0
        else:
            Start = SubArrays[i-1][-1]
        if i == N-1:
            End = SubArrays[i][-1]
        else:
            End = SubArrays[i+1][0]
        ADCSub.append(ADC[Start:End])

    #mp_pool = mp.Pool(processes=Processes)
    Final = np.array([],dtype='f8')
    for n in range(N):
        if n > 0:
            Bins = SubArrays[n] - SubArrays[n][0]
        else:
            Bins = SubArrays[n]
        k = np.zeros(len(Bins),dtype='f8')
        Start = Bins[0]
        for i in range(len(Bins)-1):
            End = Bins[i+1]
            k[i] = np.mean(ADCSub[n][Start:End])
            Start = Bins[i+1]
        Final = r_[Final,k]

    '''
    for n in range(N):
        if n == N-1:
            SubArrays[n] = np.r_[SubArrays[n],len(ADC)]
        else:
            SubArrays[n] = np.r_[SubArrays[n],SubArrays[n+1][0]]

    print "Setup Time Elapsed: %s" % (str(time() - StartTime))
    StartTime = time()
    

    '''
    # Non mp

    Final = np.array([],dtype='f8')
    for n in range(N):
        Final = r_[Final,ParseChunk(SubArrays[n],ADC)]
    temp = numpy.nan_to_num(Final[:-1])

    print "Non-mp Method Time Elapsed: %s" % (str(time() - StartTime))
    StartTime = time()
    '''
    Final = MPChunk(SubArrays, ADC)
    Final = numpy.nan_to_num(Final[:-1])
    print "mp Method Time Elapsed: %s" % (str(time() - StartTime))
    return Final

if __name__ == '__main__':
    freeze_support()
    import numpy as np
    from FILDA_Testing import *

    from time import time
    StartTime = time()
    TotalTime = time()


    ADC = Chan1ADC
    Bins = Chan1Bins
    Bins = np.array(np.r_[0,Bins],dtype=np.uint64)
    Bins = np.unique(Bins)

    Final = MeanAll(ADC, Bins)
    
    

    '''
    # Submit Work
    for i in range(Chunks):
        Start = i*(len(Chan_IPT)-1.0)/(1.0*Chunks)
        Stop = (i+1.0)*(len(Chan_IPT)-1.0)/(1.0*Chunks)
        print [Start,Stop]
        results = numpy.append(results,mp_pool.apply_async(UpdateACF, [Chan_IPT,Chan_ACF,MaxTauLength,Start,Stop]))
    
    for result in results:
        result.get()
        print sum(Chan_ACF)

    mp_pool.close()
    '''

    #   k[roll(diff(Bins),1)==0]
    #   nan_to_num(k) == Chan1LTM1[:-1]
    #   diff(Bins) == array(Chan1PC[1:-1],dtype='uint64'))
    print "Total Time Elapsed: %s" % (str(time() - TotalTime))
    StartTime = time()
