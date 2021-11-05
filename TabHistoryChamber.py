# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 09:28:48 2020

@author: minghung
"""

import os, io, json, math
from configparser import RawConfigParser
from Calendar import Calendar
from PyQt5 import QtCore, QtWidgets, QtGui 
from PyQt5 import QtMultimedia, QtMultimediaWidgets
from EmbryoBoxInfo import EmbryoHistoryInfoTableBox
from Ui_Function import * 


class CombobCheckBox(QtWidgets.QComboBox):

    def __init__(self, parent=None):
        super(CombobCheckBox, self).__init__(parent)
        self.view().pressed.connect(self.handleItemPressed)
        self._changed = False
        # self.setModel(QtGui.QStandardItemModel(self))

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:  
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)
        self._changed = True
    def getCheckItem(self):
        #getCheckItem可以獲得選擇的項目text
        checkedItems = []
        for index in range(self.count()):
            item = self.model().item(index)
            if item.checkState() == QtCore.Qt.Checked:
                checkedItems.append(item.text())
        return checkedItems
    def checkedItems(self):
        checkedItems = []
        for index in range(self.count()):
            item = self.model().item(index)
            if item.checkState() == QtCore.Qt.Checked:
                checkedItems.append(item)
        return checkedItems
    def hidePopup(self):
        if not self._changed:
            super(CombobCheckBox, self).hidePopup()
        self._changed = False
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
        self.tableload_timelapse_id=[]


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
        self.selector_files = CombobCheckBox(self.frame_setting)         
        self.selector_files.setStyleSheet("background-color:#55cbcd;selection-background-color: darkblue")           
        self.selector_files.setGeometry(1280, 10, 380, 40)  
        # self.selector_files.view().pressed.connect(self.FileLoad)        
        
        self.button_save = QtWidgets.QPushButton('Save', self)
        self.button_save.setGeometry(1700, 10, 80, 40)
        self.button_save.setStyleSheet('QPushButton {background-color:lightblue;border-radius: 20px;}  QPushButton:hover{color:black;background:bisque;} QPushButton:pressed {background:lightcoral}')
        self.button_save.clicked.connect(self.SaveTableChangeToFile)
        # self.button_save.setDisabled(True)
        

        self.button_load = QtWidgets.QPushButton('Load', self)
        self.button_load.setGeometry(1600, 10, 80, 40)
        self.button_load.setStyleSheet('QPushButton {background-color:lightblue;border-radius: 20px;}  QPushButton:hover{color:black;background:bisque;} QPushButton:pressed {background:lightcoral}')
        self.button_load.clicked.connect(self.FileLoad)
        # self.button_save.setDisabled(True)


        
        #Chamber scroll area
        # self.groupBox = QtWidgets.QGroupBox(self)
        # self.groupBox.setGeometry(QtCore.QRect(10, 70, 1580, 900))
        # self.groupBox.setObjectName("groupBox")
        # self.scrollArea = QtWidgets.QScrollArea(self.groupBox)
        # self.scrollArea.move(0, 0)
        # self.scrollArea.setFixedWidth(1580)
        # self.scrollArea.setMinimumHeight(900)
        # self.scrollArea.setWidgetResizable(True)
        # self.scrollArea.setObjectName("scrollArea")
        # self.scrollAreaWidgetContents = QtWidgets.QWidget()
        # self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        # self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        
        
        self.embryo_info_qframe = QtWidgets.QFrame(self)
        # self.embryo_info_qframe = QtWidgets.QFrame(self)        
        self.embryo_info_qframe.setFrameShape(QtWidgets.QFrame.StyledPanel)
        # self.embryo_info_qframe.setGeometry(10, 5, 1580, 60)
        self.embryo_info_qframe.setGeometry(QtCore.QRect(10, 70, 1580, 900))
        self.AddTableBox(self.embryo_info_qframe)
        # self.AddTableBox(self.embryo_info_qframe)
        # self.embryo_info_1 = EmbryoHistoryInfoTableBox(0,self.embryo_info_qframe)

        # self.embryo_info_2 = EmbryoHistoryInfoTableBox(1,self.embryo_info_qframe)
        # # self.embryo_info_1.setGeometry(QtCore.QRect(10, 70, 1580, 900))

        # self.embryo_info_array = []
        # self.embryo_info_array.append(self.embryo_info_1)
        # self.embryo_info_array.append(self.embryo_info_2)



        # label_select_file1 = QtWidgets.QLabel('Select file:', self.embryo_info_qframe)
        # label_select_file1.setFont(QtGui.QFont('Arial', 12))
        # label_select_file1.setGeometry(1230, 160, 100, 35)

        # self.selector_files_table1 = QtWidgets.QComboBox(self.embryo_info_qframe)         
        # self.selector_files_table1.setStyleSheet("background-color:#55cbcd;selection-background-color: darkblue")           
        # self.selector_files_table1.setGeometry(1230, 200, 300, 40) 
        # # self.selector_files_table1.view().pressed.connect(self.FileLoad)

        # label_select_file2 = QtWidgets.QLabel('Select file:', self.embryo_info_qframe)
        # label_select_file2.setFont(QtGui.QFont('Arial', 12))
        # label_select_file2.setGeometry(1230, 560, 100, 35)

        # self.selector_files_table2 = QtWidgets.QComboBox(self.embryo_info_qframe)         
        # self.selector_files_table2.setStyleSheet("background-color:#55cbcd;selection-background-color: darkblue")           
        # self.selector_files_table2.setGeometry(1230, 600, 300, 40) 
        # # self.selector_files_table2.view().pressed.connect(self.FileLoad)



        #video player part ----------------------------------------------------------------------
        # self.frame_video = QtWidgets.QFrame(self)        
        # self.frame_video.setFrameShape(QtWidgets.QFrame.StyledPanel)
        # self.frame_video.setFixedSize(QtCore.QSize(400, 400))  
        # self.frame_video.setStyleSheet('background-color:white;')
        # self.frame_video.setGeometry(1200,500,400,400)
               
        # self.player = QtMultimedia.QMediaPlayer(self.frame_video)
        
        # self.viewer = QtMultimediaWidgets.QVideoWidget(self.frame_video)   
        # #self.viewer.setMaximumSize(QtCore.QSize(600, 400))
        # self.player.setVideoOutput(self.viewer)     
        # self.viewer.setGeometry(1200,300,400,400)   
        
        # # layout_video = QtWidgets.QGridLayout(self.frame_video)        
        # # layout_video.addWidget(self.viewer, 0, 0, 1, 2)
       
        # self.playButton = QtWidgets.QPushButton(self)
        # # self.playButton.setFixedSize(50, 40)
        # self.playButton.setStyleSheet('background-color:lightblue;border-radius: 5px;')       
        # self.playButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        # self.playButton.clicked.connect(self.play)
        # self.playButton.setGeometry(1200,700,50,40)


        

          
        
        # self.selector_fp = QtWidgets.QComboBox(self)   
        # self.selector_fp.setFixedSize(40, 40)      
        # self.selector_fp.setStyleSheet("background-color:white;selection-background-color: darkblue")           
        # for i in range(7):
        #     self.selector_fp.addItem(str(i + 1))
        # self.selector_fp.setCurrentIndex(4) 
        # self.selector_fp.currentIndexChanged.connect(lambda: self.initSource(self.patient_id, self.chamber_id, self.well_id))
        # self.selector_fp.setGeometry(1270,650,30,30)


        # self.slider = QtWidgets.QSlider(self)        
        # self.slider.setOrientation(QtCore.Qt.Horizontal)
        # self.slider.setObjectName("horizontalSlider")
        # self.slider.setFixedWidth(580)        
        # self.slider.sliderMoved.connect(self.setPosition) 
        # self.slider.valueChanged.connect(self.setPosition) 
        # self.slider.setFocus()  #valueChanged[int].connect(self.changeValue)   
        # self.slider.setFocusPolicy(QtCore.Qt.StrongFocus)  
        # self.slider.setGeometry(1320,650,30,30)  
       
        # self.player.stateChanged.connect(self.mediaStateChanged)
        # self.player.positionChanged.connect(self.positionChanged)
        # self.player.durationChanged.connect(self.durationChanged)
        # self.player.error.connect(self.handleError)     


    
    def AddTableBox(self, parent):
        vert_lay = QtWidgets.QGridLayout(parent)         
        self.embryo_info_array = []
        for j in range(2):
            
                #if len(self.embryo_info_array) < self.well_number:
                embryo_info = EmbryoHistoryInfoTableBox(j + 1)                  
                self.embryo_info_array.append(embryo_info)  
                vert_lay.addWidget(embryo_info, j, 0 , 1, 1)              
        vert_lay.setSpacing(1)
        
    def SelectDate(self, item):        
        calendar = Calendar('history', item, self)
        calendar.show()
        calendar.exec_()        
        
    def FileLoad(self, event):        
        # Set chamber id        
        chamber_ids = []
        
       
        if len(self.selector_files.getCheckItem()) >2:
            QtWidgets.QMessageBox.warning(self,'error','select more than 2 item')
        else:

            for tableclean in self.embryo_info_array:
                tableclean.CleanAllText()
            for tabel_index,timelapse_id_time in enumerate(self.selector_files.getCheckItem()):

                print(tabel_index)
                timelapse_id = timelapse_id_time.split('->')[0]
                fertilizationtime = timelapse_id_time.split('->')[1]
                get_dic= search_history_csv(str(self.selector_pid.currentText()), timelapse_id,fertilizationtime)
                # print('get dict:',get_dic)
                self.InsertInfomationToTable(str(self.selector_pid.currentText()),timelapse_id,fertilizationtime ,tabel_index, get_dic)
                
                # self.InsertInfomationToTable(str(self.selector_pid.currentText()), str(self.selector_files.currentText()), get_dic)
                
        
        

        # history_dirs = os.listdir(self.mnt_history_path + str(self.selector_pid.currentText()) + '/' +  str(self.selector_files.currentText()) + '/csv/')        
        # for dd in history_dirs:
        #     if os.path.isdir(self.mnt_history_path + str(self.selector_pid.currentText()) + '/' +  str(self.selector_files.currentText()) + '/csv/' + dd):
        #         dir_names = dd.split('cham')
        #         if len(dir_names) > 0:
        #             chamber_ids.append(dir_names[1])       
        # for tab in self.embryo_info_array:
        #     tab.SetChamberID(chamber_ids[0])

        #after select remove that one
        

        # self.selector_files.currentText()
        # print('t1 current text',self.selector_files_table1.currentText())
        # print('t2 current text',self.selector_files_table2.currentText())
        # AllItems = [self.selector_files_table1.itemText(i) for i in range(self.selector_files_table1.count())]
        # print('t1 item',AllItems)
        # print('index',self.selector_files_table1.currentIndex())


                    
        #Find history data
        # get_dic = search_history_csv(str(self.selector_pid.currentText()), str(self.selector_files.currentText()))
        # self.InsertInfomationToTable(str(self.selector_pid.currentText()), str(self.selector_files.currentText()), get_dic)    
        # self.button_save.setDisabled(False) 
        
        

        
    def SearchPatientID(self):
        pids_history = []
        history_dirs = os.listdir(self.mnt_history_path)  
        # print('history dir = ',history_dirs)      
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
        # self.selector_files_table1.clear()  
        # self.selector_files_table2.clear()  
        for m in id_time_list:
            self.selector_files.addItem(m)  
            # self.selector_files_table1.addItem(m)  
            # self.selector_files_table2.addItem(m)  
                      
        
    def InsertInfomationToTable(self, patient_id,timelapse_id, date,tabel_index, dict_msg):   


        #Clear all table

        
        
        table = self.embryo_info_array[tabel_index]
        
        table.SetPidDate(patient_id,timelapse_id, date)
        # table.CleanAllText()
        print('tabel index',tabel_index)
        # print('dict msg',dict_msg["DishList"][0].keys())
        dish_number_max = 14
        
        for dish_number in range(dish_number_max+1):
            for dic_dishid in range(len(dict_msg["DishList"])):
                # print('dict_msg["DishList"][dic_dishid]',dict_msg["DishList"][dic_dishid])
                if dict_msg["DishList"][dic_dishid]['DishId']==str(dish_number):
                    

                    if dict_msg["DishList"][dic_dishid]['Info']!={}:
                        print(dict_msg["DishList"][dic_dishid]['Info']['PN_Fading'])
                        self.set_embryo_table_item(table, dish_number+1, 1,dict_msg["DishList"][dic_dishid]['Info']['PN_Fading'] )
                        self.set_embryo_table_item(table, dish_number+1, 2,dict_msg["DishList"][dic_dishid]['Info']['t2'] )
                        self.set_embryo_table_item(table, dish_number+1, 3,dict_msg["DishList"][dic_dishid]['Info']['t3'] )
                        self.set_embryo_table_item(table, dish_number+1, 4,dict_msg["DishList"][dic_dishid]['Info']['t4'] )
                        self.set_embryo_table_item(table, dish_number+1, 5,dict_msg["DishList"][dic_dishid]['Info']['t5'] )
                        self.set_embryo_table_item(table, dish_number+1, 6,dict_msg["DishList"][dic_dishid]['Info']['t6'] )
                        self.set_embryo_table_item(table, dish_number+1, 7,dict_msg["DishList"][dic_dishid]['Info']['t7'] )
                        self.set_embryo_table_item(table, dish_number+1, 8,dict_msg["DishList"][dic_dishid]['Info']['t8'] )
                        self.set_embryo_table_item(table, dish_number+1, 9,dict_msg["DishList"][dic_dishid]['Info']['Morula'] )
                        self.set_embryo_table_item(table, dish_number+1, 10,dict_msg["DishList"][dic_dishid]['Info']['Blas'] )
                    



        # for dish_info in dict_msg["DishList"]:
        #     print(dish_info)
        #     if dish_info['Info']!={}:
        #         print('dish_infoRRRRRRRRR')

        # for table in self.embryo_info_array:
        #     table.SetPidDate(patient_id, date)
        #     for i in range(12):
        #         self.set_embryo_table_item(table, i + 2, 2, '')
        #         self.set_embryo_table_item(table, i + 2, 4, '')
        #     #self.set_embryo_table_item(table, 14, 2, '')
            
        # total_score = 0
        # #{'DishList': [{'DishId': '8', 'Fragment': {}, 'Info': {}}, {'DishId': 2, 'Info': {'Status': 'Discard', 't2': nan, 't3': 9.67, 't4': 11.0, 't5': 18.0, 't6': 20.5, 't7': nan, 't8': 20.83, 'Morula': nan, 'Blas': 21.83, 'comp': nan, 'PN_Fading': 0.0, 'ICM': nan, 'TE': nan, 'PGS': nan, 'Probility': 0.88088155}, 'Fragment': {'pn': 1.5880851063829784, 't2': 3.1957142857142857, 't3': 3.301904761904763, 't4': 3.3818181818181823, 't5': 4.46, 't6': 4.185238095238096, 't7': 3.469166666666667, 't8': 7.082189781021898, 'morula': 8.13, 'blas': 10.843580786026202}}
        # print(dict_msg)
        # print(dict_msg.keys())
        # print(dict_msg["DishList"][0].keys())
        # print(dict_msg["DishList"][0]['Info'])
        # # print(dict_msg['DishList']['Info'])
        # coll_probs = [(dish_info["DishId"], dish_info["Info"]["Probility"]) for dish_info in dict_msg["DishList"] if "Probility" in dish_info["Info"] and dish_info["Info"]["Probility"] != ''] 
        # coll_probs.sort(key=lambda tup: tup[1], reverse=True)            
        
        # for dish_info in dict_msg["DishList"]:    
        #     embryo_tables = [table for table in self.embryo_info_array if int(dish_info["DishId"]) == table.well_id]
        #     if embryo_tables == []:
        #         continue
        #     total_score = 0
        #     count = 0
        #     #print(dish_info)
        #     #t2-t8
        #     for i in range(7):            
        #         #Insert division time
        #         if "Info" in dish_info and 't' + str(i + 2) in dish_info["Info"]:                    
        #             time = str(dish_info["Info"]['t' + str(i + 2)])
        #             self.set_embryo_table_item(embryo_tables[0], i + 3, 2, time)
        #             #print('t' + str(i + 2), embryo_tables[0].well_id, time)
                 
        #         #Insert score
        #         if "Fragment" in dish_info and 't' + str(i + 2) in dish_info["Fragment"]:
        #             try:
        #                 value = int(100 - (4 * (math.ceil(dish_info["Fragment"]['t' + str(i + 2)] * 100) / 100)))
        #                 if value < 0:
        #                     value = 0 
        #                 self.set_embryo_table_item(embryo_tables[0], i + 3, 4, str(value), True)
        #                 count += 1
        #                 total_score = total_score + value
        #             except:
        #                 self.set_embryo_table_item(embryo_tables[0], i + 3, 4, '', True)                                                 
            
        #     #Final score                 
        #     if total_score > 0:
        #         average_score = str(int((float(total_score) / float(count)) * 100) / 100)
        #         # self.set_embryo_table_item(embryo_tables[0], 14, 2, average_score, True) #1230 change 
        #     if "Probility" in dish_info["Info"]:
        #         orders = [i+1 for i,e in enumerate(coll_probs) if e[0] == dish_info["DishId"]]
        #         if orders != []:    
        #             content =  str(int(100 * dish_info["Info"]["Probility"])) + ' (' + str(orders[0]) + '/' + str(len(coll_probs)) + ')'
        #         else:
        #             content =  str(int(100 * dish_info["Info"]["Probility"]))                       
        #         self.set_embryo_table_item(embryo_tables[0], 14, 2, content, True)
        #     else:
        #         self.set_embryo_table_item(embryo_tables[0], 14, 2, '', True)
                
        #     #molura, blas.,             
        #     if "Info" in dish_info and dish_info["Info"] != {}:
        #         print (dish_info)
        #         self.set_embryo_table_item(embryo_tables[0], 10, 2, str(dish_info["Info"]["Morula"]))
        #         self.set_embryo_table_item(embryo_tables[0], 11, 2, str(dish_info["Info"]["Blas"]))                   
        #         self.set_embryo_table_item(embryo_tables[0], 2, 2, str(dish_info["Info"]["PN_Fading"]))  
        #     #Molura score
        #     if "Fragment" in dish_info and 'morula' in dish_info["Fragment"]:
        #         try:
        #             value = int(100 - (4 * (math.ceil(dish_info["Fragment"]['morula'] * 100) / 100)))
        #             if value < 0:
        #                 value = 0 
        #             self.set_embryo_table_item(embryo_tables[0], 10, 4, str(value), True)
        #         except:
        #             self.set_embryo_table_item(embryo_tables[0], 10, 4, '', True)    
        #     #pn score
        #     if "Fragment" in dish_info and 'pn' in dish_info["Fragment"]:
        #         try:
        #             value = int(100 - (4 * (math.ceil(dish_info["Fragment"]['pn'] * 100) / 100)))
        #             if value < 0:
        #                 value = 0 
        #             self.set_embryo_table_item(embryo_tables[0], 2, 4, str(value), True)
        #         except:
        #             self.set_embryo_table_item(embryo_tables[0], 2, 4, '', True)    
              
        #     #Icm, te, decision, pgs
        #     embryo_tables[0].SetIcmTe()
        #     if "Info" in dish_info and dish_info["Info"] != {}:
        #         embryo_tables[0].setDecision(dish_info["Info"]["Status"],  dish_info["Info"]["Probility"])
        #         embryo_tables[0].setPGS(dish_info["Info"]["PGS"])                      
                    
        #     #Read event file
        #     file_path = './' + 'event_info_' + patient_id + '_' + str(embryo_tables[0].well_id) + '.txt'
        #     text = ''
        #     if os.path.exists(file_path):
        #         with open(file_path, 'r') as f:
        #             text = f.read() 
        #     print (file_path)
        #     print(text)
        #     self.set_embryo_table_item(embryo_tables[0], 13, 2, str(text))
                    
                    
    def set_embryo_table_item(self, table, row, col, value, readonly=False):
        if str(value).lower() != 'nan':
            table.SetItem(row, col, value, readonly)        
        
    def SaveTableChangeToFile(self):       
        for i,table in enumerate(self.embryo_info_array):
            if i < self.well_number:
                table.SaveChangeItem()
               





#video player function use part --------------------------------------------------------

    def keyPressEvent(self, event):    
        position = self.position_val
        if event.key() == QtCore.Qt.Key_Left:
            position = self.position_val - 1000/6
        if event.key() == QtCore.Qt.Key_Right:
            position = self.position_val + 1000/6
        self.positionChanged(position)
        self.setPosition(position)
       
    #Search file to show    
    def initSelector(self):
        #self.logger.info(self.Directory + pid)        
        folders = [f for f in os.listdir('./') if os.path.isdir(f)]
        folders.sort()                 
        self.selector_folder.clear()
        for f in folders:
            self.selector_folder.addItem(f)        
        
    #Set video source    
    def initSource(self, pid, chid, wid):
        self.LoadEmbryoDataPnNew(pid, chid, wid)
        #img_to_video(chid, wid)
        
        path = os.path.abspath(load_video_path_with_7fp(pid, chid, wid, int(str(self.selector_fp.currentText())) - 1))
        #path = os.path.abspath('./video/MTL-0245-11FD-1774/cham1/dish10/MTL-0245-11FD-1774_cham1_dish10_FP0.avi')
        
        if not path:
            return
        self.playButton.setEnabled(True)
        #print(path)
        self.player.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(path)))
        
        self.patient_id = str(pid)
        self.chamber_id = str(chid)
        self.well_id = str(wid)
        


    
    #Play video
    def play(self):               
        if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()
            
    def mediaStateChanged(self, state):        
        if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.playButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPause))            
        else:
            self.playButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
    
    #Video position                
    def positionChanged(self, position):
        self.slider.setValue(position)
        self.position_val = position
      
    def durationChanged(self, duration):
        self.slider.setRange(0, duration)    
        self.slider.setTickInterval(1000/6)     
        self.slider.setSingleStep(1000/6)   

    def setPosition(self, position):
        self.player.setPosition(position)            
                
    
    def handleError(self):
        #self.playButton.setEnabled(False)
        #self.errorLabel.setText("Error: " + self.player.errorString())
        print("Error: " + self.player.errorString())    
    
                    
        