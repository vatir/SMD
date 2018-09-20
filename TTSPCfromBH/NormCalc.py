#!/usr/bin/python
'''
Created on Oct 8, 2013

@author: vatir
'''

# Use this section if direct CLI calling is desired

try:
    from TTSPCfromBH.BaseData import BaseData
except:
    try:
        RelativePath = '..';exec(open('../SetupModulePaths.py').read());del RelativePath
        from TTSPCfromBH.BaseData import BaseData
    except:
        pass

class Norm(BaseData):
    
    def __init__(self, NormData = None, PyTablesGroup = None):
        super(Norm, self).__init__(NormData, PyTablesGroup)
        
        from numpy import int16
        self.NormVersion = int16(1)
        self.Desc = "Room Light Data for TAC non-uniformity correction"
        self._DataType = 'Norm' 
    
    def CurrentNorm(self):
        return self.Norm()
    
    def _ShowLocals(self):
        return locals()

    def Norm(self, ForceRefresh = False):
        if ForceRefresh:
            try:
                del self._Norm
            except:
                pass 
        try:
            return self._Norm
        except:
            self._Norm = self.Normalize(self.RawData())
            return self._Norm.Copy
        
    def RawCleaned(self, StdCutoff = 1.5, Contiguous = False, ForceRefresh = True):
        """
        This uses the same indices for removal of outliers as the normalized version.
        
        Note: StdCutoff and Contiguous will not take effect if this has
        already been called, but ForceRefresh is not set to True.
        """
        if ForceRefresh: 
            try:
                del self._RawCleaned
            except:
                pass 
        try:
            return self._RawCleaned
        except:
            from numpy import uint64
            self._RawCleaned = self._RawBinned.Copy
            for CC in self._RawBinned.keys():
                NormOutlierIndices = self.OutlierIndices(self.Norm()[CC],
                                                         StdCutoff=StdCutoff, 
                                                         Contiguous=Contiguous)
                self._RawCleaned[CC][NormOutlierIndices] = uint64(0)
            return self._RawCleaned.Copy

    def NormCleaned(self, StdCutoff = 1.5, Contiguous = False, ForceRefresh = False):
        """
        Note: StdCutoff and Contiguous will not take effect if this has
        already been called, but ForceRefresh is not set to True.
        """
        if ForceRefresh: 
            try:
                del self._CleanedNorm
            except:
                pass 
        try:
            return self._CleanedNorm
        except:
            self._CleanedNorm =     self.ClearOutliers(
                                        self.Norm(),
                                        StdCutoff,
                                        Contiguous
                                        )
            return self._CleanedNorm.Copy
    
if __name__ == '__main__':
    # Setup Testing Environment
    RelativePath = '..';exec(open('../SetupModulePaths.py').read());del RelativePath
    

    from Test import LoadData
    ImportedData = LoadData(locals(), 
                            DataVariableName ='ImportedData', 
                            PrintOutput = True,
                            ForceUpdate = False)

    if 4 in ImportedData.RouteChannelCodes():
        print "Removed Channel 4"
        ImportedData.RemoveChannel(4)
    # Run Tests
    TestNorm = Norm(ImportedData)
#     print TestNorm.RawData()
#     print TestNorm.RawCleaned()
    print sum(sum(TestNorm.RawData().values()))
    print sum(sum(TestNorm.RawCleaned().values()))
    print sum(sum(TestNorm.RawData().values()))
    print TestNorm.RawData()
    print sum(sum(TestNorm.Norm().values()))
    print sum(sum(TestNorm.NormCleaned().values()))
    print "Test: Completed"
    
    # File Testing
    import tables
    GroupName = "Norm"
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
    
    TestNorm._SaveAllLocalVars(file_handle, group, PrintOutput='Failed')
    
    file_handle.close()
