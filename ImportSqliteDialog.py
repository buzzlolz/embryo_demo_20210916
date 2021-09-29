# -*- coding: utf-8 -*-
"""
Created on Wed May 20 15:19:41 2020

@author: minghung
"""

import os, sys, time, json, glob
from Logger import Logger 
import logging   
from PyQt5 import QtCore, QtWidgets, QtGui 

       
class ImportSqliteDialog(QtWidgets.QDialog):
    def __init__(self, main_parent, parent=None):       
        super(ImportSqliteDialog, self).__init__(parent=parent)        
        self.setWindowTitle('Import data')
        self.setStyleSheet("QWidget{background-color:#ddf5c2;}")     
        self.mnt_sqlite_path = '/home/n200/D-slot/20201221_ivf_data/'   
        
        self.parent = main_parent
        self.setGeometry(500, 200, 600, 200)
        self.cid = ''
        
        self.initUI()                
        
    def initUI(self):         
        label = QtWidgets.QLabel(self)
        label.setGeometry(20, 10, 150, 50)
        label.setFont(QtGui.QFont('Arial', 12))
        label.setText('Chamber ID:')
        
        self.edit_cid = QtWidgets.QLineEdit(self)
        self.edit_cid.setGeometry(150, 10, 50, 40)
        self.edit_cid.setStyleSheet('background-color:white;')  
        self.edit_cid.setText(self.cid)
        self.edit_cid.setReadOnly(True)
        
        label = QtWidgets.QLabel(self)
        label.setGeometry(20, 70, 100, 50)
        label.setFont(QtGui.QFont('Arial', 12))
        label.setText('Select PID:')        
        
        self.selector_pid = QtWidgets.QComboBox(self)      
        self.selector_pid.setEditable(True)   #change in 20210909
        self.selector_pid.setStyleSheet("background-color:white;selection-background-color: darkblue")           
        self.selector_pid.setGeometry(150, 70, 310, 40)
        
        self.button_ok = QtWidgets.QPushButton(self)
        self.button_ok.setGeometry(150, 130, 80, 40)
        self.button_ok.setText('OK')
        self.button_ok.setStyleSheet('background-color:lightblue;')
        self.button_ok.clicked.connect(self.select_finish)
        
    def show(self):
        self.edit_cid.setText(self.cid)
        self.selector_pid.clear()
        self.add_item()
        super(ImportSqliteDialog, self).show()
        
    def add_item(self):
        curr_pids = self.parent.GetCurrentPatientIDs()
        dirs = os.listdir(self.mnt_sqlite_path)
        for d in dirs:
            if d not in curr_pids:        
                self.selector_pid.addItem(str(d))           
            
    def select_finish(self):                
        self.parent.CallExtractSqlite(str(self.selector_pid.currentText()), str(self.edit_cid.text()))
        self.hide()
        
    def closeEvent(self, event):  
        self.hide()

        
if __name__ == '__main__':
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    logger = Logger('barcode').logger
    logger.setLevel(logging.INFO)     
     
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    window = AddCommodityWidget(0, None)        
    window.show()
    window.StartPlay()
    sys.exit(app.exec_())
    
