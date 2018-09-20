#!/usr/bin/python
'''
Created on Sep 26, 2013

@author: vatir
'''

import tables
from _abcoll import Iterable
CurrentCompressionLevel = tables.Filters(complib="lzo", complevel=1, shuffle=True)

class HDF5DataFormat(object):
    '''
    Custom Structure for Numpy Arrays to be used in the HDF5 format.
    '''
    def __init__(self, Data=False, NumpyDataType=False):
        from numpy import iterable, array, dtype
        if iterable(Data):
            isdata = True
        else:
            isdata=False
            
        if (isdata==False and NumpyDataType==False):
            self.MainData = array([],dtype='float64')
            return None
        elif(NumpyDataType==False):
            self.MainData = array(Data)
            return None
        elif(isdata==False):
            self.MainData = array([],dtype=dtype(NumpyDataType))
            return None
        else:
            self.MainData = array(Data,dtype=dtype(NumpyDataType))
            return None
    def __str__(self):
        return str(self.MainData)
 
    def __repr__(self):
        return str(self.MainData)

    def WriteArray(self, Filehandle, Group, Name, Title = ''):
        '''
        Writes the MainData array to a Array in FileHandle at Group.
        '''
        try:
            Filehandle.create_array(Group, Name, obj=self.MainData, title=Title)
            Filehandle.flush()
            return True
        except:
            print "WriteArray failed: " + str(Group) + " : " + str(Name)
            return False
    
    def WriteTable(self, Filehandle, Group, Name, ColName = 'Col1', Filters=None):
        '''
        Writes the MainData array to a Table in FileHandle at Group.
        '''
        try:
            from numpy import array
            RecArrayDataType = array(self.MainData, dtype={'names':[ColName,],'formats':[self.MainData.dtype,]})
            Filehandle.create_table(Group, Name, filters=Filters, expectedrows=len(self.MainData), description=RecArrayDataType)
            Filehandle.flush()
            return True
        except:
            print "WriteTable failed: " + str(Group) + " : " + str(Name)
            return False
    
    def WriteTableCompressed(self, Filehandle, Group, Name, ColName = 'Col1'):
        '''
        Calls WriteTable with the CurrentCompressionLevel.
        '''
        return self.WriteTable(Filehandle, Group, Name, ColName = 'Col1', Filters = CurrentCompressionLevel)

# from collections import OrderedDict
# 
# 
# def ChannelizedArray(ChannelCount = 2, NumpyDataType = 'uint64', Prefix = 'Channel_'):
#     from numpy import array
#     Prefix = "Channel_"
#     DataType = [(Prefix+str(i+1),NumpyDataType)for i in range(ChannelCount)]
#     NewArray = array([],dtype=DataType)
#     NewArray._Prefix = Prefix
#     return NewArray, Prefix

#class ChannelizedArray(OrderedDict):
#    '''
#    Helper class to hold array's for data with unknown numbers of channels.
#    
#    ChannelizedArray(ChannelCount = 2, NumpyDataType = 'uint64')
#    
#    Subclass of (OrderedDict)
#    ''' 
#    
#    def __init__(self, ChannelCount = 2, NumpyDataType = 'uint64'):
#        super(ChannelizedArray, self).__init__()
#        from numpy import array
#        self._Prefix = "Channel_"
#        self._NPDataType = [(self._Prefix+str(i+1),NumpyDataType)for i in range(ChannelCount)]
#        self._Data = array([],self._NPDataType)
#
#        for x in range(ChannelCount):
#            key = self._Prefix + str(x+1)
#            self[key] = self._Data[key].view()
#        return None
#    
#    @property
#    def Prefix(self):
#        return self._Prefix
#    
#    @property
#    def DictDescription(self):
#        return self._Data.dtype
#        
#    @property
#    def NumpyDtype(self):
#        from numpy import array
#        Desc = list()
#        for key, value in self.items():
#            try:
#                Desc.append((key, value.dtype))
#            except:
#                Desc.append((key, array(value).dtype))
#        return Desc
#    
#    @property
#    def NDArrayView(self):
#        return self._Data
#    
#    @property
#    def Copy(self):
#        NewCopy = ChannelizedArray(ChannelCount = len(self.keys()))
#        for key,data in self.items():
#            NewCopy[key]=data.copy()
#        return NewCopy
        
