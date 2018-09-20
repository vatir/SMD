#!/usr/bin/python
'''
Created on Oct 2, 2013

@author: vatir
'''
import tables

def FileOpen(filename):
    """
    Open a HDF5 file.
    
    If the file exists then open in read/write, otherwise create the file.
    
    Returns the file handle.
    """
    
    try:
        return tables.openFile(filename, mode="r+")
    except:
        return tables.openFile(filename, mode="w")
        print "File did not exist: Opened a new file"

def NodeCreate(FileHandle, Location, Name):
    """
    Create a HDF5 node.
    
    If the node exists then destroy the node and recreate.
    
    Returns the friendly name.
    """
    
    try:
        return FileHandle.create_group(Location, Name)
    except tables.NodeError:
        FileHandle.remove_node(Location, Name, recursive=True)
        return FileHandle.create_group(Location, Name)
