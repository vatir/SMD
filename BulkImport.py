#!/usr/bin/python
'''
Created on Oct 24, 2013

@author: vatir
'''

def Draw(Data, Name):
	from Display import ADCPlot
	ADCPlot(Data.ADC_Intervals, 
			Data.RawData(),
			Title="Raw Data", 
			YAxis="Intensity (Counts)").savefig(Name, dpi=300)
	
def CreateGroup(FileHandle, GroupName):
	try:
		group = file_handle.create_group('/', GroupName)
	except tables.NodeError:
		file_handle.remove_node('/', GroupName, recursive=True)
		group = file_handle.create_group('/', GroupName)
	return group

if __name__ == '__main__':
	from re import search 
	Traits = list() # Filename, Folder, DataType, ImageCreate
	
	with open('../DataList.csv') as file_handle:
		for line in file_handle:
			DataList = line[:-1].split("\t")
			if DataList[2] == '1':
				TempEntry = dict()
				TempEntry['Filename'] = DataList[0]
				Result = search('^\.\./DATA/(.*)$',DataList[1])
				TempEntry['Foldername'] = Result.group(1)
				if DataList[4] == 'Norm':
					TempEntry['DataType'] = 'Norm'
				else:
					TempEntry['DataType'] = 'Data'
				if DataList[7] == '1':
					TempEntry['Draw'] = True
				else:
					TempEntry['Draw'] = False
				Traits.append(TempEntry)

	import tables
	try:
		file_handle = tables.openFile("../RESULTS/Data.h5",mode="r+")
		print "Opened file (r+)"
	except:
		file_handle = tables.openFile("../RESULTS/Data.h5",mode="w")
		print "Opened a new file (write)"
	from warnings import filterwarnings
	filterwarnings('ignore', category=tables.NaturalNameWarning)
	from time import time
	from TTSPCfromBH.DataCalc import ADCData
	from TTSPCfromBH.NormCalc import Norm
	from TTSPCfromBH.TTPhotonDataImport import Data
	ImageLocation = '../RESULTS/Images/'
	StartTime = time()
	CurrentTime = time()
	print "-------------------------"
	for i, TraitSet in enumerate(Traits):
		Select = False
		if (i == 100) or not Select:
			CurrentTime = time()
			print "Starting: {0} : {1} : {2}".format(i, TraitSet['Foldername'], TraitSet['Filename'])
			try:
				if TraitSet['DataType'] == 'Data':
					TempData = ADCData(Data(TraitSet['Foldername'], TraitSet['Filename'], PrintStats=False))
					print "Importing Completed"
					GroupName = str(TempData.DateCollected)+ " " + TraitSet['Filename']
					Group = CreateGroup(file_handle, GroupName)
					TempData._SaveAllLocalVars(file_handle, Group, PrintOutput='Failed')
					print "HDF5 Saving Completed"
					if TraitSet['Draw']:
						ImageFilename = ImageLocation+str(TempData.DateCollected) + " " + str(TempData.TimeCollected) + " " + TraitSet['Filename'] + ".png" 
						Draw(TempData,ImageFilename)
						print "Drawing Completed"
				elif TraitSet['DataType'] == 'Norm':
					TempData = Norm(Data(TraitSet['Foldername'], TraitSet['Filename'], PrintStats=False))
					print "Importing Completed"
					GroupName = str(TempData.DateCollected)+ " " + TraitSet['Filename']
					Group = CreateGroup(file_handle, GroupName)
					TempData._SaveAllLocalVars(file_handle, Group, PrintOutput='Failed')
					print "HDF5 Saving Completed"
			except Exception as e:
				print e.__doc__
				print e.message
			print "Completed: {0} : Time: {1}".format(i, time() - CurrentTime)
			file_handle.flush()
			print "-------------------------"
	
	print "Total Time: {0}".format(time() - StartTime)

	file_handle.close()
	