# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 15:01:22 2020

@author: minghung
"""

from PyQt5 import QtCore, QtWidgets, QtGui 


class SelectCellDish(QtWidgets.QPushButton):
    def __init__(self, chid, wid, main_widget,board_info_check_change, parent=None):
        super(SelectCellDish, self).__init__(parent)
        self.main_widget = main_widget
        self.selected = False
        self.chamber_id = int(chid)
        self.well_id = int(wid)
        self.status = ''
        self.board_info_check_change = board_info_check_change

        self.setDisabled(True)
        self.setText('Well' + str(wid))
        self.setStyleSheet("QPushButton {border: 1px solid rgb(190,190,190);background-color: rgb(190,190,190); border-radius: 30; font: bold 14;font-weight:bold;color: white;text-align: center;} QPushButton:pressed {border-style: inset;}") 
    #change status of board_info_check_change
    def ChangeBoardInfoCheckBool(self,board_info_check_change):
        self.board_info_check_change =board_info_check_change

    def mousePressEvent(self, QMouseEvent):        
        #Select dish
        '''
        if QMouseEvent.button() == QtCore.Qt.LeftButton:    
            return
            if not self.selected:
                self.setStyleSheet("QPushButton {border: 1px solid rgb(190,190,190);background-color: lime; border-radius: 30; font-size: 14;font-weight:bold;color: white;text-align: center;} QPushButton:pressed {border-style: inset;}") 
                self.selected = True
            else:
                self.setStyleSheet("QPushButton {border: 1px solid rgb(190,190,190);background-color: rgb(190,190,190); border-radius: 30; font-size: 14;font-weight:bold;color: white;text-align: center;} QPushButton:pressed {border-style: inset;}") 
                self.selected = False
        '''       
        #Change tab to show video and picture
        if QMouseEvent.button() == QtCore.Qt.LeftButton:
            # check after change board info press save info button or not
            
            if not self.board_info_check_change:
                QtWidgets.QMessageBox.warning(self,'error','press save')
                
            else:
                if not self.selected:
                    return
                reply = QtWidgets.QMessageBox.information(self.main_widget, 'View Embryo','Video and Image Show', QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Close, QtWidgets.QMessageBox.Close)
                if reply == QtWidgets.QMessageBox.Ok:                
                    self.main_widget.tabs.setCurrentIndex(2)
                    patient_id = self.main_widget.tabs.widget(1).GetTimeLapseID(self.chamber_id)
                    self.main_widget.tabs.widget(2).initSource(patient_id, self.chamber_id, self.well_id)                
                else:
                    pass           
    
    #Set dish selected        
    def setEnable(self, status):
        if status == 't':
            self.setStyleSheet("QPushButton {border: 1px solid rgb(190,190,190);background-color: lime; border-radius: 30; font-size: 14;font-weight:bold;color: white;text-align: center;} QPushButton:pressed {border-style: inset;}") 
        elif status == 'd':
            self.setStyleSheet("QPushButton {border: 1px solid rgb(190,190,190);background-color: red; border-radius: 30; font-size: 14;font-weight:bold;color: white;text-align: center;} QPushButton:pressed {border-style: inset;}") 
        elif status == 'f':
            self.setStyleSheet("QPushButton {border: 1px solid rgb(190,190,190);background-color: dodgerblue; border-radius: 30; font-size: 14;font-weight:bold;color: white;text-align: center;} QPushButton:pressed {border-style: inset;}") 
        else:
            self.setStyleSheet("QPushButton {border: 1px solid rgb(190,190,190);background-color: rgb(190,190,190); border-radius: 30; font-size: 14;font-weight:bold;color: white;text-align: center;} QPushButton:pressed {border-style: inset;}") 
        
        self.selected = True
        self.status = status
    
    #Reset status        
    def reset(self):
        self.setStyleSheet("QPushButton {border: 1px solid rgb(190,190,190);background-color: rgb(190,190,190); border-radius: 30; font-size: 14;font-weight:bold;color: white;text-align: center;} QPushButton:pressed {border-style: inset;}") 
        self.selected = False
    