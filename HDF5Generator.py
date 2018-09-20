#!/usr/bin/python
'''
Created on Sep 26, 2013

@author: vatir
'''

if __name__ == '__main__':
    import numpy as np
    import DataContainer.StorageArray as sa
    import DataContainer.HDF5FileTools as ft
    
    temp = sa.HDF5DataFormat(np.arange(10000),'complex128')
    
    FileHandle = ft.FileOpen("../RESULTS/HDF5GeneratorTesting.h5")
    
    root = FileHandle.root
    
    group =  ft.NodeCreate(FileHandle, FileHandle.root, "CompressedData")
    
    print temp.WriteArray(FileHandle, group, 'TestingUncompArray', Title='Hello')
    print temp.WriteTable(FileHandle, group, 'TestingUncompTable', ColName = 'T')
    
    FileHandle.close()
    
    from TTSPCfromBH.TTPhotonDataImport import Data
    ImportedData = Data("2013/09/01", "exp 2 room light", True)
    from TTSPCfromBH.NormCalc import Norm
    Norm(ImportedData)
    
    
#    print "DataContainer output:"
#     from DataContainer.StorageArray import FileStruct
#     temp = FileStruct()