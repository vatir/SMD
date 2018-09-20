#!/usr/bin/python
'''
Created on Oct 9, 2013

@author: vatir
'''

from collections import OrderedDict
#from IPython.utils.traitlets import Enum
class OrderedCounter(OrderedDict):
    'Counter that can return elements in order'
    i = -1
    def Next(self):
        if len(self.keys()) - 1 > self.i:
            self.i += 1
        else:
            self.i = 0
        return self[self.keys()[self.i]]

    def Reset(self):
        self.i = -1
        return True

Colors = OrderedCounter()
Colors['red'] = 'r'
Colors['blue'] = 'b'
Colors['green'] = 'g'
Colors['black'] = 'k'
Colors['cyan'] = 'c'
Colors['magenta'] = 'm'
Colors['yellow'] = 'y'

def ForkDisplay(ADC_Intervals, Traces, Title = 'ADC Data Plot', YAxis = 'Intensity', *args, **kargs):
    try:
        __IPYTHON__
#         if ('__IPYTHON__' in globals()['__builtins__'].keys()):
        return ADCPlot(ADC_Intervals, Traces, Title, YAxis, kargs)
    except:
        pass
    from multiprocessing import Process
    proc = Process(target=ADCPlot, args=(ADC_Intervals, Traces, Title, YAxis, kargs))
    proc.start()
    return proc

def SetupPlot(Title):
    #import matplotlib.pylab as plt
    from scipy.constants import golden
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    
    
    mpl.rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
    mpl.rc('text', usetex=True)
    mpl.rcParams['lines.linewidth'] = 1.0
    
    dpi = 150
    scale = 4.5
    Fig = plt.figure(Title, (golden*scale, scale), dpi=dpi)
    Fig.set_facecolor('white')

    return Fig

def AddLegend(Fig, Axes, Sorted = False):
    try:
        Fig.subplots_adjust(right=0.75)
        if Sorted:
            # Sort Legend
            import operator
            handles, labels = Axes.get_legend_handles_labels()
            hl = sorted(zip(handles, labels), key=operator.itemgetter(1))
            handles2, labels2 = zip(*hl)
            Axes.legend(handles2, labels2, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        else:
            Axes.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., fancybox=True, title=r'\textbf{Data}')
    except:
        print "Failed to create Legend!!!"
        pass

def ADCPlot(ADC_Intervals, Traces, Title = 'ADC Data Plot', YAxis = 'Intensity', *args):
    args = args[0]
    from matplotlib import use
    use("Qt4Agg", warn=False) # Normal Backend
    #use("WXAgg", warn=False)
    #use("WebAgg", warn=False) # Web based images
    #use("GTK3Cairo", warn=False) 
