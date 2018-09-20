# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 16:27:41 2013

@author: vatir
"""

from __future__ import print_function

#if __name__ == '__main__':
try:
    RelativePath = '.';exec(open("./SetupModulePaths.py").read());del RelativePath
except:
    exec(open("SetupModulePaths.py").read())

from Display import SetupPlot
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import numpy as np
from numpy.random import uniform, seed
from matplotlib.mlab import griddata
import time

Chan1PC = np.diff(Bins)
Chan1LTM1 = Final
#Chan1PC[2061966] = 1

Chan1PC[(numpy.std(Chan1PC)*5.0+numpy.average(Chan1PC)) < Chan1PC] = 0

Y = Chan1PC
YBin = range(max(Chan1PC))
#YBin = 10

X = Chan1LTM1

XBin = 30

#I = array(Chan1PC,dtype='float64')
#Y = I
#YBin = max(Y)

# ADC offset correction: (Numbers estimated from water data)
#X = X - 1.35
#X = X[X>0]
#Y = Y[X>0]

# griddata and contour.
start = time.clock()
try:
    i += 1
except:
    i = 0
    
Fig = SetupPlot("FILDA" + str(i))
#Fig.set_size_inches(Fig.get_size_inches()+[-5.5,0.0])


#plt.subplot(111)

H = np.histogram2d(X,Y, bins=(XBin,YBin))
LM1BinPoints = H[1][:-1]
PCBinPoints = H[2][:-1]
ar = H[0]

left, width = 0.1, 0.65
bottom, height = 0.1, 0.65
bottom_h = left_h = left+width+0.02
#Fig.set_figwidth(6)

rect_scatter = [left, bottom, width, height]
rect_histx = [left, bottom_h, width, 0.2]
rect_histy = [left_h, bottom, 0.2, height]

#plt.contour(xi,yi,zi,15,linewidths=0.5,colors='k')
#plt.contourf(xi,yi,zi,15,cmap=plt.cm.rainbow,
#             norm=plt.normalize(vmax=abs(zi).max(), vmin=-abs(zi).max()))
axScatter = plt.axes(rect_scatter)

plt.xlabel("Time (ns)")
plt.ylabel("N")


axHistx = plt.axes(rect_histx)
axHisty = plt.axes(rect_histy)

try:
    axScatter.contour(LM1BinPoints, PCBinPoints, ar.T,30,linewidths=0.2,colors='k', antialiased=True, interpolation='nearest')
except ValueError:
    pass

CFMain = axScatter.contourf(LM1BinPoints, PCBinPoints, ar.T,30,cmap=plt.cm.rainbow,
             norm=plt.normalize(vmax=abs(ar).max(), vmin=0.0),antialiased=False, interpolation='nearest')

#axScatter.set_xlim(min(LM1BinPoints),max(LM1BinPoints))
#axScatter.set_ylim(min(PCBinPoints),max(PCBinPoints))
axScatter.set_xlim(0.0,max(LM1BinPoints))

#axScatter.set_ylim(0.0,max(PCBinPoints))
axScatter.set_ylim(0.0,(numpy.std(Chan1PC)*3.0+numpy.average(Chan1PC)))


nullfmt   = NullFormatter()
# no labels

# the scatter plot:

axHistx.hist(X, bins=XBin, color = 'blue', linewidth = 0.2)
axHisty.hist(Y, bins=YBin, orientation='horizontal', color = 'r', linewidth = 0.2)

axHistx.set_xlim( axScatter.get_xlim() )
axHisty.set_ylim( axScatter.get_ylim() )

axHistx.xaxis.set_major_formatter(nullfmt)
axHisty.yaxis.set_major_formatter(nullfmt)

#axHisty.xaxis.set_major_locator(MaxNLocator(4))
#axHistx.yaxis.set_major_locator(MaxNLocator(4))
axHistx.yaxis.set_major_formatter(nullfmt)
axHisty.xaxis.set_major_formatter(nullfmt)

plt.colorbar(CFMain) # draw colorbar


#plt.plot(x, y, 'ko', ms=3)
#plt.title('FILDA')

plt.draw()

"""
X = array(Chan1PC,dtype='float64')
Y = array(Chan1LTM1,dtype='float64')

# griddata and contour.
start = time.clock()
SetupPlot("FILDA")

#plt.subplot(111)
H = histogram2d(X,Y, bins=(LPCH,100))
LM1BinPoints = H[2][:-1]
PCBinPoints = H[1][:-1]
ar = H[0]

try:
    plt.contour(LM1BinPoints, PCBinPoints, ar,30,linewidths=0.2,colors='k', antialiased=True)
except ValueError:
    pass
    
plt.contourf(LM1BinPoints, PCBinPoints, ar,30,cmap=plt.cm.rainbow,
             norm=plt.normalize(vmax=abs(ar).max(), vmin=0.0),antialiased=False)

plt.colorbar() # draw colorbar



#plt.contour(xi,yi,zi,15,linewidths=0.5,colors='k')
#plt.contourf(xi,yi,zi,15,cmap=plt.cm.rainbow,
#             norm=plt.normalize(vmax=abs(zi).max(), vmin=-abs(zi).max()))

#plt.plot(x, y, 'ko', ms=3)
plt.xlim(LM1BinPoints[0],LM1BinPoints[-1])
plt.ylim(PCBinPoints[0],PCBinPoints[-1])
plt.xlabel("ns")
plt.ylabel("N")
plt.title('FILDA')

plt.draw()
"""