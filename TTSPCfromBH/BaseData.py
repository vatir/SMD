#!/usr/bin/python
'''
Created on Oct 11, 2013

@author: vatir
'''

# Use this section if direct CLI calling is desired


class BaseData(object):
	"""
	Base Data Class : NOT FOR DIRECT USE
	"""
	def __init__(self, ImportData = None, PyTablesGroup = None):
		from numpy import int16
		from tables import Group
		self.BaseDataVersion = int16(1)
		self._DataType = 'BaseData'
		if not(ImportData == None):
			self._SetupContainers(ImportData)
			self._SetupInfoTraits(ImportData)
			# Setup RawBinned Data in Case the ImportData Object is Garbage Collected
			self._BinData(ImportData)
			return None
		elif isinstance(PyTablesGroup, Group):
			self._LoadAllLocalVars(PyTablesGroup)
		
	def _SetupInfoTraits(self, ImportData):
		self.TotalCounts = ImportData.PhotonCount
		self.TotalTime = ImportData.TotalTime
		self.TimeCollected = ImportData.TimeCollected
		self.DateCollected = ImportData.DateCollected
		self.TAC_Gain = ImportData.TAC_Gain
		self.Desc = ""
		self.Filename = ImportData.Filename
		self.Folder = ImportData.Folder
		
	def _SetupContainers(self, ImportData):
		from DataContainer.StorageArray import ChannelizedArray
		from numpy import float64

		self.ADC_Intervals = ImportData.ADC_Intervals()
		self.RouteChannelCodes = ImportData.RouteChannelCodes()
		self.ChannelCount = len(self.RouteChannelCodes)
		self._RawBinned = ChannelizedArray(len(self.ADC_Intervals), self.ChannelCount, 'uint64')
		self.PhotonCount = ChannelizedArray(1, self.ChannelCount, 'uint64')
		self.ChannelDelayCont = ChannelizedArray(1, self.ChannelCount, 'float64')
		self.ChannelDelayDiscrete = ChannelizedArray(1, self.ChannelCount, 'uint64')

		if self.ChannelCount == 2:
			self.NormG = float64(1.0)
		
	def _BinData(self, ImportData):
		from numpy import bincount, array, uint32, float64, sum
		for i, CC in enumerate(self.PhotonCount.keys()):
			# Create the RawBinned Data
			self._RawBinned[CC] = array(
								bincount(
								ImportData.ADC[ImportData.Route==(self.RouteChannelCodes[i])], 
								minlength = ImportData.ADC_Bins-1),
								dtype='uint64')
			# Set Total Photons per Channel
			self.PhotonCount[CC] = sum(self._RawBinned[CC],dtype=self.PhotonCount[CC].dtype)
			self.ChannelDelayCont[CC] = float64(0.0)
			self.ChannelDelayDiscrete[CC] = uint32(0)

	def _CompareDataProperties(self, DataSet1, DataSet2 = None, CompareList = None):
		if not isinstance(DataSet2, BaseData):
			DataSet2 = self
		if not isinstance(CompareList, list):
			CompareList = [
						'TAC_Gain',
						'ChannelCount'
					   ]
		CurrentState = True
		for item in CompareList:
			if not (locals()['DataSet1'].__getattribute__(item) == locals()['DataSet2'].__getattribute__(item)):
				print item + " : Does Not Match!!!"
				CurrentState = False
		return CurrentState
		
	def RawData(self):
		return self._RawBinned.Copy
	
	def Normalize(self, RawData):
		from DataContainer.StorageArray import ChannelizedArray
		Normed = ChannelizedArray(len(self._RawBinned), self.ChannelCount, 'float64')
		for CC in RawData.keys():
			# Create Normalized TAC Normalization
			from numpy import array
			Normed[CC] = array(1.0*RawData[CC]/(1.0*sum(RawData[CC])),dtype='float64')
		return Normed.Copy
	
	def ClearOutliers(self, DataSet, StdCutoff, Contiguous):
			from numpy import float64
			for CC in DataSet.keys():

				NormOutlierIndices = self.OutlierIndices(DataSet[CC], 
														 StdCutoff=StdCutoff, 
														 Contiguous=Contiguous)
				DataSet[CC][NormOutlierIndices] = float64(0.0)
			return self.Normalize(DataSet)
		
	def OutlierIndices (self, DataSet, StdCutoff, Contiguous):
		from numpy import abs, mean, std, ones, argmax, argmin, zeros
		Deviants = abs((DataSet - mean(DataSet[DataSet != 0]))) > StdCutoff*std(DataSet[DataSet != 0])
		if not Contiguous:
			if (Deviants == True).all():
				return zeros(len(DataSet), dtype='bool')
			return Deviants
		FirstIndex = argmin(Deviants)
		LastIndex = argmax(Deviants[FirstIndex:])
		Deviants = ones(len(Deviants),dtype='bool')
		Deviants[FirstIndex:LastIndex] = False
		if (Deviants == True).all():
			return zeros(len(DataSet), dtype='bool')
		return Deviants

	def _SaveAllLocalVars(self, Filehandle, Group, PrintOutput = 'Failed'):
		"""
		PrintOutput: All, Failed, False
		"""
		from DataContainer.StorageArray import ChannelizedArray
		from numpy import ndarray, array
		self._DataType
		for var in vars(self):
			if PrintOutput=='All': print "\n" + str(var) + " : " + str(type(vars(locals()['self'])[var]))
			if str(var) == 'Norm':
				continue
			try:
				if isinstance(vars(locals()['self'])[var], (ndarray,list)):
					if PrintOutput=='All': print "Trying to save: " + str(var) + " : As a ndarray"
					Filehandle.create_array(Group, var, obj=vars(locals()['self'])[var], title='')
					Group._f_get_child(var).set_attr('VarType','ndarray')
					
				elif isinstance(vars(locals()['self'])[var], ChannelizedArray):
					try:
						CurrentVar = vars(locals()['self'])[var]
						if PrintOutput=='All': print "Trying to save: " + str(var) + " : As a ChannelizedArray"
						if PrintOutput=='All': print CurrentVar._Data
						if PrintOutput=='All': print CurrentVar
						try:
							CurrentLength = len(CurrentVar)
						except:
							CurrentLength = 1
						if PrintOutput=='All': print "Expected Length: " + str(CurrentLength)
						Filehandle.create_table(Group, var, filters=None, expectedrows=CurrentLength, description=CurrentVar._Data)
						Group._f_get_child(var).set_attr('VarType','ChannelizedArray')
						del CurrentLength
						del CurrentVar
					except:
						import sys
						e = sys.exc_info()
						print e
					
				else:
					if PrintOutput=='All': print "Trying to save: " + str(var) + " : As a Scalar"
					Filehandle.create_array(Group, var, obj=array(vars(locals()['self'])[var]), title='')
					Group._f_get_child(var).set_attr('VarType','ndarray')
					
			except:
				if (PrintOutput=='All') or (PrintOutput=='Failed'): print "Failed to save: " + str(var)
				
		Filehandle.flush()
		return True

	def _LoadAllLocalVars(self, Group, PrintOutput = 'Failed'):
		"""
		PrintOutput: All, Failed, False
		"""
		from DataContainer.StorageArray import ChannelizedArray
		from numpy import ndarray, copy
		for var in Group:
			if PrintOutput=='All': print "\n" + str(var.name) + " : " + str(var.ndim)
			if PrintOutput=='All': print "" + str(var.name) + " : " + str(var.flavor)
			if PrintOutput=='All': print "" + str(var.name) + " : " + str(var.shape)
			if PrintOutput=='All': print "" + str(var.name) + " : " + str(len(var))
			if PrintOutput=='All': print "" + str(var.name) + " : " + str(var.get_attr('VarType'))
			if PrintOutput=='All': print "" + str(var.name) + " : " + str(var.dtype)
			
			try:
				if var.get_attr('VarType') == 'ndarray':
					vars(locals()['self'])[var.name] = var.read()
					
					
				elif var.get_attr('VarType') == 'ChannelizedArray':
					vars(locals()['self'])[var.name] = ChannelizedArray(len(var), ChannelCount = len(var.colnames), NumpyDataType = var.dtype[0])
					vars(locals()['self'])[var.name]._Data = var.read()
					vars(locals()['self'])[var.name]._SetItems()
			except:
				if PrintOutput=='Failed': print 'Failed to load: ' + str(var.name)
				
