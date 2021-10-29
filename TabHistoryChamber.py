# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 09:28:48 2020

@author: minghung
"""

import os, io, json, math
from configparser import RawConfigParser
from Calendar import Calendar
from PyQt5 import QtCore, QtWidgets, QtGui 

from EmbryoBoxInfo import EmbryoHistoryInfoTableBox
from Ui_Function import * 


class TabHistoryChamber(QtWidgets.QWidget):
    def __init__(self, logger, machine_infos, widget_selChamber, main_widget, parent=None):
        super(TabHistoryChamber, self).__init__(parent=parent)
        self.main_widget = main_widget
        self.logger = logger
        self.cfg = RawConfigParser()    
        self.well_number = int(machine_infos[0][2])        
        self.selChamber_tab = widget_selChamber
        self.init()
        self.mnt_history_path = './history/'


    def init(self):        
        #Setting area
        self.frame_setting = QtWidgets.QFrame(self)        
        self.frame_setting.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_setting.setGeometry(10, 5, 1580, 60)
        
        label_pid = QtWidgets.QLabel('Patient ID:', self.frame_setting)
        
        label_pid.setFont(QtGui.QFont('Arial', 12))
        label_pid.setGeometry(10, 10, 120, 40)
        self.selector_pid = QtWidgets.QComboBox(self.frame_setting)         
        self.selector_pid.setEditable(True)   #change in 20210909
        self.selector_pid.setStyleSheet("background-color:white;selection-background-color: darkblue")           
        self.selector_pid.setGeometry(85, 10, 310, 40)         
        self.selector_pid.currentIndexChanged.connect(lambda: self.selector_files.clear())       
        
        label_startTime = QtWidgets.QLabel('Start Time:', self.frame_setting)
        label_startTime.setFont(QtGui.QFont('Arial', 12))
        label_startTime.setGeometry(400, 10, 100, 40)
        self.edit_startTime = QtWidgets.QLineEdit(self.frame_setting)
        self.edit_startTime.setGeometry(480, 10, 200, 40)
        self.edit_startTime.setStyleSheet('background-color:white;')  
        self.edit_startTime.setText('2020/01/01 00:00:00')
        
        self.button_calendar_start = QtWidgets.QPushButton(self.frame_setting)
        self.button_calendar_start.setGeometry(655, 10, 50, 40)
        self.button_calendar_start.setStyleSheet('background-color:lightblue;')
        self.button_calendar_start.setIcon(QtGui.QIcon('CalenderIcon.png'))
        self.button_calendar_start.setIconSize(QtCore.QSize(130,130))
        self.button_calendar_start.clicked.connect(lambda: self.SelectDate('start'))
        
        label_endTime = QtWidgets.QLabel('End Time:', self.frame_setting)
        label_endTime.setFont(QtGui.QFont('Arial', 12))
        label_endTime.setGeometry(720, 10, 100, 40)
        self.edit_endTime = QtWidgets.QLineEdit(self.frame_setting)
        self.edit_endTime.setGeometry(820, 10, 200, 40)
        self.edit_endTime.setStyleSheet('background-color:white;')  
        self.edit_endTime.setText('2020/12/31 24:00:00')
        
        self.button_calendar_end = QtWidgets.QPushButton(self.frame_setting)
        self.button_calendar_end.setGeometry(1025, 10, 50, 40)
        self.button_calendar_end.setStyleSheet('background-color:lightblue;')
        self.button_calendar_end.setIcon(QtGui.QIcon('CalenderIcon.png'))
        self.button_calendar_end.setIconSize(QtCore.QSize(130,130))
        self.button_calendar_end.clicked.connect(lambda: self.SelectDate('end'))
        
        self.button_search = QtWidgets.QPushButton('Search', self.frame_setting)
        self.button_search.setGeometry(1080, 10, 100, 40)
        self.button_search.setStyleSheet('QPushButton {background-color:lightblue;border-radius: 20px;}  QPushButton:hover{color:black;background:bisque;} QPushButton:pressed {background:lightcoral}')
        self.button_search.clicked.connect(self.SearchFiles)
        
        label_results = QtWidgets.QLabel('Results:', self.frame_setting)
        label_results.setFont(QtGui.QFont('Arial', 12))
        label_results.setGeometry(1200, 10, 100, 40)
        self.selector_files = QtWidgets.QComboBox(self.frame_setting)         
        self.selector_files.setStyleSheet("background-color:#55cbcd;selection-background-color: darkblue")           
        self.selector_files.setGeometry(1280, 10, 200, 40)  
        self.selector_files.view().pressed.connect(self.FileLoad)        
        
        self.button_save = QtWidgets.QPushButton('Save', self.frame_setting)
        self.button_save.setGeometry(1490, 10, 80, 40)
        self.button_save.setStyleSheet('QPushButton {background-color:lightblue;border-radius: 20px;}  QPushButton:hover{color:black;background:bisque;} QPushButton:pressed {background:lightcoral}')
        self.button_save.clicked.connect(self.SaveTableChangeToFile)
        self.button_save.setDisabled(True)
        
        #Chamber scroll area
        self.groupBox = QtWidgets.QGroupBox(self)
        self.groupBox.setGeometry(QtCore.QRect(10, 70, 1580, 900))
        self.groupBox.setObjectName("groupBox")
        self.scrollArea = QtWidgets.QScrollArea(self.groupBox)
        self.scrollArea.move(0, 0)
        self.scrollArea.setFixedWidth(1580)
        self.scrollArea.setMinimumHeight(900)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        
        self.AddTableBox(self.scrollAreaWidgetContents)
    
    def AddTableBox(self, parent):
        vert_lay = QtWidgets.QGridLayout(parent)         
        self.embryo_info_array = []
        for j in range(4):
            
                #if len(self.embryo_info_array) < self.well_number:
                embryo_info = EmbryoHistoryInfoTableBox(len(self.embryo_info_array) + 1)                  
                self.embryo_info_array.append(embryo_info)  
                vert_lay.addWidget(embryo_info, j, 0 , 1, 1)              
        vert_lay.setSpacing(1)
        
    def SelectDate(self, item):        
        calendar = Calendar('history', item, self)
        calendar.show()
        calendar.exec_()        
        
    def FileLoad(self, event):        
        #Set chamber id        
        chamber_ids = []

        history_dirs = os.listdir(self.mnt_history_path + str(self.selector_pid.currentText()) + '/' +  str(self.selector_files.currentText()) + '/csv/')        
        for dd in history_dirs:
            if os.path.isdir(self.mnt_history_path + str(self.selector_pid.currentText()) + '/' +  str(self.selector_files.currentText()) + '/csv/' + dd):
                dir_names = dd.split('cham')
                if len(dir_names) > 0:
                    chamber_ids.append(dir_names[1])       
        for tab in self.embryo_info_array:
            tab.SetChamberID(chamber_ids[0])
                    
        #Find history data
        get_dic = search_history_csv(str(self.selector_pid.currentText()), str(self.selector_files.currentText()))
        self.InsertInfomationToTable(str(self.selector_pid.currentText()), str(self.selector_files.currentText()), get_dic)    
        self.button_save.setDisabled(False) 
        
    def SearchPatientID(self):
        pids_history = []
        history_dirs = os.listdir(self.mnt_history_path)        
        for dd in history_dirs:
            if os.path.isdir(self.mnt_history_path + dd):
                pids_history.append(dd)
                
        self.selector_pid.clear()
        for pid in pids_history:        
           self.selector_pid.addItem(str(pid))      
            
    def SearchFiles(self):       
        id_time_list = history_getid_timelist(str(self.selector_pid.currentText()))
        if id_time_list == None:
            return     
        self.selector_files.clear()   
        for m in id_time_list:
            self.selector_files.addItem(m)                     
        
    def InsertInfomationToTable(self, patient_id, date, dict_msg):        
        #Clear all table
        for table in self.embryo_info_array:
            table.SetPidDate(patient_id, date)
            for i in range(12):
                self.set_embryo_table_item(table, i + 2, 2, '')
                self.set_embryo_table_item(table, i + 2, 4, '')
            #self.set_embryo_table_item(table, 14, 2, '')
            
        total_score = 0
        #{'DishList': [{'DishId': '8', 'Fragment': {}, 'Info': {}}, {'DishId': 2, 'Info': {'Status': 'Discard', 't2': nan, 't3': 9.67, 't4': 11.0, 't5': 18.0, 't6': 20.5, 't7': nan, 't8': 20.83, 'Morula': nan, 'Blas': 21.83, 'comp': nan, 'PN_Fading': 0.0, 'ICM': nan, 'TE': nan, 'PGS': nan, 'Probility': 0.88088155}, 'Fragment': {'pn': 1.5880851063829784, 't2': 3.1957142857142857, 't3': 3.301904761904763, 't4': 3.3818181818181823, 't5': 4.46, 't6': 4.185238095238096, 't7': 3.469166666666667, 't8': 7.082189781021898, 'morula': 8.13, 'blas': 10.843580786026202}}
        print(dict_msg)
        print(dict_msg.keys())
        print(dict_msg["DishList"][0].keys())
        print(dict_msg["DishList"][0]['Info'])
        # print(dict_msg['DishList']['Info'])
        coll_probs = [(dish_info["DishId"], dish_info["Info"]["Probility"]) for dish_info in dict_msg["DishList"] if "Probility" in dish_info["Info"] and dish_info["Info"]["Probility"] != ''] 
        coll_probs.sort(key=lambda tup: tup[1], reverse=True)            
        
        for dish_info in dict_msg["DishList"]:    
            embryo_tables = [table for table in self.embryo_info_array if int(dish_info["DishId"]) == table.well_id]
            if embryo_tables == []:
                continue
            total_score = 0
            count = 0
            #print(dish_info)
            #t2-t8
            for i in range(7):            
                #Insert division time
                if "Info" in dish_info and 't' + str(i + 2) in dish_info["Info"]:                    
                    time = str(dish_info["Info"]['t' + str(i + 2)])
                    self.set_embryo_table_item(embryo_tables[0], i + 3, 2, time)
                    #print('t' + str(i + 2), embryo_tables[0].well_id, time)
                 
                #Insert score
                if "Fragment" in dish_info and 't' + str(i + 2) in dish_info["Fragment"]:
                    try:
                        value = int(100 - (4 * (math.ceil(dish_info["Fragment"]['t' + str(i + 2)] * 100) / 100)))
                        if value < 0:
                            value = 0 
                        self.set_embryo_table_item(embryo_tables[0], i + 3, 4, str(value), True)
                        count += 1
                        total_score = total_score + value
                    except:
                        self.set_embryo_table_item(embryo_tables[0], i + 3, 4, '', True)                                                 
            
            #Final score                 
            if total_score > 0:
                average_score = str(int((float(total_score) / float(count)) * 100) / 100)
                # self.set_embryo_table_item(embryo_tables[0], 14, 2, average_score, True) #1230 change 
            if "Probility" in dish_info["Info"]:
                orders = [i+1 for i,e in enumerate(coll_probs) if e[0] == dish_info["DishId"]]
                if orders != []:    
                    content =  str(int(100 * dish_info["Info"]["Probility"])) + ' (' + str(orders[0]) + '/' + str(len(coll_probs)) + ')'
                else:
                    content =  str(int(100 * dish_info["Info"]["Probility"]))                       
                self.set_embryo_table_item(embryo_tables[0], 14, 2, content, True)
            else:
                self.set_embryo_table_item(embryo_tables[0], 14, 2, '', True)
                
            #molura, blas.,             
            if "Info" in dish_info and dish_info["Info"] != {}:
                print (dish_info)
                self.set_embryo_table_item(embryo_tables[0], 10, 2, str(dish_info["Info"]["Morula"]))
                self.set_embryo_table_item(embryo_tables[0], 11, 2, str(dish_info["Info"]["Blas"]))                   
                self.set_embryo_table_item(embryo_tables[0], 2, 2, str(dish_info["Info"]["PN_Fading"]))  
            #Molura score
            if "Fragment" in dish_info and 'morula' in dish_info["Fragment"]:
                try:
                    value = int(100 - (4 * (math.ceil(dish_info["Fragment"]['morula'] * 100) / 100)))
                    if value < 0:
                        value = 0 
                    self.set_embryo_table_item(embryo_tables[0], 10, 4, str(value), True)
                except:
                    self.set_embryo_table_item(embryo_tables[0], 10, 4, '', True)    
            #pn score
            if "Fragment" in dish_info and 'pn' in dish_info["Fragment"]:
                try:
                    value = int(100 - (4 * (math.ceil(dish_info["Fragment"]['pn'] * 100) / 100)))
                    if value < 0:
                        value = 0 
                    self.set_embryo_table_item(embryo_tables[0], 2, 4, str(value), True)
                except:
                    self.set_embryo_table_item(embryo_tables[0], 2, 4, '', True)    
              
            #Icm, te, decision, pgs
            embryo_tables[0].SetIcmTe()
            if "Info" in dish_info and dish_info["Info"] != {}:
                embryo_tables[0].setDecision(dish_info["Info"]["Status"],  dish_info["Info"]["Probility"])
                embryo_tables[0].setPGS(dish_info["Info"]["PGS"])                      
                    
            #Read event file
            file_path = './' + 'event_info_' + patient_id + '_' + str(embryo_tables[0].well_id) + '.txt'
            text = ''
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    text = f.read() 
            print (file_path)
            print(text)
            self.set_embryo_table_item(embryo_tables[0], 13, 2, str(text))
                    
                    
    def set_embryo_table_item(self, table, row, col, value, readonly=False):
        if str(value).lower() != 'nan':
            table.SetItem(row, col, value, readonly)        
        
    def SaveTableChangeToFile(self):       
        for i,table in enumerate(self.embryo_info_array):
            if i < self.well_number:
                table.SaveChangeItem()
               
        
        
        
                
    
    
    
                    
        