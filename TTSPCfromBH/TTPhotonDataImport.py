#!/usr/bin/python
'''
Created on Oct 3, 2013

@author: vatir
'''

# Imports needed for entire file.

def ConvertRelativePath(Folder):
    '''
    Converts a path relative to SMD/DATA to abs path.
    '''
    from os import path
    from re import search
    import sys, os, os.path, inspect
    if '__file__' not in locals():
        __file__ = inspect.getframeinfo(inspect.currentframe())[0]

    CurPath = os.path.abspath(__file__)
    
    #CurPath = path.abspath('.')
    while path.split(CurPath)[1].lower() != 'smd':
        CurPath = path.split(CurPath)[0]
        Path = path.split(CurPath)[0]
        if path.split(CurPath)[1]=='':
            break
    else:
        Path = path.split(CurPath)[0]
    
    Path = os.path.join(Path, 'SMD')
    Path = os.path.join(Path, 'DATA')
    return os.path.join(Path, Folder+'\\')
    #DirPrefixSearch = search('^(.*)\\SMD.*$',CurPath)
    #if DirPrefixSearch != None:
    #    DirPrefix = DirPrefixSearch.group(1)
    #else:
    #    DirPrefix = ''
    #return str(DirPrefix) + "\\SMD\\DATA\\" + str(Folder) + "\\"

