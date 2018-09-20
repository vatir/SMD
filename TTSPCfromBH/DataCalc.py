#!/usr/bin/python
'''
Created on Oct 10, 2013

@author: vatir
'''
# Use this section if direct CLI calling is desired

try:
    from TTSPCfromBH.BaseData import BaseData
    from TTSPCfromBH.NormCalc import Norm
except:
    try:
        RelativePath = '..';exec(open('../SetupModulePaths.py').read());del RelativePath
        from TTSPCfromBH.BaseData import BaseData
        from TTSPCfromBH.NormCalc import Norm
    except:
        pass

class ADCData(BaseData):
    
    def __init__(self, CurrentData = None, PyTablesGroup = None, NormData = ''):
        super(ADCData, self).__init__(CurrentData, PyTablesGroup)
        
        from numpy import int16
        self.NormVersion = int16(1)
        self.Desc = "ADC Data"
        self.Norm = None
        self._DataType = 'ADCData'
        if isinstance(NormData, Norm):
            print "Setting Norm"
            self.SetNorm(NormData)
    
    def _CreateTACNormData(self):
        if self.HasNorm():
            from DataContainer.StorageArray import ChannelizedArray
            self._TACNormedData = ChannelizedArray(len(self._RawBinned),self.ChannelCount,'float64')
            from numpy import zeros
            for i in range(len(self.RouteChannelCodes)):
                CC = self._TACNormedData.Prefix +str(i+1)
                NonZero = (self.Norm.Norm()[CC] != 0)
                self._TACNormedData[CC] = zeros(len(NonZero), dtype='float64')
                self._TACNormedData[CC][NonZero] = (1.0*self._RawBinned[CC][NonZero])/(1.0*self.Norm._RawBinned[CC][NonZero])
                self._TACNormedData[CC] = (1.0*self._TACNormedData[CC])/(1.0*len(self._TACNormedData[CC]))
                try:
                    del self._Normed
                except:
                    pass
            return True
        else:
            print "No Norm Data Present"
            return False
    
    def HasNorm(self):
        if isinstance(self.Norm, Norm):
            return True
        else:
            return False
    
    def SetNorm(self, NormData):
        if isinstance(NormData,Norm):
            if self._CompareDataProperties(NormData):
                self.Norm = NormData
                self._CreateTACNormData()
                return True 
        else:
            print "NormData is not of type: Norm"
            return False
    
    def GetData(self):
        return self.Normed()
    
    def Normed(self, ForceRefresh = False):
        if ForceRefresh:
            try:
                del self._Normed
            except:
                pass 
        try:
            return self._Normed
        except:
            if self.HasNorm():
                self._Normed = self.Normalize(self._TACNormedData)
            else:
                self._Normed = self.Normalize(self.RawData())
            return self._Normed

if __name__ == '__main__':
    RelativePath = '..';exec(open('../SetupModulePaths.py').read());del RelativePath

    from Test import LoadData, LoadHighCountRateData, LoadNorm
    ImportedData = LoadData(locals(), 
                            DataVariableName ='ImportedData', 
                            PrintOutput = True,
                            ForceUpdate = True)
    
    HCRData = LoadHighCountRateData(locals(),
                       DataVariableName ='HCRData', 
                       PrintOutput = True,
                       ForceUpdate = True)

    if 4 in ImportedData.RouteChannelCodes():
        ImportedData.RemoveChannel(4)

    CurrentNorm = LoadNorm(locals(),
             ImportedData, 
             DataVariableName ='CurrentNorm',
             ForceUpdate = True
             )
    
    del ImportedData
    
    CurrentData = ADCData(HCRData, CurrentNorm)
    del HCRData
    CurrentData.SetNorm(CurrentNorm)
    print "Data has TAC Norm: " + str(CurrentData.HasNorm())

    # File Testing
    import tables
    GroupName = "Data"
    try:
        file_handle = tables.openFile("../../RESULTS/NormCalcTesting.h5",mode="r+")
        print "Opened file (r+)"
    except:
        file_handle = tables.openFile("../../RESULTS/NormCalcTesting.h5",mode="w")
        print "Opened a new file (write)"
    
    root = file_handle.root
    try:
        group = file_handle.create_group(root, GroupName)
    except tables.NodeError:
        file_handle.remove_node(root, GroupName, recursive=True)
        group = file_handle.create_group(root, GroupName)
    
    CurrentData._SaveAllLocalVars(file_handle, group, PrintOutput='Failed')
    
    file_handle.close()

    
#     from Display import ADCPlot
#     Plots = list()
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
#     
#     n = 0
#     for Plot in Plots:
#         if n != len(Plots):
#             Plot.show(block=True)
#         else:
#             Plot.show(block=False)
#         n += 1
