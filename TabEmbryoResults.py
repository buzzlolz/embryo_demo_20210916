# -*- coding: utf-8 -*-
"""
Created on Fri May 29 16:41:09 2020

@author: minghung
"""

import os, math
from PyQt5 import QtCore, QtWidgets, QtGui 
from PyQt5 import QtMultimedia, QtMultimediaWidgets
        
#from PlotCanvas import PlotCanvas
from EmbryoBoxInfo import EmbryoImageLabel, EmbryoInfoTable
from Ui_Function import * 


class TabEmbryoResults(QtWidgets.QWidget):
    def __init__(self, logger, tab_machine, parent=None):
        super(TabEmbryoResults, self).__init__(parent=parent)
        self.logger = logger
        self.tab_machine = tab_machine       
        _, self.grade_parameters = self.tab_machine.ReadMachineConfig()
        self.position_val = 0
        
        self.patient_id = ''
        self.chamber_id = ''
        self.well_id = ''
                 
        self.initUI()
              
    def initUI(self):        
        #infomation
        label_info = QtWidgets.QLabel('Information:')
        label_info.setFont(QtGui.QFont('Arial', 14))
        label_info.setFixedHeight(20)
        #label_info.setGeometry(230, 160, 30, 30)
        
        self.edit_info = QtWidgets.QPlainTextEdit()
        #self.edit_info.setGeometry(260, 160, 30, 30)
        self.edit_info.setStyleSheet('background-color:white; font-size:16pt') 
        #self.edit_info.setAlignment(QtCore.Qt.AlignRight)
        self.edit_info.insertPlainText('Overall Scoring: 0\n')
        self.edit_info.insertPlainText('Event:\n')
        self.edit_info.setFixedSize(700, 170)
        self.edit_info.setFocusPolicy(QtCore.Qt.ClickFocus) 
        self.edit_info.textChanged.connect(self.edit_info_changed)               
        
        #Video frame
        label_video = QtWidgets.QLabel('Video:')
        label_video.setFont(QtGui.QFont('Arial', 12))
        label_video.setFixedHeight(20)
        self.frame_video = QtWidgets.QFrame(self)        
        self.frame_video.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_video.setFixedSize(QtCore.QSize(700, 600))  
        self.frame_video.setStyleSheet('background-color:white;')
               
        self.player = QtMultimedia.QMediaPlayer(self.frame_video)
        self.viewer = QtMultimediaWidgets.QVideoWidget(self.frame_video)   
        #self.viewer.setMaximumSize(QtCore.QSize(600, 400))
        self.player.setVideoOutput(self.viewer)        
        
        layout_video = QtWidgets.QGridLayout(self.frame_video)        
        layout_video.addWidget(self.viewer, 0, 0, 1, 2)
       
        self.playButton = QtWidgets.QPushButton()
        self.playButton.setFixedSize(50, 40)
        self.playButton.setStyleSheet('background-color:lightblue;border-radius: 5px;')       
        self.playButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)
        
        self.selector_fp = QtWidgets.QComboBox(self)   
        self.selector_fp.setFixedSize(40, 40)      
        self.selector_fp.setStyleSheet("background-color:white;selection-background-color: darkblue")           
        for i in range(7):
            self.selector_fp.addItem(str(i + 1))
        self.selector_fp.setCurrentIndex(4) 
        self.selector_fp.currentIndexChanged.connect(lambda: self.initSource(self.patient_id, self.chamber_id, self.well_id))
        
        self.slider = QtWidgets.QSlider(self)        
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setObjectName("horizontalSlider")
        self.slider.setFixedWidth(580)        
        self.slider.sliderMoved.connect(self.setPosition) 
        self.slider.valueChanged.connect(self.setPosition) 
        self.slider.setFocus()  #valueChanged[int].connect(self.changeValue)   
        self.slider.setFocusPolicy(QtCore.Qt.StrongFocus)    
       
        self.player.stateChanged.connect(self.mediaStateChanged)
        self.player.positionChanged.connect(self.positionChanged)
        self.player.durationChanged.connect(self.durationChanged)
        self.player.error.connect(self.handleError)        
        
        #Image show frame        
        label_table_left = QtWidgets.QLabel('Stage 1:')
        label_table_left.setFont(QtGui.QFont('Arial', 12))
        label_table_left.setFixedHeight(25)
        label_table_right = QtWidgets.QLabel('Stage 2:')
        label_table_right.setFont(QtGui.QFont('Arial', 12))
        label_table_right.setFixedHeight(25)
        self.table_img_left = EmbryoInfoTable(5, 4, ['2pn', '2cell', '3cell', '4cell', '5cell'], self)
        self.table_img_left.setFixedSize(QtCore.QSize(420, 850))   
        self.table_img_left.setFocusPolicy(QtCore.Qt.ClickFocus) 
        self.table_img_right = EmbryoInfoTable(5, 4, ['6cell', '7cell', '8cell', 'Morula', 'Blastocyst'], self)
        self.table_img_right.setGeometry(1155, 40, 420, 850)
        self.table_img_right.setFocusPolicy(QtCore.Qt.ClickFocus) 
        
        layout = QtWidgets.QGridLayout(self) 
        layout.addWidget(label_table_left, 0, 0, 1, 2, QtCore.Qt.AlignHCenter)  
        layout.addWidget(self.table_img_left, 1, 0, 10, 2, QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        layout.addWidget(label_video, 0, 2, 1, 4, QtCore.Qt.AlignHCenter)        
        layout.addWidget(self.frame_video, 1, 2, 6, 4, QtCore.Qt.AlignLeft)#HCenter)
        layout.addWidget(self.playButton, 7, 2, 1, 1)          
        layout.addWidget(self.selector_fp, 7, 3, 1, 1) 
        layout.addWidget(self.slider, 7, 4, 1, 2)
        layout.addWidget(label_table_right, 0, 6, 1, 2, QtCore.Qt.AlignHCenter)
        #layout.addWidget(self.table_img_right, 1, 6, 10, 2, QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        layout.addWidget(label_info, 8, 2, 1, 4, QtCore.Qt.AlignHCenter)
        layout.addWidget(self.edit_info, 9, 2, 1, 4)
    
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
        self.LoadEmbryoData(pid, chid, wid)
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
                
    def edit_info_changed(self):
        content = self.edit_info.toPlainText()
        lines = content.split('\n')
        if len(lines) < 2 or self.patient_id == '' or self.well_id == '':
            return
            
        text = []
        if 'Event:' in lines[1]:
            text.append(lines[1].split('Event:')[1])
        for i in range(len(lines)):
            if i > 1:
                text.append(lines[i])
        print (text)        
        with open('event_info_' + self.patient_id + '_' + self.well_id + '.txt', 'w') as f:
            f.write(' '.join(text))        

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
     
    def LoadEmbryoData(self, patient_id, chamber_id, dish_id):
        print ('LoadEmbryoData')
        #_, filename_dic, timespend_dic, percent_dic = get_each_stage_result(chid, wid)
         
        #{'Xlsx': {'pn': 7.469999999999999, 't2': 9.629999999999999, 't3': 25.129999999999995, 't4': 26.129999999999995, 't5': 42.47, 't6': 44.129999999999995, 't7': 45.300000000000004, 't8': 51.300000000000004, 'morula': 83.46000000000001, 'blas': nan}, 'Predict': {'pn': 0.0, 't2': 5.83, 't3': 20.67, 't4': 22.33, 't5': nan, 't6': 33.0, 't7': 47.5, 't8': 48.33, 'morula': 76.17, 'blas': 79.17, 'comp': nan}, 'Fragment': {'pn': 0.5311904761904762, 't2': 1.1187142857142856, 't3': 3.8090625, 't4': 1.9507042253521132, 't5': 3.500714285714285, 't6': 1.88358024691358, 't7': 2.2823333333333333, 't8': 2.1847499999999997, 'morula': 1.927297297297297, 'blas': 2.9246296296296292}, 'Cham_id': '6', 'Dish_id': '5', 'Patient_id': 'MTL-0245-13A1-9874', 'Dict_key': ['pn', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 'morula', 'blas']}
        dict_msg = get_xlsx_predict_division_time(patient_id, chamber_id, dish_id)
        print(dict_msg)
        total_score = 0
        count = 0   
        
        #Left table               
        for n in range(5):
            #Analysis            
            grade = '-'
            score = '-'
            time = '-'
            #Find grade time
            if n == 0:
                if "pn" in dict_msg["Predict"] and str(dict_msg["Predict"]["pn"]) != 'nan' and str(dict_msg["Predict"]["pn"]) != 'NaN' and self.intTryParse(dict_msg["Predict"]["pn"]):
                    time = str(int(dict_msg["Predict"]["pn"] * 100.0) / 100.0) 
                if "pn" in dict_msg["Fragment"] and str(dict_msg["Fragment"]["pn"]) != 'nan' and str(dict_msg["Fragment"]["pn"]) != 'NaN' and self.intTryParse(dict_msg["Fragment"]["pn"]):  
                    grade = self.MapGradeValue(int(dict_msg["Fragment"]["pn"]))
                    score = 100 - (4 * int(dict_msg["Fragment"]["pn"]))
                print('score',score)                 
                if score != '-':
                    total_score = total_score + score
                    count += 1
            if n >= 1:
                if 't' + str(n + 1) in dict_msg["Predict"] and str(dict_msg["Predict"]['t' + str(n + 1)]) != 'nan' and str(dict_msg["Predict"]['t' + str(n + 1)]) != 'NaN' and self.intTryParse(dict_msg["Predict"]['t' + str(n + 1)]):
                    time = str(int(dict_msg["Predict"]['t' + str(n + 1)] * 100.0) / 100.0)  
                if 't' + str(n + 1) in dict_msg["Fragment"] and str(dict_msg["Fragment"]['t' + str(n + 1)]) != 'nan' and str(dict_msg["Fragment"]['t' + str(n + 1)]) != 'NaN' and self.intTryParse(dict_msg["Fragment"]['t' + str(n + 1)]):  
                    grade = self.MapGradeValue(math.ceil(dict_msg["Fragment"]['t' + str(n + 1)]))
                    score = 100 - (4 * math.ceil(dict_msg["Fragment"]['t' + str(n + 1)]))               
                if score != '-':
                    total_score = total_score + score
                    count += 1            
            label_l_analysis = EmbryoImageLabel(150, 150, [str(grade), str(time), str(score)]) 
            
            #View              
            time = '-'
            #Find grade time
            if n == 0 and "pn" in dict_msg["Xlsx"] and str(dict_msg["Xlsx"]["pn"]) != 'nan' and str(dict_msg["Xlsx"]["pn"]) != 'NaN' and self.intTryParse(dict_msg["Xlsx"]["pn"]):
                time = str(int(dict_msg["Xlsx"]["pn"] * 100.0) / 100.0)                
            if n >= 1 and 't' + str(n + 1) in dict_msg["Xlsx"] and str(dict_msg["Xlsx"]['t' + str(n + 1)]) != 'nan' and str(dict_msg["Xlsx"]['t' + str(n + 1)]) != 'NaN' and self.intTryParse(dict_msg["Xlsx"]['t' + str(n + 1)]):   
                time = str(int(dict_msg["Xlsx"]['t' + str(n + 1)] * 100.0) / 100.0)                                     
            label_l_view = EmbryoImageLabel(150, 150, ['-', str(time), '-'])   
            
            #Insert data      
            self.table_img_left.AddRow(n, label_l_analysis, label_l_view)  
                         
        #Right table
        for n in range(5):
            grade = '-'   
            score = '-'
            time = '-'            
            #Find grade time            
            if n < 3: 
                if 't' + str(n + 6) in dict_msg["Predict"] and str(dict_msg["Predict"]['t' + str(n + 6)]) != 'nan' and str(dict_msg["Predict"]['t' + str(n + 6)]) != 'NaN' and self.intTryParse(dict_msg["Predict"]['t' + str(n + 6)]):
                    time = str(int(dict_msg["Predict"]['t' + str(n + 6)] * 100.0) / 100.0)                    
                if 't' + str(n + 6) in dict_msg["Fragment"] and str(dict_msg["Fragment"]['t' + str(n + 6)]) != 'nan' and str(dict_msg["Fragment"]['t' + str(n + 6)]) != 'NaN' and self.intTryParse(dict_msg["Fragment"]['t' + str(n + 6)]):
                    grade = self.MapGradeValue(math.ceil(dict_msg["Fragment"]['t' + str(n + 6)]))
                    score = 100 - (4 * math.ceil(dict_msg["Fragment"]['t' + str(n + 6)]))                
                if score != '-':
                    total_score = total_score + score
                    count += 1
                    
            if n == 3:
                if "morula" in dict_msg["Predict"] and str(dict_msg["Predict"]["morula"]) != 'nan' and str(dict_msg["Predict"]["morula"]) != 'NaN' and self.intTryParse(dict_msg["Predict"]["morula"]):                             
                    time = str(int(dict_msg["Predict"]["morula"] * 100.0) / 100.0)
                if "morula" in dict_msg["Fragment"] and str(dict_msg["Fragment"]["morula"]) != 'nan' and str(dict_msg["Fragment"]["morula"]) != 'NaN' and self.intTryParse(dict_msg["Fragment"]["morula"]):       
                    grade = self.MapGradeValue(math.ceil(dict_msg["Fragment"]["morula"]))
                    score = 100 - (4 * math.ceil(dict_msg["Fragment"]["morula"]))
                   
            if n == 4:
                if "blas" in dict_msg["Predict"] and str(dict_msg["Predict"]["blas"]) != 'nan' and str(dict_msg["Predict"]["blas"]) != 'NaN' and self.intTryParse(dict_msg["Predict"]["blas"]):                                       
                    time = str(int(dict_msg["Predict"]["blas"] * 100.0) / 100.0)
                                       
            #View           
            time_ = '-'
            #Find grade time
            if n < 3: 
                if 't' + str(n + 6) in dict_msg["Xlsx"] and str(dict_msg["Xlsx"]['t' + str(n + 6)]) != 'nan' and str(dict_msg["Xlsx"]['t' + str(n + 6)]) != 'NaN' and self.intTryParse(dict_msg["Xlsx"]['t' + str(n + 6)]):                
                    time_ = str(int(dict_msg["Xlsx"]['t' + str(n + 6)] * 100.0) / 100.0)
                                    
            if n == 3:
                if "morula" in dict_msg["Xlsx"] and str(dict_msg["Xlsx"]["morula"]) != 'nan' and str(dict_msg["Xlsx"]["morula"]) != 'NaN' and self.intTryParse(dict_msg["Xlsx"]["morula"]):
                    time_ = str(int(dict_msg["Xlsx"]["morula"] * 100.0) / 100.0)
                   
            if n == 4:
                if "blas" in dict_msg["Xlsx"] and str(dict_msg["Xlsx"]["blas"]) != 'nan' and str(dict_msg["Xlsx"]["blas"]) != 'NaN' and self.intTryParse(dict_msg["Xlsx"]["blas"]):                                 
                    time_ = str(int(dict_msg["Xlsx"]["blas"] * 100.0) / 100.0)
                                             
                  
            #Insert data 
            self.table_img_right.SetChamberIdPid(chamber_id, dish_id)
            if n < 4:
                label_r_view = EmbryoImageLabel(150, 150, ['-', str(time_), '-'])
                label_r_analysis = EmbryoImageLabel(150, 150, [str(grade), str(time), str(score)])                           
            else:
                label_r_view = EmbryoImageLabel(150, 150, [str(time_), '-', '-'])
                label_r_analysis = EmbryoImageLabel(150, 150, [str(time), "ICM", "TE"])
            self.table_img_right.AddRow(n, label_r_analysis, label_r_view) 
                        
        #Insert info data
        if count != 0:
            val = str(int((float(total_score) / float(count)) * 100) / 100)
        else:
            val = 0
                
        self.edit_info.clear()
        self.edit_info.insertPlainText('Overall Scoring: {}\n'.format(val))
        self.edit_info.insertPlainText('Event:')
      
    #Vdeo player error  
    def handleError(self):
        #self.playButton.setEnabled(False)
        #self.errorLabel.setText("Error: " + self.player.errorString())
        print("Error: " + self.player.errorString())        
        
    def MapGradeValue(self, val):       
        if str(val) == 'nan' or str(val) == 'NaN':
            return 0
                     
        grade_std = []
        for i in range(5):
            if "grade" + str(i + 1) in self.grade_parameters:
                grade_std.append(int(self.grade_parameters["grade" + str(i + 1)]))
        final_grade = 1      
        val = int(100 - (4 * (math.ceil(val * 100) / 100)))   
        if val < 0:
            val = 0                       
        for i in range(len(grade_std)):
            idx = len(grade_std) - i - 1
            if val >= grade_std[idx]:
                final_grade = idx + 1
                
        return final_grade
        
    def intTryParse(self, value):
        try:
            int(value)
            return True
        except ValueError:
            return False
       
    
        
        
