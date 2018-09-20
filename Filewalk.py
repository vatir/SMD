#!/usr/bin/python
'''
Created on Oct 24, 2013

@author: vatir
'''

if __name__ == '__main__':
	from re import search

#	DirPrefixSearch = search('^(.*)/SMD.*$',CurPath)
#	if DirPrefixSearch != None:
#		DirPrefix = DirPrefixSearch.group(1)
#	else:
#		DirPrefix = ''

	d = set()
	f = set()
	from collections import OrderedDict
	Items = OrderedDict()
	
	from os import walk
	for x in walk('../DATA/'):
		for Filename in x[2]:
			Results = search('^(.*)_\d{3}\.set$', Filename)
			try:
				Items[Results.group(1)] = x[0]
			except:
				pass
	
	for x in Items.items():
		print '"'+str(x[0])+'"' + "\t" + '"'+str(x[1])+'"'
#         for filename in x:
#             print filename
	