#     if not InSpyder:
#         use("Qt4Agg", warn=False)
#     else:
#         use("GTK3Cairo", warn=False)
    from numpy import amin, amax
    import matplotlib.pylab as plt
    fig = SetupPlot(Title)
    fig.clf(keep_observers=True)
    
    PlotCount = 1
    if 'Residuals' in args:
        PlotCount += 1
    if 'Corr' in args:
        PlotCount += 1
        
    if 'Residuals' in args:
        if 'Corr' in args:
            CorrAxes = fig.add_subplot(100*PlotCount + 10 + 3)
            CorrAxes.set_ylabel(r'\textbf{%s}'%"ACF")
            CorrAxes.set_xlim(ADC_Intervals[0],ADC_Intervals[-1])
            CorrAxes.set_xlabel(r'\textbf{Time \mathrm{(ns)}')
            from statsmodels.tsa.stattools import acf

        ResAxes = fig.add_subplot(100*PlotCount + 10 + 2)
        if PlotCount == 2:
            ResAxes.set_xlabel(r'\textbf{Time \mathrm{(ns)}')
        #ResFig = SetupPlot(str(Title) + " Residuals")
        #ResAxes.set_title(r'\textbf{%s}'%(Title))
        if 'Squared' in args:
            ResAxes.set_ylabel(r'\textbf{%s}'%"{R^2}")
        else:
            ResAxes.set_ylabel(r'\textbf{%s}'%"{R}")
        ResAxes.set_xlim(ADC_Intervals[0],ADC_Intervals[-1])
        
        ResYUpperLimit = 0.0
        ResYLowerLimit = 0.0
        CorrYUpperLimit = 0.0
        CorrYLowerLimit = 0.0
        for Res in args['Residuals']:
            CurrentColor = Colors.Next()
            Residual = (Res[0] - Res[1])
            if 'Corr' in args:
                ACF = acf(Residual, alpha = 0.01, nlags=len(Residual)-1, fft=True)
                CorrAxes.plot(ADC_Intervals, ACF[0], CurrentColor, aa=True, alpha = 0.8)
                CorrAxes.plot(ADC_Intervals, ACF[1][:,0], 'k', aa=True, alpha = 0.8)
                CorrAxes.plot(ADC_Intervals, ACF[1][:,1], 'k', aa=True, alpha = 0.8)
                if 1.1*amax(ACF[1][:,1][1:]) > CorrYUpperLimit:
                    CorrYUpperLimit = 1.1*amax(ACF[1][:,1][1:])
                if 1.1*amin(ACF[1][:,0][1:]) < CorrYLowerLimit:
                    CorrYLowerLimit = 1.1*amin(ACF[1][:,0][1:])
            if 'Squared' in args:
                Residual = Residual**2.0
            if 1.1*amax(Residual) > ResYUpperLimit:
                ResYUpperLimit = 1.1*amax(Residual)
            if 1.1*amin(Residual) < ResYLowerLimit:
                ResYLowerLimit = 1.1*amin(Residual)
            ResAxes.plot(ADC_Intervals, Residual, CurrentColor, aa=True, alpha = 0.8)
        ResAxes.set_xlim(ADC_Intervals[0],ADC_Intervals[-1])
        ResAxes.set_ylim(1.1*ResYLowerLimit,1.1*ResYUpperLimit)
        if 'Corr' in args:
            CorrAxes.set_ylim(1.1*CorrYLowerLimit,1.1*CorrYUpperLimit)
        Colors.Reset()

    axes = fig.add_subplot(PlotCount*100+11)
    if PlotCount == 1:
        axes.set_xlabel(r'\textbf{Time \mathrm{(ns)}')
    axes.set_title(r'\textbf{%s}'%(Title))
    axes.set_ylabel(r'\textbf{%s}'%(YAxis))
    
    axes.set_xlim(ADC_Intervals[0],ADC_Intervals[-1])
    axes.set_ylim(1.0*amin(Traces.values()),1.1*amax(Traces.values()))
    
    for key in Traces.keys():
        if 'Log' in args:
            axes.semilogy(ADC_Intervals, Traces[key], Colors.Next(), aa=True, label=key, alpha = 0.8)
        else:
            axes.plot(ADC_Intervals, Traces[key], Colors.Next(), aa=True, label=key, alpha = 0.8)
        
    Colors.Reset()
    
    # Make room for the Legend
    
    AddLegend(fig, axes)
    
    #Redraw twice to appease the Latex Gods
    plt.draw()
    plt.show()
    return fig, axes
    
if __name__ == '__main__':
    try:
        RelativePath = '..';exec(open("../SetupModulePaths.py").read());del RelativePath
    except:
        exec(open("SetupModulePaths.py").read())
    #RelativePath = '..';exec(open('../SetupModulePaths.py').read());del RelativePath

