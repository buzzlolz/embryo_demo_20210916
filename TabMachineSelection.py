# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 13:08:43 2020

@author: minghung
"""

import os, io, math
from configparser import RawConfigParser
from Calendar import Calendar
from PyQt5 import QtCore, QtWidgets, QtGui 

from SelectCellDish import SelectCellDish


class TabMachineSelection(QtWidgets.QWidget):
    def __init__(self, logger, widget_partner, main_widget, parent=None):
        super(TabMachineSelection, self).__init__(parent=parent)
        self.tab_partner = widget_partner
        self.main_widget = main_widget
        self.logger = logger        
        self.cfg_machine = RawConfigParser()  
        self.machine_cfg_path = './config/config_machine.ini'
        self.machine_infos, self.parameters = self.ReadMachineConfig()  
        self.edit_grades = []
      
        self.initUI()
        
    def initUI(self):
        #Patient info        
        self.frame_setting = QtWidgets.QFrame(self)        
        self.frame_setting.setFrameShape(QtWidgets.QFrame.StyledPanel)
        #self.frame_setting.setFixedSize(QtCore.QSize(800, 500))
        self.frame_setting.setGeometry(10, 10, 600, 320)
        
        # label_gs = QtWidgets.QLabel('Embryo Grading:', self.frame_setting) 
        # label_gs.setFont(QtGui.QFont('Arial', 12))
        # label_gs.setGeometry(10, 10, 150, 30)
        # for i in range(4):
        #     label_g = QtWidgets.QLabel('Grade ' + str(i+1) + ' =', self.frame_setting)
        #     label_g.setFont(QtGui.QFont('Arial', 12))
        #     label_g.setGeometry(10, 10 + 50*(i+1), 100, 40)
        #     edit_grade = QtWidgets.QLineEdit(self.frame_setting)
        #     edit_grade.setGeometry(100, 10 + 50*(i+1), 40, 40)
        #     edit_grade.setStyleSheet('background-color:white;') 
        #     edit_grade.setAlignment(QtCore.Qt.AlignRight)            
        #     edit_grade.setText(str(self.parameters["grade" + str(i + 1)]))
        #     self.edit_grades.append(edit_grade)
        #     label_percent = QtWidgets.QLabel('%', self.frame_setting)
        #     label_percent.setFont(QtGui.QFont('Arial', 12))
        #     label_percent.setGeometry(150, 10 + 50*(i+1), 50, 40)
               
        label_m = QtWidgets.QLabel('Incubation System:', self.frame_setting) 
        label_m.setFont(QtGui.QFont('Arial', 12))
        label_m.setGeometry(250, 10, 170, 40)
        self.selector_machine = QtWidgets.QComboBox(self.frame_setting)         
        self.selector_machine.setStyleSheet("background-color:white;selection-background-color: darkblue")           
        self.selector_machine.setGeometry(250, 60, 150, 40)     
        for m in self.machine_infos:
            self.selector_machine.addItem(str(m[0]))                               
        self.selector_machine.currentIndexChanged.connect(self.ResetChamberPlant)   
        
        # self.button_save = QtWidgets.QPushButton('Save', self.frame_setting)
        # self.button_save.setGeometry(250, 120, 100, 40)
        # self.button_save.setStyleSheet('QPushButton {background-color:lightblue;border-radius: 20px;}  QPushButton:hover{color:black;background:bisque;} QPushButton:pressed {background:lightcoral}')
        # self.button_save.clicked.connect(self.SaveSetting)                
        
        self.frame_chamber = QtWidgets.QFrame(self) 
        self.frame_chamber.setGeometry(10, 340, 1580, 630)     
        self.frame_chamber.setFrameShape(QtWidgets.QFrame.StyledPanel)        
        self.layout_chamber = QtWidgets.QGridLayout(self.frame_chamber) 
        #self.layout_chamber.setAlignment(QtCore.Qt.AlignHCenter)                
                        
        self.AddWells(self.machine_infos[0][1], self.machine_infos[0][2])   
        self.tab_partner.AddWells(self.machine_infos[0][1], self.machine_infos[0][2])
              
        index = self.selector_machine.findText(self.parameters["machine"], QtCore.Qt.MatchFixedString)
        self.selector_machine.setCurrentIndex(index)
                     
    #Read config file        
    def ReadMachineConfig(self): 
        path = self.machine_cfg_path
        self.logger.info('Read file=' + path)
        if not os.path.exists(path):
            print('Not found file=' + path) 
            self.logger.error('Not found file=' + path)                               
            return []
        #try:
        if True:            
            machine_infos = []
            self.cfg_machine.read(path)                
            if 'name' in [item[0] for item in self.cfg_machine.items('CompanyInfo')]:                
                names = self.cfg_machine.get('CompanyInfo', 'name').split(',')
                for name in names:                    
                    if 'Machine_' + name in self.cfg_machine.sections():
                        chamber_number = self.cfg_machine.get('Machine_' + name, 'chamber')
                        well_number = self.cfg_machine.get('Machine_' + name, 'well')
                        machine_infos.append((name, int(chamber_number), int(well_number)))
                        
            setting = {"machine":'', "grade1":0, "grade2":0, "grade3":0, "grade4":0, "grade5":0, "t1":'', "t2":'', "t4":'', "t8":'', "teb":''} 
            for key, value in setting.items():                
                if key in [item[0] for item in self.cfg_machine.items('Setting')]:           
                    setting[key] = self.cfg_machine.get('Setting', key)               
           
            return machine_infos, setting
        #except:
        #   self.logger.error('Read config error. msg=' + str(sys.exc_info()[1])) 
        #    return [] 
            
    def SaveSetting(self):
        self.cfg_machine.set('Setting', 'machine', str(self.selector_machine.currentText()))
        for i, edit in enumerate(self.edit_grades):
            self.cfg_machine.set('Setting', 'grade' + str(i + 1), str(edit.text()))            
                    
        with io.open(self.machine_cfg_path, 'w') as f:
            self.cfg_machine.write(f)      
            
    def AddWells(self, chamber_number, well_number):
        count = 0      
        for frame_row in range(3):            
            for i in range(3):                
                
                #Chamber selection
                widget_chamber = QtWidgets.QWidget()
                group_chamber = QtWidgets.QGroupBox(widget_chamber)                
                #group_chamber.setFrameShape(QtWidgets.QFrame.StyledPanel)
                group_chamber.setFixedSize(QtCore.QSize(510, 200))
                #group_chamber.setGeometry(10 + i*440 + 5*i, 0 + 200*frame_row + 5*frame_row, 440, 200)
                #print(10 + i*440 + 5*i, 0 + 200*frame_row + 5*frame_row)
                
                if count >= chamber_number:
                    self.layout_chamber.addWidget(widget_chamber, frame_row, i)
                    count += 1
                    continue
                
                label_choose = QtWidgets.QLabel('Chamber Number:' + str(3*frame_row + i + 1), group_chamber)
                label_choose.setFont(QtGui.QFont('Arial', 12))
                label_choose.setGeometry(10, 10, 250, 40)      
              
                #Add dishs
                #self.select_dishs = []
                count_well = 0                
                for c in range(8):
                    for r in range(2):
                        if count_well >= well_number:
                            continue
                        dish = SelectCellDish(count + 1, (c * 2) + r + 1, self.main_widget, group_chamber)
                        dish.setDisabled(True)
                        dish.setGeometry(5 + 50 * c + 12 * c, 50 + r * 50 + 12 * r, 60, 60)
                        count_well += 1
                        #dish.setEnabled(False)
                    #self.select_dishs.append(dish)
                
                self.layout_chamber.addWidget(widget_chamber, frame_row, i)
                count += 1
                
    def ResetChamberPlant(self):
        #Clear
        while self.layout_chamber.count():
            item = self.layout_chamber.takeAt(0)
            widget = item.widget()
            widget.deleteLater()      
        
        #Add new
        machine = self.selector_machine.currentText()
        sel_machine = [m for m in self.machine_infos if m[0] == machine]        
        if sel_machine != []:
            print('reset')
            self.AddWells(sel_machine[0][1], sel_machine[0][2])
            self.tab_partner.AddWells(sel_machine[0][1], sel_machine[0][2])
    