# -*- coding: utf-8 -*-
"""
Created on Wed May 20 15:19:41 2020

@author: minghung
"""

import os, sys, time
from Logger import Logger 
import logging   
from PyQt5 import QtCore, QtWidgets, QtGui 
from PyQt5.QtCore import QThread,pyqtSignal


#if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
#if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
        
from TabSelectChamber import TabSelectChamber
from TabEmbryoResults import TabEmbryoResults
from TabHistoryChamber import TabHistoryChamber
from TabMachineSelection import TabMachineSelection
#import inf_add_mask






class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(0, 0 , 1800, 1050)
        self.setWindowTitle('Embryo Analysis System')
        self.setStyleSheet("QWidget{background-color:#ff90b1;}")
       
        self.tabs = QtWidgets.QTabWidget(self) 
        self.tabs.setFixedSize(QtCore.QSize(1800, 1050))          
        
        self.widget_selChamber = TabSelectChamber(logger, self)
        self.widget_selMachine = TabMachineSelection(logger, self.widget_selChamber, self)
        self.widget_embryoResults = TabEmbryoResults(logger, self.widget_selMachine, self)
        self.widget_historyResults = TabHistoryChamber(logger, self.widget_selMachine.machine_infos, self.widget_selChamber, self)
        self.tabs.setIconSize(QtCore.QSize(35, 35)) 
        self.tabs.addTab(self.widget_selMachine, QtGui.QIcon('machine.png'), 'Machine Selection')
        self.tabs.addTab(self.widget_selChamber, QtGui.QIcon('logo.png'), 'Chamber Selection')
        self.tabs.addTab(self.widget_embryoResults, QtGui.QIcon('embryo.png'), 'Embryo Viewer')
        self.tabs.addTab(self.widget_historyResults, QtGui.QIcon('history.png'), 'History') 

        self.tabs.currentChanged.connect(self.onChange)
                
    def onChange(self, i):
        if i == 3:
            self.widget_historyResults.SearchPatientID()
        
    def closeEvent(self, event):
        self.widget_selChamber.closeEvent(event)
        #self.widget_selMachine.closeEvent(event)
        #self.widget_embryoResults.closeEvent(event)
        #self.widget_historyResults.closeEvent(event)
        #self.thread.stop()
        print('stop')
        time.sleep(4)
        self.close()
        
if __name__ == '__main__':
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    logger = Logger('embryo').logger
    logger.setLevel(logging.INFO)  
     
    app = QtWidgets.QApplication(sys.argv)
    #app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    window = Window()        
    window.show()
    sys.exit(app.exec_())
    