#			try:
#				if isinstance(vars(locals()['self'])[var], (ndarray,list)):
#					if PrintOutput=='All': print "Trying to save: " + str(var) + " : As a ndarray"
#					Filehandle.create_array(Group, var, obj=vars(locals()['self'])[var], title='')
#					
#				elif isinstance(vars(locals()['self'])[var], ChannelizedArray):
#					try:
#						CurrentVar = vars(locals()['self'])[var]
#						if PrintOutput=='All': print "Trying to save: " + str(var) + " : As a ChannelizedArray"
#						if PrintOutput=='All': print CurrentVar._Data
#						if PrintOutput=='All': print CurrentVar
#						try:
#							CurrentLength = len(CurrentVar)
#						except:
#							CurrentLength = 1
#						if PrintOutput=='All': print "Expected Length: " + str(CurrentLength)
#						Filehandle.create_table(Group, var, filters=None, expectedrows=CurrentLength, description=CurrentVar._Data)
#						del CurrentLength
#						del CurrentVar
#					except:
#						import sys
#						e = sys.exc_info()
#						print e
#					
#				else:
#					if PrintOutput=='All': print "Trying to save: " + str(var) + " : As a Scalar"
#					Filehandle.create_array(Group, var, obj=vars(locals()['self'])[var], title='')
#					
#			except:
#				if (PrintOutput=='All') or (PrintOutput=='Failed'): print "Failed to save: " + str(var)
#				
#		Filehandle.flush()
		return True

if __name__ == '__main__':
	# Setup Testing Environment
	RelativePath = '..';exec(open('../SetupModulePaths.py').read());del RelativePath
	
	from Test import LoadData
	ImportedData = LoadData(locals(),
						DataVariableName ='ImportedData', 
						PrintOutput = True,
						ForceUpdate = False)
	if 4 in ImportedData.RouteChannelCodes():
		ImportedData.RemoveChannel(4)
	
	# Run Tests
	Data = BaseData(ImportedData)
	print Data.RouteChannelCodes
	from numpy import sum
	print sum(Data.Normalize(Data._RawBinned).values())
	
	print "Test: Completed"
	