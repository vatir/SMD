#!/usr/bin/python
'''
Created on Oct 10, 2013

@author: vatir
'''

# Use this section if direct CLI calling is desired

try:
    from TTSPCfromBH import TTPhotonDataImport
except:
    try:
        exec(open('../SetupModulePaths.py').read())
        PathsSet = True
        from TTSPCfromBH import TTPhotonDataImport
    except:
        pass
        
# Large Norm Testing
defaultfilename = "exp 2 room light"
defaultfolder = "2013/09/01"

# Small Norm Testing
defaultfilename = "exp 5 wavelength 765 nm room light"
defaultfolder = "2013/08/22"

# Medium Norm Testing (2 Channel)
defaultfilename = "exp 2 room light"
defaultfolder = "Single_Molecule_Data/local_data/August/30"

# Medium Norm 3 Channel Testing
# defaultfilename = "gain 3 room light 60 sec"
# defaultfolder = "Single_Molecule_Data/local_data/Water and Buffer Testing/"

# High Count Rate Data File
HCRFilename = "exp 8 1 nm dna in buffer cp"
HCRFolder = "2013/09/01"

# High Count Rate Data File
HCRFilename = "exp 4 wavelength 765 nm 50 pm dna one emission filters condensing lense circular polarizer room lights off long run"
HCRFolder  = "2013/08/22"

# Medium Size Data
HCRFilename = "exp 5 old buffer 150 pol day old test"
HCRFolder  = "Single_Molecule_Data/local_data/August/30"

def LoadHighCountRateData(Locals, DataVariableName ='HCRData' , PrintOutput = False, ForceUpdate = False):
    return LoadData(Locals, HCRFolder, HCRFilename, DataVariableName, PrintOutput, ForceUpdate)

def LoadData(Locals, Folder='', Filename='', DataVariableName ='ImportedData' , PrintOutput = False, ForceUpdate = False):
    if ForceUpdate or (not ((str(DataVariableName) in Locals.keys()))):
        print str(DataVariableName) + " : not found : Importing..."
        from TTSPCfromBH.TTPhotonDataImport import Data
        if (Folder == '' and Filename == ''):
            return Data(defaultfolder, defaultfilename, PrintOutput)
        else:
            return Data(Folder, Filename, PrintOutput)
    return Locals[DataVariableName]

def LoadNorm(Locals, ImportedData, DataVariableName ='CurrentNorm', PrintOutput = False, ForceUpdate = False):
    if ForceUpdate or (not(str(DataVariableName) in Locals)):
        print str(DataVariableName) + " : not found : Importing..."
        from TTSPCfromBH.NormCalc import Norm
        return Norm(ImportedData)
    return Locals[DataVariableName]

if __name__ == '__main__':
    RelativePath = '..';exec(open('../SetupModulePaths.py').read());del RelativePath
    
    print "Testing LoadData:"
    ImportedData = LoadData(locals(), 
                            DataVariableName ='ImportedData', 
                            PrintOutput = True)
    
    print "\nTesting HCRData:"
    LoadHighCountRateData(locals(), 
            DataVariableName ='HCRData', 
            PrintOutput = True)
    
    print "\nTesting LoadNorm:"
    LoadNorm(locals(),
             ImportedData, 
             DataVariableName ='CurrentNorm'
             )
