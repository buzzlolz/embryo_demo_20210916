# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 09:02:16 2019

@author: minghung
"""

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from PyQt5 import QtWidgets, QtGui, QtCore

import random

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=7, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
        self.Plot([random.random() for i in range(1000)])        
        
    def Plot(self, data):            
        self.ax.plot(data, 'r-')
        self.ax.set_title('Embryo Developed Curve')
        self.ax.axis([0, 70, 0, 8.5])
        self.ax.grid(True)
        self.second_line, = self.ax.plot([], [], c = '#ff7538')
        
        self.y_labels = ['', '2pn', '2cell', '3cell', '4cell', '5cell', 'morula', 'earlybc', 'blastocyst']
        self.ax.set_yticks([i for i in range(len(self.y_labels))])  
        self.ax.set_yticklabels(self.y_labels)
             
        self.draw()
        
    def MoveSecondLine(self, ctime):         
        self.second_line.set_xdata([ctime, ctime])
        self.second_line.set_ydata([10, 0])                          
        self.draw()      
        