class ChannelizedArray(object):
    '''
    Helper class to hold array's for data with unknown numbers of channels.
    '''

    def __init__(self, Length, ChannelCount = 2, NumpyDataType = 'uint64'):
        from numpy import zeros
        self._Prefix = "Channel_" # Should be phased out (Use keys instead)
        self._Length = Length
        self._NumpyDataType = NumpyDataType
        self._NPDataType = [(self._Prefix+str(i+1),NumpyDataType)for i in range(ChannelCount)]
        self._Data = zeros(Length, dtype=self._NPDataType)
        self._ChannelCount = ChannelCount
        
        self._SetItems()
            
        return None
    
    def _SetItems(self):
        from numpy import arange
        from numpy.lib.stride_tricks import as_strided
        self._values = []
        shape = self._Data.shape
        TempData = self._Data.view(dtype=self._NumpyDataType)
        stride = self._Data.strides
        for x in (arange(self._ChannelCount)+1):
            self._values.append(as_strided(TempData[x-1:], shape, stride))
        self.UpdateKeys()
        
    def UpdateKeys(self):
        self._keys = [k[0] for k in self.NumpyDtype]
        
    def __getitem__(self, value):
        return self._Data[value]

    def __setitem__(self, item, value):
        from numpy import can_cast
        if not(can_cast(value.dtype,self._Data[item].dtype)): raise TypeError
        from collections import Iterable as CheckIterable
        if isinstance(value,CheckIterable):
            if (len(value)==self._Length):
                self._Data[item] = value
                return True
        elif self._Length == 1:
            self._Data[item] = value
            return True
        print "Length of value does not match array"
        
    def __len__(self):
        return self._Length
        
    @property
    def shape(self):
        return self._Data.shape
        
    @property
    def ChannelCount(self):
        return self._ChannelCount

    def items(self):
        return [(key, value) for key,value in zip(self._keys,self._values)]
    
    def values(self):
        from numpy import array
        return array(self._values)
        
    def keys(self):
        return self._keys
        
    def DictDescription(self):
        from numpy import array
        Desc = dict()
        Desc['names']=list()
        Desc['formats']=list()
        for key, value in self.items():
            Desc['names'].append(key)
            try:
                Desc['formats'].append(value.dtype)
            except:
                Desc['formats'].append(array(value).dtype)
        return Desc
    
#     def AsRecArray(self):
#         from numpy import recarray
#         return self._Data.astype(recarray, dtype=self.NumpyDtype)
    
    def ViewAsType(self, Dtype):
        NewCopy = ChannelizedArray(self._Length, self._ChannelCount, Dtype)
        from numpy import array
        for Index in self.keys():
            NewCopy[Index] = array(self._Data[Index],copy=True,dtype=Dtype)
        NewCopy._SetItems()
        return NewCopy
        
    def ChangeColName(self, Orig, New):
        OrigDtype = self._NPDataType
        try:
            for i, key in enumerate(self.NumpyDtype):
                if key[0] == Orig:
                    self._NPDataType[i] = (New,key[1])
            self.UpdateKeys()
            self._Data = self._Data.view(dtype=self._NPDataType)
        except Exception, e:
            print "Error: %s" % str(e)
            self._NPDataType = OrigDtype
                
    def DeleteCol(self, Col):
        NewCopy = ChannelizedArray(self._Length, self._ChannelCount-1, self._NumpyDataType)
        for i, key in enumerate(NewCopy.keys()):
            NewCopy.ChangeColName(NewCopy.Prefix + str(i+1), str(i))
        try:
            i = 0
            for key in self.keys():
                if key == Col:
                    continue
                NewCopy.ChangeColName(str(i), str(key))
                NewCopy._Data[str(key)] = self._Data[str(key)].copy()
                i += 1
            NewCopy._SetItems()
            return NewCopy.Copy
        except Exception, e:
            print "Error: %s" % str(e)
    
    def AddCol(self, Name = None):
        NewCopy = ChannelizedArray(self._Length, self._ChannelCount+1, self._NumpyDataType)
        for i, key in enumerate(NewCopy.keys()):
            NewCopy.ChangeColName(NewCopy.Prefix + str(i+1), str(i))
        try:
            i = 0
            for key in self.keys():
                NewCopy.ChangeColName(str(i), str(key))
                NewCopy._Data[str(key)] = self._Data[str(key)].copy()
                i += 1
            NewCopy._SetItems()
            if Name != None:
                NewCopy.ChangeColName(str(i), Name)
            return NewCopy.Copy
        except Exception, e:
            print "Error: %s" % str(e)

    @property
    def dtype(self):
        return self._NumpyDataType

    @property
    def NumpyDtype(self):
        return self._NPDataType
    
    @property
    def Prefix(self):
        return self._Prefix

    @property
    def Copy(self):
        NewCopy = ChannelizedArray(self._Length, self._ChannelCount, self._NumpyDataType)
        NewCopy._Data = self._Data.copy()

        # Set to alternate values to avoid overlaps then set to correct values: There must be a better way to do this
        for i, key in enumerate(NewCopy.keys()):
            NewCopy.ChangeColName(NewCopy.Prefix + str(i+1), str(i))
        for i, key in enumerate(self.keys()):
            NewCopy.ChangeColName(str(i), key)

        NewCopy._SetItems()
        return NewCopy