class Data(object):
    
    def __init__(self, Folder, Filename, PrintStats = False):
        from numpy import int16
        self.Version = int16(1)

        self.Import(Folder, Filename, PrintStats)
        self.RouteChannelCodes()
        return None
    
    def Import(self, Folder, Filename, PrintStats = False):
        import numpy as np
        from os import path
        '''
        Import BH Time Tagged Data
        Folder: Relative to the DATA directory
        Filename: Filename without extension
        '''

        Folder = ConvertRelativePath(Folder)
        Folder = Folder.replace('/','\\')
        '''
        Kept Variables
        ImportTime : std time output : Timestamp from when import was completed for checking when data was imported
        TimeSpentOnImport : seconds : Total time spent importing
        ADC_Intervals : float : Center of ADC time bins
        MicroTime : float : (macro time clock in ns) file value has already been converted from 0.1 ns increments, e.g., 500 = 50 ns
        SyncTime : float: self.MicroTime converted to seconds
        TAC_Range : Manually set from looking at data .set file. Use for dynamic lookup.
        TAC_Gain : Manually set from looking at data .set file. Use for dynamic lookup.
        ADC_Bins : Number of bins in the ADC: Manually set from looking at data .set file. Use for dynamic lookup.
        DateCollected : str : Date the data was collected
        TimeCollected : str : Time of day the data was collected (clock may not have been set correctly use only for relative measurments.)


        Route : Route code for each photon in order of arrival
        MT : Photon Macro Times in order of arrival in ns (macro defined as total time since first photon arrived, all channels are considered for this number)
        ADC : Photon Micro Times in order of arrival in ns
        
        Error Lists: (Should be small or empty)
        MarkPhotons : Index Location of entries labeled as Marks
        GapPhotons : Index Location of entries with labeled with the Gap Flag
        InvalidPhotons : Index Location of entries with labeled with the Invalid Flag
        '''
        
        from time import time 
        StartTime = time()
        if PrintStats:
            CurrentTime = time()
            print "-------------------------"
            print "Files Imported:"
            
        """
        File Import:
        """
        
        RawTiming32bit = np.array([],dtype='uint32')
        n = 0
        while path.exists(Folder + Filename+"_"+str(n).rjust(3,'0')+".spc"):
            with open(Folder + Filename +"_"+str(n).rjust(3,'0')+".spc", 'rb') as input_file_handle:
                if len(RawTiming32bit) == 0:
                    if PrintStats:
                        print "File Imported:" + Folder + Filename+"_"+str(n).rjust(3,'0')+".spc"
                    RawTiming32bit = np.array(np.fromfile(input_file_handle, dtype=np.dtype('<u4'), count = -1))
                else:
                    if PrintStats:
                        print "File Imported:" + Folder + Filename+"_"+str(n).rjust(3,'0')+".spc"
                    # Skips the first data entry as the macro time should not change and the odd first record is not handled
                    #RawTiming32bit=np.hstack((RawTiming32bit, np.array(np.fromfile(input_file_handle, dtype=np.dtype('<u4'), count = -1))[1:]))
                    RawTiming32bit=np.r_[RawTiming32bit, np.array(np.fromfile(input_file_handle, dtype=np.dtype('<u4'), count = -1))[1:]]
                    
                    #RawTiming32bit=np.array(np.fromfile(input_file_handle, dtype=np.dtype('uint32'), count = -1))[1:]
            n = n + 1

        # Get system parameters
        with open(Folder + Filename+"_"+str(n-1).rjust(3,'0')+".set", 'rb') as input_file_handle:
            if PrintStats:
                print "File Imported:" + Folder + Filename+"_"+str(n).rjust(3,'0')+".set"
            for line in input_file_handle:
                if line[7:15] == "SP_TAC_G": 
                    self.TAC_Gain = int(line[18])
                elif line[7:15] == "SP_TAC_R": 
                    self.TAC_Range = float(line[18:31]) * 10.0**9.0
                elif line[7:16] == "SP_ADC_RE": 
                    self.ADC_Bins = int(line[19:23])
                elif "Date" in line:
                    self.DateCollected = line[14:24]
                elif "Time" in line:
                    self.TimeCollected = line[14:22]
                    
        self.Filename = Filename
        self.Folder = Folder
        
        
        if PrintStats:
            print "-------------------------"
            print "TAC Gain:       " + str(self.TAC_Gain)
            print "TAC Range:      " + str(self.TAC_Range)
            print "ADC Bins:       " + str(self.ADC_Bins)
            print "Date Collected: " + str(self.DateCollected)
            print "Time Collected: " + str(self.TimeCollected)
            
        
        if PrintStats:
            print "-------------------------"
            print "Files Imported(Timing): " + str(time() - CurrentTime)
            CurrentTime = time()
    
        """
        Parse Imported Data:
        """
        
        # Get self.MicroTime from the first frame:
        self.MicroTime = (RawTiming32bit[0] & 0x00ffffff)/10.0
        RawTiming32bit = RawTiming32bit[1:]
        
        self.SyncTime = self.MicroTime*10.0**-9.0
        
        # Remove Invalid and Gap Entries and Store
        self.MarkPhotons = RawTiming32bit[RawTiming32bit&0x10000000==0x10000000]
        RawTiming32bit = RawTiming32bit[RawTiming32bit&0x20000000!=0x20000000]
        self.GapPhotons = RawTiming32bit[RawTiming32bit&0x20000000==0x20000000]
        RawTiming32bit = RawTiming32bit[RawTiming32bit&0x20000000!=0x20000000]
        self.InvalidPhotons = RawTiming32bit[RawTiming32bit&0xc0000000==0x80000000]
        RawTiming32bit = RawTiming32bit[RawTiming32bit&0xc0000000!=0x80000000]
        
        PhotonIndices = ((RawTiming32bit&0xc0000000)!=0xc0000000)
        self.PhotonCount = len(PhotonIndices[PhotonIndices])
        RawLength = len(RawTiming32bit)
        
        SmallMT = np.zeros(RawLength,dtype='uint16')
        MTOverflows = np.zeros(RawLength,dtype='uint64')
    
        MTOverflows[np.invert(PhotonIndices)] += 4096*RawTiming32bit[np.invert(PhotonIndices)]&0xfffffff
    
        SmallMT[PhotonIndices] = np.array(((RawTiming32bit[PhotonIndices])&0xfff),dtype='uint16')
        
        MTOverflows[((PhotonIndices) & ((RawTiming32bit&0x40000000)==0x40000000))] += 4096
        
        self.Route = np.array((1+(RawTiming32bit[PhotonIndices]&0xf000)%(0xf)),dtype='uint8')
        
        self.MT = SmallMT + (np.cumsum(MTOverflows))
        self.MT = self.MT[PhotonIndices]
        
        self.ADC = np.array(((self.ADC_Bins - 1)-((RawTiming32bit[PhotonIndices]&0x0fff0000)>>16)),dtype='uint16')
        
        self.TotalTime = self.MT[-1]*self.SyncTime
        
        if PrintStats:
            print "-------------------------"
            print "Total Photons:\t" + str(self.PhotonCount)
            print "Total Time:\t" + str(self.TotalTime)
            print "Count Rate:\t" + str(self.PhotonCount/((self.MT[-1])*self.SyncTime))
            print "-------------------------"
            print "Error Types"
            print "Gap Photons:     " + str(len(self.GapPhotons))
            print "Invalid Photons: " + str(len(self.InvalidPhotons))
            print "Mark Entries:    " + str(len(self.MarkPhotons))
            print "-------------------------"
            print "Import (Timing): " + str(str(time() - CurrentTime))
            print "-------------------------"
            print "Total Time: " + str(time() - StartTime)
            print "-------------------------"
            
        # Cleanup check
        del RawTiming32bit
        
        self.TimeSpentOnImport = time() - StartTime
        self.ImportTime = time()
        return True
        
    def ADC_Intervals(self, ForceRefresh = False):
        if ForceRefresh: 
            try:
                del self._ADCI
            except:
                pass 
        try:
            return self._ADCI
        except:            
            from numpy import arange
            # self.ADC_Intervals: time of the center of each ADC bin
            self._ADCI = arange(self.TAC_Range/(2.0*self.ADC_Bins*self.TAC_Gain),self.TAC_Range*(1.0-1.0/(2.0*self.ADC_Bins))/self.TAC_Gain,self.TAC_Range/(self.ADC_Bins*self.TAC_Gain))
            return self._ADCI
    
    def MT_in_ns(self):
        return self.MicroTime*self.MT

    def ADC_in_ns(self):
        return self.ADC*self.TAC_Range/(self.ADC_Bins*self.TAC_Gain)
    
    def RouteChannelCodes(self, ForceRefresh=False):
        if ForceRefresh: 
            try:
                del self._RCC
            except:
                pass 
        try:
            return self._RCC
        except:
            from numpy import unique
            CC = unique(self.Route)
            self._RCC = sorted(CC)
            return self._RCC
    
    def TimeCode(self):
        return None
    
    def RemoveChannel(self, ChannelCode):
        if ChannelCode in self.RouteChannelCodes():
            try:
                ToKeep = self.Route != ChannelCode
                self.ADC = self.ADC[ToKeep]
                self.MT = self.MT[ToKeep]
                self.Route = self.Route[ToKeep]
                self.PhotonCount = len(self.Route)
                try:
                    while True:
                        del self._RCC
                except:
                    pass
                return True
            except:
                return False
        else:
            return False
    
    def HighestCountRateChannel(self, ForceRefresh=False):
        try:
            if ForceRefresh or not (self._HCRC in self.RouteChannelCodes()): 
                del self._LCRC
        except:
            pass 
        try:
            return self._HCRC
        except:
            ChannelCode = None
            Count = None
            for RouteCode in self.RouteChannelCodes():
                CurrentCount = len(self.Route[self.Route == RouteCode])
                if CurrentCount > Count:
                    Count = CurrentCount
                    ChannelCode = RouteCode
            self._HCRC = ChannelCode
            return self._HCRC
            
    def LowestCountRateChannel(self, ForceRefresh=False):
        try:
            if ForceRefresh or not (self._LCRC in self.RouteChannelCodes()): 
                del self._LCRC
        except:
            pass 
        try:
            return self._LCRC
        except:
            from numpy import inf
            ChannelCode = None
            Count = inf
            for RouteCode in self.RouteChannelCodes():
                CurrentCount = len(self.Route[self.Route == RouteCode])
                if CurrentCount < Count:
                    Count = CurrentCount
                    ChannelCode = RouteCode
            self._LCRC = ChannelCode
            return self._LCRC
            
if __name__ == '__main__':
    exec(open('SetupModulePaths.py').read())
    #RelativePath = '..';exec(open('../SetupModulePaths.py').read());del RelativePath
    from Test import LoadData
    ImportedData = LoadData(locals(), 
                            DataVariableName ='ImportedData', 
                            PrintOutput = True,
                            ForceUpdate = True)
    print ImportedData.RouteChannelCodes()
    print ImportedData.HighestCountRateChannel()
    print ImportedData.LowestCountRateChannel()
    print "Test: Completed"
    