#     
# #     from Test import LoadData, LoadNorm
# #     ImportedData = LoadData(locals(), 
# #                             DataVariableName ='ImportedData', 
# #                             PrintOutput = False)
# #     
# #     ImportedData.RemoveChannel(4)
# #     
# #     CurrentNorm = LoadNorm(locals(),
# #              ImportedData, 
# #              DataVariableName ='CurrentNorm',
# #              ForceUpdate = False
# #              )
#     # File Testing
#     import tables
#     from TTSPCfromBH.NormCalc import Norm
#     from TTSPCfromBH.DataCalc import ADCData 
# 
#     file_handle = tables.openFile("../../RESULTS/NormCalcTesting.h5",mode="r+")
#     CurrentNorm = Norm(PyTablesGroup=file_handle.get_node('/',"Norm"))
#     CurrentData = ADCData(PyTablesGroup=file_handle.get_node('/',"Data"))
#     file_handle.close()
#     CurrentData.SetNorm(CurrentNorm)
# 
#     Plots = list()
#     
#     print "Plotting: Raw Normalization Data"
#     Plots.append(ADCPlot(CurrentNorm.ADC_Intervals, 
#                     CurrentNorm.RawData(), 
#                     Title="Raw Normalization Data", 
#                     YAxis="Intensity (Counts)"))
#      
#     print "\nPlotting: Raw Normalization Data without Outliers:"
#     Plots.append(ADCPlot(CurrentNorm.ADC_Intervals, 
#                     CurrentNorm.RawCleaned(), 
#                     Title="Raw Normalization Data without Outliers", 
#                     YAxis="Intensity (Counts)"))
# 
#     print "\nPlotting: Normalization"
#     Plots.append(ADCPlot(CurrentNorm.ADC_Intervals, 
#                     CurrentNorm.CurrentNorm(), 
#                     Title="Normalization", 
#                     YAxis="Normalized Intensity"))
#  
#     print "\nPlotting: Normalization without Outliers:"
#     Plots.append(ADCPlot(CurrentNorm.ADC_Intervals,
#                     CurrentNorm.NormCleaned(), 
#                     Title="Normalization without Outliers", 
#                     YAxis="Normalized Intensity"))
# 
#     print "\nPlotting: Raw Data:"
#     Plots.append(ADCPlot(CurrentData.ADC_Intervals, 
#                     CurrentData.RawData(), 
#                     Title="Raw Data", 
#                     YAxis="Intensity (Counts)"))
#     
#     print "\nPlotting: Normed Data:"
#     Plots.append(ADCPlot(CurrentData.ADC_Intervals, 
#                     CurrentData.GetData(), 
#                     Title="Normed Data", 
#                     YAxis="Intensity (Counts)"))
#     Show = False
#     if Show:
#         for Plot in Plots:
#                 Plot.show()
#     
#     Save = False
#     if Save:
#         for i, Plot in enumerate(Plots):
#             Plot.savefig(str(i)+'.png', dpi=300)

    from DataContainer.StorageArray import ChannelizedArray
    from numpy import arange, exp
    from numpy.random import rand
    Time = arange(0,4095,1)*16.6666/4095.0
    Testing = ChannelizedArray(len(Time), 2, 'float64')
    Testing.ChangeColName('Channel_1', 'Data')
    Testing.ChangeColName('Channel_2', 'Fit')
    Testing['Fit'] = exp(-Time/4.1)
    Testing['Data'] = exp(-Time/4.1) + (rand(4095) - 0.5)*0.1*Time*0.01

    print "\nPlotting:"
    ForkDisplay(Time, 
            Testing, 
            Title="Display Testing", 
            YAxis="Intensity (Normalized)", 
            Residuals = ((Testing['Data'],Testing['Fit']),),
            Corr = True)

    print "\nPlotting:"
    ForkDisplay(Time, 
            Testing, 
            Title="Display Testing", 
            YAxis="Intensity (Normalized)", 
            Residuals = ((Testing['Data'],Testing['Fit']),),
            Squared = True
            )

    print "\nPlotting:"
    ForkDisplay(Time, 
            Testing, 
            Title="Display Testing", 
            YAxis="Intensity (Normalized)")
    # Add a check to initialize latex on the first run (Maybe create and destroy a figure if there has not been one run so far)


# Random Stuff

#     import matplotlib.pyplot as plt
#     import Image
#     from cStringIO import StringIO
#     vFile = StringIO()
#     plt.savefig(vFile, dpi=100,format='png')
#     plt.savefig(vFile, dpi=100,format='png')
#     im = Image.open('temp.png')
#     im.show()
#     vFile.close()
    