class NormFileStruct(object):
    '''
    Custom Structure for HDF5
    '''
    
    def __init__(self, Length, ChannelCount = 2):
        from numpy import float64, int64
        self.RawNorm = ChannelizedArray(Length, ChannelCount, 'uint64')
        self.Norm = ChannelizedArray(Length, ChannelCount, 'float64')
        self.PhotonCount = ChannelizedArray(1, ChannelCount, 'uint64')
        # This will be for the later version that holds measurement data
        #self.ChannelCableDelay = ChannelizedArray(ChannelCount, 'float64')
        
        if ChannelCount == 2:
            self.NormG = float64(1.0)
        
        self.CollectionLengthCounts = int64(0)
        self.CollectionLengthTime = float64(1.0)
        
        self.DateCollected = ""
        self.FileDate = ""
        self.Desc = ""
        
        self.Filename = ""
        self.Folder = ""
    
if __name__ == '__main__':
    RelativePath = '..';exec(open('../SetupModulePaths.py').read());del RelativePath

    temp = NormFileStruct(4095)
    
    from numpy import arange
    temp = HDF5DataFormat(arange(10000))
    
    
    try:
        file_handle = tables.openFile("../../RESULTS/StorageArrayTesting.h5",mode="r+")
        print "Opened file (r+)"
    except:
        file_handle = tables.openFile("../../RESULTS/StorageArrayTesting.h5",mode="w")
        print "Opened a new file (write)"
    
    root = file_handle.root
    try:
        group = file_handle.create_group(root, "CompressedData")
    except tables.NodeError:
        file_handle.remove_node(root, "CompressedData", recursive=True)
        group = file_handle.create_group(root, "CompressedData")
    
    print temp.WriteArray(file_handle, group, 'TestingUncompArray')
    print temp.WriteTableCompressed(file_handle, group, 'TestingUncompTable', ColName = 'T')
    
    file_handle.close()


#     import os
#       
#     try:
#         os.unlink("testing.h5")
#     except:
#         pass
#       
#     try:
#         file_handle = tables.openFile("testing.h5",mode="r+")
#         print "Opened file (r+)"
#     except:
#         file_handle = tables.openFile("testing.h5",mode="w")
#         print "Opened a new file (write)"
#       
#     root = file_handle.root
#     try:
#         group = file_handle.create_group(root, "CompressedData")
#     except tables.NodeError:
#         file_handle.remove_node(root, "CompressedData", recursive=True)
#         group = file_handle.create_group(root, "CompressedData")
#       
#     _filter = tables.Filters(complib="lzo", complevel=1, shuffle=True)
#   
#     data = np.arange(10000)
#     temp = np.array(data,dtype={'names':['col1',],'formats':[data.dtype,]})
#       
#     try:
#         file_handle.create_table(group, 'MT', filters=_filter, expectedrows=len(data), description=temp)
#     except tables.NodeError:
#         file_handle.remove_node(group, 'MT')
#         file_handle.create_table(group, 'MT', filters=_filter, expectedrows=len(data), description=temp)
#     print temp
#       
#     file_handle.close()
#     del file_handle
#       
#     os.unlink("testing.h5")
#
