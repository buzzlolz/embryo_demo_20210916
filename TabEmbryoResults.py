
  
# -*- coding: utf-8 -*-
"""
Created on Fri May 29 16:41:09 2020
@author: minghung
"""

import os, math
from PyQt5 import QtCore, QtWidgets, QtGui 
from PyQt5 import QtMultimedia, QtMultimediaWidgets
        
#from PlotCanvas import PlotCanvas
from EmbryoBoxInfo import EmbryoImageLabel,EmbryoNewInfoTable,EmbryoPnTable,EmbryoBlasTable,EmbryoTotalScoreTable,EmbryoSelectDishTable
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

        # self.well_number = 14

        self.divisionTime_avg_success=[25.67,36.4,39.02,51.17,55.64,59.21,67.63,90.86,112.6]
        self.divisionTime_avg_false = [27.16,38.09,41.67,55.14,58.05,62.21,71.81,93.52,112.24]
        self.ReadScorePercentIniFile()
        self.initUI()
              
    def initUI(self):        



        

        self.table_pn = EmbryoPnTable(1, 5, ['pn_Fading'], self)
        self.table_pn.setFocusPolicy(QtCore.Qt.ClickFocus) 
        self.table_pn.setGeometry(800,10,702,87)   


        #save sheet manual row information
        self.manual_info_save_Button = QtWidgets.QPushButton('Update Info', self)
        # self.playButton.setFixedSize(50, 40)
        # self.manual_info_save_Button.setStyleSheet('background-color:lightblue;border-radius: 5px;')   
        self.manual_info_save_Button.setStyleSheet('QPushButton {background-color:#1991e0;border-radius: 20px;}  QPushButton:hover{color:black;background:bisque;} QPushButton:pressed {background:lightcoral}')
            
        # self.manual_info_save_Button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        self.manual_info_save_Button.clicked.connect(lambda: self.EmbryoViewerInfoSave())
        self.manual_info_save_Button.setGeometry(1540,30,170,40)


        self.frame_video = QtWidgets.QFrame(self)        
        self.frame_video.setFrameShape(QtWidgets.QFrame.StyledPanel)
        # self.frame_video.setFixedSize(QtCore.QSize(700, 630))  
        self.frame_video.setStyleSheet('background-color:white;')
        self.frame_video.setGeometry(50,10,700,630)
               
        self.player = QtMultimedia.QMediaPlayer(self.frame_video)
        
        self.viewer = QtMultimediaWidgets.QVideoWidget(self.frame_video)   
        #self.viewer.setMaximumSize(QtCore.QSize(600, 400))
        self.player.setVideoOutput(self.viewer)     
        self.viewer.setGeometry(50,0,700,630)   
        
        # layout_video = QtWidgets.QGridLayout(self.frame_video)        
        # layout_video.addWidget(self.viewer, 0, 0, 1, 2)
       
        self.playButton = QtWidgets.QPushButton(self)
        # self.playButton.setFixedSize(50, 40)
        self.playButton.setStyleSheet('background-color:lightblue;border-radius: 5px;')       
        self.playButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)
        self.playButton.setGeometry(50,650,50,40)


        

          
        
        self.selector_fp = QtWidgets.QComboBox(self)   
        self.selector_fp.setFixedSize(40, 40)      
        self.selector_fp.setStyleSheet("background-color:white;selection-background-color: darkblue")           
        for i in range(7):
            self.selector_fp.addItem(str(i + 1))
        self.selector_fp.setCurrentIndex(4) 
        self.selector_fp.currentIndexChanged.connect(lambda: self.initSource(self.patient_id, self.chamber_id, self.well_id))
        self.selector_fp.setGeometry(120,650,30,30)


        self.slider = QtWidgets.QSlider(self)        
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setObjectName("horizontalSlider")
        self.slider.setFixedWidth(580)        
        self.slider.sliderMoved.connect(self.setPosition) 
        self.slider.valueChanged.connect(self.setPosition) 
        self.slider.setFocus()  #valueChanged[int].connect(self.changeValue)   
        self.slider.setFocusPolicy(QtCore.Qt.StrongFocus)  
        self.slider.setGeometry(170,660,30,30)  
       
        self.player.setNotifyInterval(int(1000/6))
        self.player.stateChanged.connect(self.mediaStateChanged)
        self.player.positionChanged.connect(self.positionChanged)
        self.player.durationChanged.connect(self.durationChanged)
        self.player.error.connect(self.handleError)     


        

        self.video_time_show = QtWidgets.QLabel(self)        
        self.video_time_show.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.video_time_show.setFont(QtGui.QFont('Arial', 16))
        # self.frame_video.setFixedSize(QtCore.QSize(700, 630))  
        self.video_time_show.setStyleSheet('background-color:white;')
        self.video_time_show.setGeometry(650,600,100,40)
        
        
        # t2-t8 table
        self.table_img_left = EmbryoNewInfoTable(7, 7, ['2cell', '3cell', '4cell', '5cell','6cell', '7cell', '8cell'], self)
        self.table_img_left.setFocusPolicy(QtCore.Qt.ClickFocus) 
        self.table_img_left.setGeometry(800,109,702,418)

        # morula blas table
        self.table_blas_info = EmbryoBlasTable(2, 4, ['Morula','Blas'], self)
        self.table_blas_info.setFocusPolicy(QtCore.Qt.ClickFocus) 
        self.table_blas_info.setGeometry(800,530,702,143)


        #know which dish select table 
        self.table_dish_selected = EmbryoSelectDishTable(7,2,self)
        self.table_dish_selected.setFocusPolicy(QtCore.Qt.ClickFocus) 
        self.table_dish_selected.setGeometry(1540,250,122,242)
        self.table_dish_selected.doubleClicked.connect(self.DoubleClickSelectWell)


        # total score table
        self.table_total_score_info = EmbryoTotalScoreTable(1, 2, self)
        self.table_total_score_info.setFocusPolicy(QtCore.Qt.ClickFocus) 
        self.table_total_score_info.setGeometry(1540,530,202,92)




        #pn option radio buttons -------------------

        self.qframe_pn= QtWidgets.QFrame(self)      
        self.qframe_pn.setGeometry(45, 710, 605, 65)
        self.qframe_pn.setFrameShape(QtWidgets.QFrame.Box) 
        
        self.qframe_pn.setFrameShadow(QtWidgets.QFrame.Sunken) 



        label_combobox_pn = QtWidgets.QLabel('PN :',self.qframe_pn)
        label_combobox_pn.setFont(QtGui.QFont('Arial', 14,QtGui.QFont.Bold))
        label_combobox_pn.setFixedHeight(20)
        label_combobox_pn.setGeometry(5, 5, 150, 25)

        self.combobox_pn_choices = ['NPN', '1PN','2PN', '3PN', 'Poly-PN']
        

        self.qradio_pn_choices = []

        for i in range(len(self.combobox_pn_choices)):
            self.qradio_pn_choices.append(QtWidgets.QRadioButton('%s' %self.combobox_pn_choices[i],self.qframe_pn))

        for i in range(5):
             self.qradio_pn_choices[i].setGeometry(5+i*120, 30, 100, 30)
             self.qradio_pn_choices[i].setStyleSheet('font-size:18px;')
        
        
        self.qradio_pn_group = QtWidgets.QButtonGroup(self)
        
        for qradio in self.qradio_pn_choices:
            self.qradio_pn_group.addButton(qradio)

        




        #pn radio buttons -------------------
        


        #location option radio buttons ------------------------

        self.qframe_location= QtWidgets.QFrame(self)      
        self.qframe_location.setGeometry(45, 780, 605, 65)
        self.qframe_location.setFrameShape(QtWidgets.QFrame.Box) 
        
        self.qframe_location.setFrameShadow(QtWidgets.QFrame.Sunken) 

        label_combobox_location = QtWidgets.QLabel('Location:',self.qframe_location)
        label_combobox_location.setFont(QtGui.QFont('Arial', 14,QtGui.QFont.Bold))
        label_combobox_location.setFixedHeight(20)
        label_combobox_location.setGeometry(5, 5, 150, 20)
        self.combobox_location_choices = ['Central', 'Central/Side', 'Side']
        

        self.qradio_location_choices = []

        for i in range(len(self.combobox_location_choices)):
            self.qradio_location_choices.append(QtWidgets.QRadioButton('%s' %self.combobox_location_choices[i],self.qframe_location))

        for i in range(3):
             self.qradio_location_choices[i].setGeometry(5+i*150, 30, 150, 30)
             self.qradio_location_choices[i].setStyleSheet('font-size:18px;')
        
        
        self.qradio_location_group = QtWidgets.QButtonGroup(self)
        
        for qradio in self.qradio_location_choices:
            self.qradio_location_group.addButton(qradio)

        #location option radio buttons ------------------------



        #morphological option chekcbox buttons ------------------------

        self.qframe_morphological= QtWidgets.QFrame(self)      
        self.qframe_morphological.setGeometry(45, 850, 605, 95)
        self.qframe_morphological.setFrameShape(QtWidgets.QFrame.Box) 
        self.qframe_morphological.setFrameShadow(QtWidgets.QFrame.Sunken) 

        label_combobox_morphological = QtWidgets.QLabel('Morphological:',self.qframe_morphological)
        label_combobox_morphological.setFont(QtGui.QFont('Arial', 14,QtGui.QFont.Bold))
        label_combobox_morphological.setFixedHeight(20)
        label_combobox_morphological.setGeometry(5, 5, 180, 25)


        

        self.combobox_morphological_choices = ['Refractile Body', 'Central Darkness','Abnormality','Large pb']
         
        self.qradio_morphological_choices = []

        for i in range(len(self.combobox_morphological_choices)):
            self.qradio_morphological_choices.append(QtWidgets.QCheckBox('%s' %self.combobox_morphological_choices[i],self.qframe_morphological))

        for i in range(4):
             self.qradio_morphological_choices[i].setGeometry(5+i*250, 35, 250, 25)
             self.qradio_morphological_choices[i].setStyleSheet('font-size:18px;')
        for i in range(2,len(self.combobox_morphological_choices)):
             self.qradio_morphological_choices[i].setGeometry(5+(i-2)*250, 65, 250, 25)
             self.qradio_morphological_choices[i].setStyleSheet('font-size:18px;')
        
        #morphological option chekcbox buttons ------------------------


        
        #divisiontime option chekcbox buttons ------------------------

        self.qframe_divisiontime= QtWidgets.QFrame(self)      
        self.qframe_divisiontime.setGeometry(795, 710, 780, 85)
        self.qframe_divisiontime.setFrameShape(QtWidgets.QFrame.Box) 
        self.qframe_divisiontime.setFrameShadow(QtWidgets.QFrame.Sunken) 



        label_combobox_divisiontime = QtWidgets.QLabel('Division_time :',self.qframe_divisiontime)
        label_combobox_divisiontime.setFont(QtGui.QFont('Arial', 14,QtGui.QFont.Bold))
        label_combobox_divisiontime.setFixedHeight(20)
        label_combobox_divisiontime.setGeometry(5, 5, 180, 20)


        

        self.combobox_divisiontime_choices = ['Asymmetry', 'Multinucleation', 'Reverse Cleavage', 'Direct Uneven Cleavage','Vacuolated','Chaos']
         
        self.qradio_divisiontime_choices = []

        for i in range(len(self.combobox_divisiontime_choices)):
            self.qradio_divisiontime_choices.append(QtWidgets.QCheckBox('%s' %self.combobox_divisiontime_choices[i],self.qframe_divisiontime))

        for i in range(4):
             self.qradio_divisiontime_choices[i].setGeometry(5+i*180, 30, 220, 20)
             self.qradio_divisiontime_choices[i].setStyleSheet('font-size:18px;')
        for i in range(4,len(self.combobox_divisiontime_choices)):
             self.qradio_divisiontime_choices[i].setGeometry(5+(i-4)*180, 60, 180, 20)
             self.qradio_divisiontime_choices[i].setStyleSheet('font-size:18px;')
        
        #divisiontime option chekcbox buttons ------------------------




        #ICM option radio buttons ------------------------

        self.qframe_ICM= QtWidgets.QFrame(self)      
        self.qframe_ICM.setGeometry(795, 810, 460, 75)
        self.qframe_ICM.setFrameShape(QtWidgets.QFrame.Box) 
        self.qframe_ICM.setFrameShadow(QtWidgets.QFrame.Sunken) 

        label_combobox_ICM = QtWidgets.QLabel('ICM:',self.qframe_ICM)
        label_combobox_ICM.setFont(QtGui.QFont('Arial', 14,QtGui.QFont.Bold))
        label_combobox_ICM.setFixedHeight(20)
        label_combobox_ICM.setGeometry(5, 5, 150, 20)
        self.combobox_ICM_TE_choices = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-']
        # self.combobox_pn.addItems(combobox_pn_choices)
        # self.combobox_pn.setGeometry(10, 800, 150, 30)

        self.qradio_ICM_choices = []

        for i in range(len(self.combobox_ICM_TE_choices)):
            self.qradio_ICM_choices.append(QtWidgets.QRadioButton('%s' %self.combobox_ICM_TE_choices[i],self.qframe_ICM))

        for i in range(len(self.combobox_ICM_TE_choices)):
            
            self.qradio_ICM_choices[i].setGeometry(5+i*50, 30, 50, 30)
            self.qradio_ICM_choices[i].setStyleSheet('font-size:18px;')
        
        
        self.qradio_ICM_group = QtWidgets.QButtonGroup(self)
        
        for qradio in self.qradio_ICM_choices:
            self.qradio_ICM_group.addButton(qradio)

        #ICM  option radio buttons ------------------------
        



        #TE option radio buttons ------------------------


        self.qframe_TE= QtWidgets.QFrame(self)      
        self.qframe_TE.setGeometry(795, 895, 460, 75)
        self.qframe_TE.setFrameShape(QtWidgets.QFrame.Box) 
        self.qframe_TE.setFrameShadow(QtWidgets.QFrame.Sunken) 

        label_combobox_TE = QtWidgets.QLabel('TE:',self.qframe_TE)
        label_combobox_TE.setFont(QtGui.QFont('Arial', 14,QtGui.QFont.Bold))
        label_combobox_TE.setFixedHeight(20)
        label_combobox_TE.setGeometry(5, 5, 150, 20)
        # combobox_ICM_TE_choices = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-']
        # self.combobox_pn.addItems(combobox_pn_choices)
        # self.combobox_pn.setGeometry(10, 800, 150, 30)

        self.qradio_TE_choices = []

        for i in range(len(self.combobox_ICM_TE_choices)):
            self.qradio_TE_choices.append(QtWidgets.QRadioButton('%s' %self.combobox_ICM_TE_choices[i],self.qframe_TE))

        for i in range(len(self.combobox_ICM_TE_choices)):
             self.qradio_TE_choices[i].setGeometry(5+i*50, 30, 50, 30)
             self.qradio_TE_choices[i].setStyleSheet('font-size:18px;')
        
        
        self.qradio_TE_group = QtWidgets.QButtonGroup(self)
        
        for qradio in self.qradio_TE_choices:
            self.qradio_TE_group.addButton(qradio)




        
        #ICM  option radio buttons ------------------------
    

        # qbutton_offline = QtWidgets.QRadioButton('offline',self)
        # qbutton_offline.setGeometry(300, 0, 150, 20) 
        # qbutton_offline.setFont(QtGui.QFont('Arial', 12))
        # qbutton_offline.toggled.connect(lambda:self.ClickSetmanualCheckbox(True))


        


        # qbutton_pn_group = QtWidgets.QButtonGroup(self)
        # qbutton_pn_group.addButton(qbutton_online, 1)
        # qbutton_pn_group.addButton(qbutton_offline, 2)

        
        # label_combobox_divisiontime = QtWidgets.QLabel('division_time class:',self)
        # label_combobox_divisiontime.setFont(QtGui.QFont('Arial', 14))
        # label_combobox_divisiontime.setFixedHeight(20)
        # # label_combobox_divisiontime.setGeometry(10, 850, 180, 30)
        # # label_combobox_divisiontime.setGeometry(10, 800, 150, 30)
        # self.combobox_divisiontime=QtWidgets.QComboBox(self)
        # combobox_divisiontime_choices = ['Asymmetry', 'Multinucleation', 'Reverse Cleavage', 'Direct Uneven Cleavage','Vacuolated','Chaos']
        # self.combobox_divisiontime.addItems(combobox_divisiontime_choices)
        # self.combobox_divisiontime.setGeometry(10, 890, 150, 30)



        # self.table_img_left.setGeometry(700, 40, 701, 850)
        # self.table_img_right = EmbryoInfoTable(5, 4, ['6cell', '7cell', '8cell', 'Morula', 'Blastocyst'], self)
        # self.table_img_right.setGeometry(1155, 40, 420, 850)
        # self.table_img_right.setFocusPolicy(QtCore.Qt.ClickFocus) 
        
        
        


        # layout = QtWidgets.QGridLayout(self) 
        # layout.addWidget(label_table_left, 0, 0, 1, 2, QtCore.Qt.AlignHCenter)  


        # layout.addWidget(self.table_img_left, 2, 8, 9, 4 )
        # layout.addWidget(self.table_pn, 0, 6, 2, 2 )
        
        # # layout.addWidget(label_video, 0, 2, 1, 4, QtCore.Qt.AlignHCenter)        
        # layout.addWidget(self.frame_video, 0, 0, 5, 4)#HCenter)
        # layout.addWidget(self.playButton, 6, 0, 1, 1)          
        # layout.addWidget(self.selector_fp, 6, 1, 1, 1) 
        # layout.addWidget(self.slider, 6, 2, 1, 2)
        # layout.addWidget(label_combobox_pn, 6, 0, 1, 2)
        # layout.addWidget(self.combobox_pn, 6, 2, 1, 1)

        # layout.addWidget(label_combobox_divisiontime, 7,2, 1, 2,QtCore.Qt.AlignHCenter)
        # layout.addWidget(self.combobox_divisiontime, 7, 3, 1, 2,QtCore.Qt.AlignHCenter)
        # layout.addWidget(label_table_right, 0, 6, 1, 2, QtCore.Qt.AlignHCenter)
        #layout.addWidget(self.table_img_right, 1, 6, 10, 2, QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        # layout.addWidget(label_info, 8, 2, 1, 4, QtCore.Qt.AlignHCenter)
        # layout.addWidget(self.edit_info, 9, 2, 1, 4)

    #get score percent of total ex (div : frag = 0.3:0.7) and which stage score use ex( t2 , t5 ,morula )
    def ReadScorePercentIniFile(self):
        path = './config/config_score_ratio.ini'
        # print('ini path',path)
        self.logger.info('Read file=' + path)
        if not os.path.exists(path):
            print('Not found file=' + path) 
            self.logger.error('Not found file=' + path)                               
        else:
            cfg = RawConfigParser()   
            cfg.read(path)

            score_input_factor_list= []

            score_input_factor=cfg.get('RatioInfo','factor')  
            self.score_input_factor_list=score_input_factor.split(',')
            self.score_division_percentage=round(float(cfg.get('RatioInfo','division_percentage')),2)
            self.score_fragment_percentage=round(float(cfg.get('RatioInfo','fragment_percentage') ),2)
     
            # print('score_input_factor:',score_input_factor,type(score_input_factor))
            # print('score_division_percentage',score_division_percentage,type(score_division_percentage))
            # print('score_fragment_percentage',score_fragment_percentage,type(score_fragment_percentage))            
            # print('cfgcfg.items',cfg.items('DecisionInfo'))
            
            
                

    #get which dish have chamber list for dish select table
    def ReadPatientTransferWell(self,timelapse_id):
        path = './config/config_' +timelapse_id + '.ini'
        # print('ini path',path)
        self.logger.info('Read file=' + path)
        if not os.path.exists(path): 
            print('Not found file=' + path) 
            self.logger.error('Not found file=' + path)                               
        else:
            cfg = RawConfigParser()   
            cfg.read(path)
            # print('cfgcfg.items',cfg.items('DecisionInfo'))
            
            #Show results        
            transfer_well_list = []
            for i in range(len(cfg.items('DecisionInfo'))):
                
                if 'transfer' in [item[0] for item in cfg.items('DecisionInfo')]:
                    settings = cfg.get('DecisionInfo','transfer')                    
                    transfer_well_list = settings.split(',')
            return transfer_well_list
                

    def DoubleClickSelectWell(self):
        row = self.table_dish_selected.currentIndex().row()
        column = self.table_dish_selected.currentIndex().column()
        # print(row, column)
        self.initSource( self.patient_id, self.chamber_id, int(column*7+row))
    

    def EmbryoViewerInfoSave(self):
        
       


        #others info save(RadioButton,QCheckBox)
        save_pn = ''
        
        for combobox_pn_index in range(len(self.qradio_pn_choices)):
            if self.qradio_pn_choices[combobox_pn_index].isChecked():
                save_pn=self.combobox_pn_choices[combobox_pn_index]

        save_location = ''

        for combobox_location_index in range(len(self.qradio_location_choices)):
            if self.qradio_location_choices[combobox_location_index].isChecked():
                save_location=self.combobox_location_choices[combobox_location_index]

        save_morphological = []

        for combobox_morphological_index in range(len(self.qradio_morphological_choices)):
            if self.qradio_morphological_choices[combobox_morphological_index].isChecked():
                save_morphological.append(self.combobox_morphological_choices[combobox_morphological_index])
        
        save_divisiontime = []

        for combobox_divisiontime_index in range(len(self.qradio_divisiontime_choices)):
            if self.qradio_divisiontime_choices[combobox_divisiontime_index].isChecked():
                save_divisiontime.append(self.combobox_divisiontime_choices[combobox_divisiontime_index])
        
        
        save_ICM = ''

        for combobox_ICM_index in range(len(self.qradio_ICM_choices)):
            if self.qradio_ICM_choices[combobox_ICM_index].isChecked():
                save_ICM=self.combobox_ICM_TE_choices[combobox_ICM_index]
        
        save_TE = ''
        for combobox_TE_index in range(len(self.qradio_TE_choices)):
            if self.qradio_TE_choices[combobox_TE_index].isChecked():
                save_TE=self.combobox_ICM_TE_choices[combobox_TE_index]
        
        # print('save info ',save_pn,save_location,save_morphological,save_divisiontime,save_ICM,save_TE)

        # write_EmbryoViewer_combobox_qradio_info(self.chamber_id,self.well_id,save_pn,save_location,save_morphological,save_divisiontime,save_ICM,save_TE)
        

        #update table info(div score ,sub score)
        
        
        for i in range(7):
            div_score=''
           
            div_time =self.table_img_left.item(i*2+2, 2).text()
            if div_time!='':

                interval_time_suc_false = abs(self.divisionTime_avg_false[i]-self.divisionTime_avg_success[i])
                # print('interval time',interval_time_suc_false)
                if abs(float(div_time)-self.divisionTime_avg_success[i])> interval_time_suc_false:
                    div_score = 0
                    # print('div_score',div_score)
                else:
                    # print('div_score r',div_score)
                    div_score= round((1-(abs(float(div_time)-self.divisionTime_avg_success[i] )/interval_time_suc_false))*100,2)
                # div_score = round(float(div_time)/2,2)
                item_data_div_score = QtWidgets.QTableWidgetItem(str(div_score))
                item_data_div_score.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item_data_div_score.setFlags(QtCore.Qt.ItemIsEnabled)
                self.table_img_left.setItem(i*2+2, 3, item_data_div_score)
            
            frag_score = ''
            frag_percent =self.table_img_left.item(i*2+2, 4).text()
            if frag_percent!='':
                frag_score = round(100-float(frag_percent),2)
                if frag_score<0:
                    frag_score=0
                item_data_frag_score = QtWidgets.QTableWidgetItem(str(frag_score))
                item_data_frag_score.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item_data_frag_score.setFlags(QtCore.Qt.ItemIsEnabled)
                self.table_img_left.setItem(i*2+2, 5, item_data_frag_score)

            
            sub_score = div_score

            if sub_score=='':
                
                sub_score=frag_score
            else:
                if frag_score!='':

                    # sub_score=round((div_score+frag_score)/2,2)
                    sub_score = round(div_score*self.score_division_percentage+frag_score*self.score_fragment_percentage,2)
                    # print('sub_score 2 ',sub_score)
            
            item_sub_score = QtWidgets.QTableWidgetItem(str(sub_score))
            item_sub_score.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_sub_score.setFlags(QtCore.Qt.ItemIsEnabled)
            self.table_img_left.setItem(i*2+2, 6, item_sub_score)


            
                    

           
        for i in range(2):
            div_time_score=''
            div_time =self.table_blas_info.item(i*2+2, 2).text()
            if div_time!='':
                # print('float(div_time)-self.divisionTime_avg_success[i+7])> interval_time_suc_false',abs(float(div_time)-self.divisionTime_avg_success[i+7])> interval_time_suc_false)
                interval_time_suc_false = abs(self.divisionTime_avg_false[i+7]-self.divisionTime_avg_success[i+7])
                if abs(float(div_time)-self.divisionTime_avg_success[i+7])> interval_time_suc_false:
                    div_time_score = 0
                else:
                    div_time_score= round((1-(abs(float(div_time)-self.divisionTime_avg_success[i+7] )/interval_time_suc_false))*100,2)
                   
                item_data = QtWidgets.QTableWidgetItem(str(div_time_score))
                item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item_data.setFlags(QtCore.Qt.ItemIsEnabled)
                self.table_blas_info.setItem(i*2+2, 3, item_data)
        

        


        #update pn table-manual pn number
        pn_label_list= ['NPN','1PN','2PN','3PN','Poly-PN'] 
        if save_pn != '':
            pn_number = pn_label_list.index(save_pn)
            item_data_PN = QtWidgets.QTableWidgetItem(str(pn_number))
            item_data_PN.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_data_PN.setFlags(QtCore.Qt.ItemIsEnabled)
            self.table_pn.setItem(2, 4, item_data_PN)


        # sub score in table(t2-t8) add to total score
       

        self.GetSystemManualAvgScore()


        #table manual row info save

        dic_manual_info = {
        'Div_Time':{'PN_Fading':'','t2':'','t3':'','t4':'','t5':'','t6':'','t7':'','t8':'','Morula':'','Blas':''}
        ,'Frag_Percent':{'PN_Fading':'','t2':'','t3':'','t4':'','t5':'','t6':'','t7':'','t8':'','Morula':'','Blas':''}
        ,'Combobox':{'cbo_PN':'','cbo_Loction':'','rdo_Morphological':'','rdo_DivisionTime':'','cbo_ICM':'','cbo_TE':''}
        ,'Total_Score':''
        }
        dic_manual_info['Div_Time']['PN_Fading']=str(self.table_pn.item(2, 2).text())
        dic_manual_info['Div_Time']['t2']=str(self.table_img_left.item(2, 2).text())
        dic_manual_info['Div_Time']['t3']=str(self.table_img_left.item(4, 2).text())
        dic_manual_info['Div_Time']['t4']=str(self.table_img_left.item(6, 2).text())
        dic_manual_info['Div_Time']['t5']=str(self.table_img_left.item(8, 2).text())
        dic_manual_info['Div_Time']['t6']=str(self.table_img_left.item(10, 2).text())
        dic_manual_info['Div_Time']['t7']=str(self.table_img_left.item(12, 2).text())
        dic_manual_info['Div_Time']['t8']=str(self.table_img_left.item(14, 2).text())
        dic_manual_info['Div_Time']['Morula']=str(self.table_blas_info.item(2, 2).text())
        dic_manual_info['Div_Time']['Blas']=str(self.table_blas_info.item(4, 2).text())


        # dic_manual_info['Frag_Percent']['PN_Fading']=str(self.table_pn.item(2, 2).text())
        dic_manual_info['Frag_Percent']['t2']=str(self.table_img_left.item(2, 4).text())
        dic_manual_info['Frag_Percent']['t3']=str(self.table_img_left.item(4, 4).text())
        dic_manual_info['Frag_Percent']['t4']=str(self.table_img_left.item(6, 4).text())
        dic_manual_info['Frag_Percent']['t5']=str(self.table_img_left.item(8, 4).text())
        dic_manual_info['Frag_Percent']['t6']=str(self.table_img_left.item(10, 4).text())
        dic_manual_info['Frag_Percent']['t7']=str(self.table_img_left.item(12, 4).text())
        dic_manual_info['Frag_Percent']['t8']=str(self.table_img_left.item(14, 4).text())
        # dic_manual_info['Frag_Percent']['Morula']=str(self.table_blas_info.item(2, 2).text())
        # dic_manual_info['Frag_Percent']['Blas']=str(self.table_blas_info.item(4, 2).text())
        # print('dic',dic_manual_info)

        dic_manual_info['Combobox']['cbo_PN']=save_pn
        dic_manual_info['Combobox']['cbo_Loction']=save_location
        dic_manual_info['Combobox']['rdo_Morphological']=save_morphological
        dic_manual_info['Combobox']['rdo_DivisionTime']=save_divisiontime
        dic_manual_info['Combobox']['cbo_ICM']=save_ICM
        dic_manual_info['Combobox']['cbo_TE']=save_TE

        dic_manual_info['Total_Score']=str(self.table_total_score_info.item(2, 1).text())



        write_table_manual_info_csv(self.chamber_id,self.well_id,dic_manual_info)


        # total_score_system,total_score_manual=self.GetSystemManualAvgScore()
        # item_total_score_system= QtWidgets.QTableWidgetItem(str(total_score_system))
        # item_total_score_system.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        # item_total_score_system.setFlags(QtCore.Qt.ItemIsEnabled)
        # self.table_total_score_info.setItem(1, 1, item_total_score_system)

        # item_total_score_manual= QtWidgets.QTableWidgetItem(str(total_score_manual))
        # item_total_score_manual.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        # item_total_score_manual.setFlags(QtCore.Qt.ItemIsEnabled)
        # self.table_total_score_info.setItem(2, 1, item_total_score_manual)


        

        # total_score_system = []
        # # if self.table_pn.item(2, 6).text()!='':


        # for i in range (7):
        #     if self.table_img_left.item(i*2+1, 6).text()!='':
        #         total_score_system.append(float(self.table_img_left.item(i*2+1, 6).text()))
        # total_score_manual = []
        # for i in range (7):
        #     if self.table_img_left.item(i*2+2, 6).text()!='':
        #         total_score_manual.append(float(self.table_img_left.item(i*2+2, 6).text()))
        
        # total_score_system_avg = sum(total_score_system)/len(total_score_system)
        # total_score_manual_avg = sum(total_score_manual)/len(total_score_manual)
        # print('total_score_system_avg',total_score_system_avg)
        # print('total_score_manual_avg',total_score_manual_avg)


    def GetSystemManualAvgScore(self):
        stage_list = ['t2','t3','t4','t5','t6','t7','t8','morula','blas']
        score_input_factor_index = [stage_list.index(a) for a in self.score_input_factor_list]
        # self.score_input_factor_list
        total_score_system_avg=''
        total_score_manual_avg=''
        
        total_score_system = []
        total_score_manual=[]

        for i in score_input_factor_index:
            if i<7:
                if self.table_img_left.item(i*2+1, 6).text()!='':
                    total_score_system.append(float(self.table_img_left.item(i*2+1, 6).text()))
                if self.table_img_left.item(i*2+2, 6).text()!='':
                    total_score_manual.append(float(self.table_img_left.item(i*2+2, 6).text()))
            else:
                if  self.table_blas_info.item((i-7)*2+1, 3).text()!='':
                    total_score_system.append(float(self.table_blas_info.item((i-7)*2+1, 3).text()))
                if  self.table_blas_info.item((i-7)*2+2, 3).text()!='':
                    total_score_manual.append(float(self.table_blas_info.item((i-7)*2+2, 3).text()))
        
        # total_score_manual = []

        # for i in range (7):
        #     if self.table_img_left.item(i*2+1, 6).text()!='':
        #         total_score_system.append(float(self.table_img_left.item(i*2+1, 6).text()))

        # for i in range(2):
        #     if  self.table_blas_info.item(i*2+1, 3).text()!='':
        #         total_score_system.append(float(self.table_blas_info.item(i*2+1, 3).text()))
        # total_score_manual = []
        # for i in range (7):
        #     if self.table_img_left.item(i*2+2, 6).text()!='':
        #         total_score_manual.append(float(self.table_img_left.item(i*2+2, 6).text()))
        # for i in range(2):
        #     if  self.table_blas_info.item(i*2+2, 3).text()!='':
        #         total_score_manual.append(float(self.table_blas_info.item(i*2+2, 3).text()))
        


        # print('total_score_system:',total_score_system)
        # print('total_score_manual',total_score_manual)
        if len(total_score_system)!=0:
            total_score_system_avg = round(sum(total_score_system)/len(total_score_system),2)
        if len(total_score_manual)!=0:
            total_score_manual_avg = round(sum(total_score_manual)/len(total_score_manual),2)
        # print('total_score_system_avg',total_score_system_avg)
        # print('total_score_manual_avg',total_score_manual_avg)


        item_total_score_system= QtWidgets.QTableWidgetItem(str(total_score_system_avg))
        item_total_score_system.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item_total_score_system.setFlags(QtCore.Qt.ItemIsEnabled)
        self.table_total_score_info.setItem(1, 1, item_total_score_system)

        item_total_score_manual= QtWidgets.QTableWidgetItem(str(total_score_manual_avg))
        item_total_score_manual.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item_total_score_manual.setFlags(QtCore.Qt.ItemIsEnabled)
        self.table_total_score_info.setItem(2, 1, item_total_score_manual)

        # return total_score_system_avg,total_score_manual_avg


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
        self.ReadScorePercentIniFile()
        self.LoadEmbryoDataPnNew(pid, chid, wid)

        #get transfer well id list which have embryo
        transfer_wellid_list =self.ReadPatientTransferWell(pid)
        self.table_dish_selected.initWellSelectTable(transfer_wellid_list,wid)





        #img_to_video(chid, wid)
        
        path = os.path.abspath(load_video_path_with_7fp(pid, chid, wid, int(str(self.selector_fp.currentText())) - 1))
        
        if not path:
            return
        self.playButton.setEnabled(True)

        self.player.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(path)))
        
        self.patient_id = str(pid)
        self.chamber_id = str(chid)
        self.well_id = str(wid)


        self.offset_time = get_patient_offset_time_from_ini(self.patient_id)
        hour=0
        minute=0
        second=0
        if self.offset_time!='':
            hour,minute,second = int(self.offset_time.split(':')[0]),int(self.offset_time.split(':')[1]),int(self.offset_time.split(':')[2])
        # print('hour minute second',hour,minute,second)
        self.offset_time_to_hours = hour+round(minute/60,2)+round(second/3600,2)
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
        
        # print('slider bar value:',position)
        self.slider.setValue(position)
        self.position_val = position
      
    def durationChanged(self, duration):
        self.slider.setRange(0, duration)    
        self.slider.setTickInterval(round(1000/6,2))     
        self.slider.setSingleStep(round(1000/6,2))   

    def setPosition(self, position):
        self.player.setPosition(position) 


        
        
        
        if self.offset_time_to_hours!='':

            hr_set = round(float(position)/1000+self.offset_time_to_hours,2)
        self.video_time_show.setText(str(hr_set) +' hr') 
        

    def LoadEmbryoDataPnNew(self, patient_id, chamber_id, dish_id):
        print ('LoadEmbryoData')
        # self.video_time_show.setText('')
        #_, filename_dic, timespend_dic, percent_dic = get_each_stage_result(chid, wid)
         
        #{'Xlsx': {'pn': 7.469999999999999, 't2': 9.629999999999999, 't3': 25.129999999999995, 't4': 26.129999999999995, 't5': 42.47, 't6': 44.129999999999995, 't7': 45.300000000000004, 't8': 51.300000000000004, 'morula': 83.46000000000001, 'blas': nan}, 'Predict': {'pn': 0.0, 't2': 5.83, 't3': 20.67, 't4': 22.33, 't5': nan, 't6': 33.0, 't7': 47.5, 't8': 48.33, 'morula': 76.17, 'blas': 79.17, 'comp': nan}, 'Fragment': {'pn': 0.5311904761904762, 't2': 1.1187142857142856, 't3': 3.8090625, 't4': 1.9507042253521132, 't5': 3.500714285714285, 't6': 1.88358024691358, 't7': 2.2823333333333333, 't8': 2.1847499999999997, 'morula': 1.927297297297297, 'blas': 2.9246296296296292}, 'Cham_id': '6', 'Dish_id': '5', 'Patient_id': 'MTL-0245-13A1-9874', 'Dict_key': ['pn', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 'morula', 'blas']}
        dict_msg = get_xlsx_predict_division_time(patient_id, chamber_id, dish_id)# get system predict division time

        dict_manual_msg  = read_table_manual_info_csv(chamber_id, dish_id)
        # print('dict_manual_msg:',dict_manual_msg)

        offset_time = get_patient_offset_time_from_ini(patient_id)
        hour=0
        minute=0
        second=0
        if offset_time!='':
            hour,minute,second = int(offset_time.split(':')[0]),int(offset_time.split(':')[1]),int(offset_time.split(':')[2])
        # print('hour minute second',hour,minute,second)
        
        total_score = 0
        offset_time_to_hours = hour+round(minute/60,2)+round(second/3600,2)
        


        #------------------------------- system time----------------------

        #PN table 

        pn_time='-'
        pn_score=''
        pn_number=dict_msg["Pn_number"]


        if "pn" in dict_msg["Predict"] and str(dict_msg["Predict"]["pn"]) != 'nan' and str(dict_msg["Predict"]["pn"]) != 'NaN' and self.floatTryParse(dict_msg["Predict"]["pn"]):
            pn_time = str(int((float(dict_msg["Predict"]["pn"])+offset_time_to_hours) * 100.0) / 100.0)
        
        self.table_pn.AddRow( pn_time, pn_score,pn_number)



        #2cell ~blas table t2-t8
        for index in range(2,9):
            time = ''
            time_score=''
            frag=''
            frag_score=''
            total_score_time_frag=''
            


            if 't' + str(index) in dict_msg["Predict"] and str(dict_msg["Predict"]['t' + str(index)]) != '' and str(dict_msg["Predict"]['t' + str(index)]) != 'nan' and str(dict_msg["Predict"]['t' + str(index)]) != 'NaN' and self.floatTryParse(dict_msg["Predict"]['t' + str(index)]):
                time = str(int(float((dict_msg["Predict"]['t' + str(index)])+offset_time_to_hours) * 100.0) / 100.0)
                interval_time_suc_false = abs(self.divisionTime_avg_false[index-2]-self.divisionTime_avg_success[index-2])
                time_score=''
                # print('interval time',interval_time_suc_false)
                if abs(float(time)-self.divisionTime_avg_success[index-2])> interval_time_suc_false:
                    time_score = 0
                    # print('div_score',time_score)
                else:
                    # print('div_score r',time_score)
                    time_score= round((1-(abs(float(time)-self.divisionTime_avg_success[index-2] )/interval_time_suc_false))*100,2)
                    # div_score = round(float(div_time)/2,2)
                # time_score = (int(float(dict_msg["Predict"]['t' + str(index)]) * 100.0) / 100.0)/2
                total_score_time_frag=time_score
                
                
            if 't' + str(index) in dict_msg["Fragment"] and str(dict_msg["Fragment"]['t' + str(index)]) != '' and str(dict_msg["Fragment"]['t' + str(index)]) != 'nan' and str(dict_msg["Fragment"]['t' + str(index)]) != 'NaN' and self.floatTryParse(dict_msg["Fragment"]['t' + str(index)]):  
                frag=(round(4*(float(dict_msg["Fragment"]['t' + str(index)])),2))
                frag_score = round(100 - frag,2)

                # frag_score = frag/2

                if total_score_time_frag=='':
                    # print('Total score is 0')
                    total_score_time_frag = frag_score
                else:
                    # total_score_time_frag = total_score_time_frag+ frag_score
                    # total_score_time_frag =round(total_score_time_frag/2,2)
                    total_score_time_frag=round(time_score*self.score_division_percentage+frag_score*self.score_fragment_percentage,2)
                    # print('Total score is divid 2')

            # print('total_score_time_frag:',total_score_time_frag)
            label_l_analysis = EmbryoImageLabel(150, 150, [str(time), str(time_score), str(frag), str(frag_score), str(total_score_time_frag)])


            self.table_img_left.AddSystemRow(index-2, label_l_analysis) 
        

        #morula blas table
    
        for index in range(2):
            time = ''
            time_score=''
            frag=''
            frag_score=''
            total_score_time_frag=0
            if index == 0:
                if "morula" in dict_msg["Predict"] and str(dict_msg["Predict"]["morula"]) != '' and str(dict_msg["Predict"]["morula"]) != 'nan' and str(dict_msg["Predict"]["morula"]) != 'NaN' and self.floatTryParse(dict_msg["Predict"]["morula"]):     
                    time = str(int(float(dict_msg["Predict"]['morula']+offset_time_to_hours) * 100.0) / 100.0)  
    
                    interval_time_suc_false = abs(self.divisionTime_avg_false[index+7]-self.divisionTime_avg_success[index+7])
                    time_score=''
                    if abs(float(time)-self.divisionTime_avg_success[index+7])> interval_time_suc_false:
                        time_score = 0
                        
                    else:
                        
                        time_score= round((1-(abs(float(time)-self.divisionTime_avg_success[index+7] )/interval_time_suc_false))*100,2)
                        
            if index == 1:
                if "blas" in dict_msg["Predict"] and str(dict_msg["Predict"]["blas"]) != '' and str(dict_msg["Predict"]["blas"]) != 'nan' and str(dict_msg["Predict"]["blas"]) != 'NaN' and self.floatTryParse(dict_msg["Predict"]["blas"]):                                       
                    time = str(int(float(dict_msg["Predict"]['blas']+offset_time_to_hours) * 100.0) / 100.0)  
                    #
                    interval_time_suc_false = abs(self.divisionTime_avg_false[index+7]-self.divisionTime_avg_success[index+7])
                    time_score=''
                    if abs(float(time)-self.divisionTime_avg_success[index+7])> interval_time_suc_false:
                        time_score = 0
                        
                    else:
                        
                        time_score= round((1-(abs(float(time)-self.divisionTime_avg_success[index+7] )/interval_time_suc_false))*100,2)
                        
            
            label_l_analysis_blas = EmbryoImageLabel(150, 150, [str(time), str(time_score)])


            self.table_blas_info.AddSystemRow(index, label_l_analysis_blas)
                             
        


        #------------------------------- system time----------------------



        #------------------------------- manual time----------------------

        #PN table 

        pn_time=''
        pn_score=''
        pn_number=''

        # print("dict_manual_msgdict_manual_msg PN_Fading:",dict_manual_msg["PN_Fading"])
        if "PN_Fading" in dict_manual_msg['Div_Time'] and str(dict_manual_msg['Div_Time']["PN_Fading"]) != '' and str(dict_manual_msg['Div_Time']["PN_Fading"]) != 'nan' and str(dict_manual_msg['Div_Time']["PN_Fading"]) != 'NaN' and self.floatTryParse(float(dict_manual_msg['Div_Time']["PN_Fading"])):
            pn_time = int(float(dict_manual_msg['Div_Time']["PN_Fading"]) * 100.0) / 100.0
        label_l_analysis_pn = EmbryoImageLabel(150, 150, [str(pn_time),str(pn_score),str(pn_number)])

        
        self.table_pn.AddManualRow( label_l_analysis_pn)





        #2cell ~blas table t2-t8
        for index in range(2,9):
            time = ''
            time_score=''
            frag=''
            frag_score=''
            total_score_time_frag=''
            # print('t2',dict_manual_msg['t2'])
            

            # print('self.intTryParse',self.intTryParse(dict_manual_msg['t' + str(index)]))
            if 't' + str(index) in dict_manual_msg['Div_Time'] and str(dict_manual_msg['Div_Time']['t' + str(index)]) != '' and str(dict_manual_msg['Div_Time']['t' + str(index)]) != 'nan' and str(dict_manual_msg['Div_Time']['t' + str(index)]) != 'NaN' and self.floatTryParse(float(dict_manual_msg['Div_Time']['t' + str(index)])):
                time = round(float(dict_manual_msg['Div_Time']['t' + str(index)]),2 )
                interval_time_suc_false = abs(self.divisionTime_avg_false[index-2]-self.divisionTime_avg_success[index-2])
                time_score=''
                
                if abs(float(time)-self.divisionTime_avg_success[index-2])> interval_time_suc_false:
                    time_score = 0
                   
                else:
                   
                    time_score= round((1-(abs(float(time)-self.divisionTime_avg_success[index-2] )/interval_time_suc_false))*100,2)
                   
                total_score_time_frag=time_score
            else:
                if 't' + str(index) in dict_msg["Predict"] and str(dict_msg["Predict"]['t' + str(index)]) != '' and str(dict_msg["Predict"]['t' + str(index)]) != 'nan' and str(dict_msg["Predict"]['t' + str(index)]) != 'NaN' and self.floatTryParse(dict_msg["Predict"]['t' + str(index)]):
                    time = str(int(float((dict_msg["Predict"]['t' + str(index)])+offset_time_to_hours) * 100.0) / 100.0)
                    interval_time_suc_false = abs(self.divisionTime_avg_false[index-2]-self.divisionTime_avg_success[index-2])
                    time_score=''
                    # print('interval time',interval_time_suc_false)
                    if abs(float(time)-self.divisionTime_avg_success[index-2])> interval_time_suc_false:
                        time_score = 0
                        # print('div_score',time_score)
                    else:
                        # print('div_score r',time_score)
                        time_score= round((1-(abs(float(time)-self.divisionTime_avg_success[index-2] )/interval_time_suc_false))*100,2)
                        # div_score = round(float(div_time)/2,2)
                    # time_score = (int(float(dict_msg["Predict"]['t' + str(index)]) * 100.0) / 100.0)/2
                    total_score_time_frag=time_score
                    

            # print(index,round(float(dict_manual_msg["Frag_Percent"]['t' + str(index)]),2))
            # print(index,self.floatTryParse(dict_manual_msg["Frag_Percent"]['t' + str(index)]))
            # print(float(dict_manual_msg["Frag_Percent"]['t' + str(index)]))
            if 't' + str(index) in dict_manual_msg["Frag_Percent"] and str(dict_manual_msg["Frag_Percent"]['t' + str(index)]) != '' and str(dict_manual_msg["Frag_Percent"]['t' + str(index)]) != 'nan' and str(dict_manual_msg["Frag_Percent"]['t' + str(index)]) != 'NaN' and self.floatTryParse(dict_manual_msg["Frag_Percent"]['t' + str(index)]):  
                
                frag=(round(float(dict_manual_msg["Frag_Percent"]['t' + str(index)]),2))
                # print('ict_manual_msg["Frag_Percent"]',frag)
                frag_score = round(100 - frag,2)
                if frag_score<0:
                    frag_score=0

                if total_score_time_frag=='':
                   
                    total_score_time_frag = frag_score
                else:
                    total_score_time_frag=round(time_score*self.score_division_percentage+frag_score*self.score_fragment_percentage,2)
                    
                    # total_score_time_frag = total_score_time_frag+ frag_score
                    # total_score_time_frag =round(total_score_time_frag/2,2)
                    
            else:
                if 't' + str(index) in dict_msg["Fragment"] and str(dict_msg['Fragment']) != '' and   str(dict_msg["Fragment"]['t' + str(index)]) != 'nan' and str(dict_msg["Fragment"]['t' + str(index)]) != 'NaN' and self.floatTryParse(dict_msg["Fragment"]['t' + str(index)]):  
                    frag=(round(4*(float(dict_msg["Fragment"]['t' + str(index)])),2))
                    frag_score = round(100 - frag,2)

                    # frag_score = frag/2
                    if total_score_time_frag=='':

                        total_score_time_frag = frag_score
                    else:
                        total_score_time_frag=round(time_score*self.score_division_percentage+frag_score*self.score_fragment_percentage,2)
                    
                        # total_score_time_frag = total_score_time_frag+ frag_score
                        # total_score_time_frag =round(total_score_time_frag/2,2)
                    
            
            
            label_l_analysis_manual = EmbryoImageLabel(150, 150, [str(time), str(time_score), str(frag), str(frag_score), str(total_score_time_frag)])


            self.table_img_left.AddManualRow(index-2, label_l_analysis_manual) 
        

        #morula blas table

        for index in range(2):
            time = ''
            time_score=''
            frag=''
            frag_score=''
            total_score_time_frag=''

            
            if index == 0:
                if "Morula" in dict_manual_msg['Div_Time'] and str(dict_manual_msg['Div_Time']["Morula"]) != '' and str(dict_manual_msg['Div_Time']["Morula"]) != 'nan' and str(dict_manual_msg['Div_Time']["Morula"]) != 'NaN' and self.floatTryParse(float(dict_manual_msg['Div_Time']["Morula"])):     
                    # time = str(int(float(dict_manual_msg['Morula']) * 100.0) / 100.0)  
                    # time_score = (int(float(dict_manual_msg['Morula']) * 100.0) / 100.0)/2
                    time =round( float(dict_manual_msg['Div_Time']["Morula"]) ,2)
                    interval_time_suc_false = abs(self.divisionTime_avg_false[index+7]-self.divisionTime_avg_success[index+7])
                    time_score=''
                    # print('interval time',interval_time_suc_false)
                    if abs(float(time)-self.divisionTime_avg_success[index+7])> interval_time_suc_false:
                        time_score = 0
                        # print('div_score',time_score)
                    else:
                        # print('div_score r',time_score)
                        time_score= round((1-(abs(float(time)-self.divisionTime_avg_success[index+7] )/interval_time_suc_false))*100,2)
                        # div_score = round(float(div_time)/2,2)
                    # time_score = (int(float(dict_msg["Predict"]['t' + str(index)]) * 100.0) / 100.0)/2
                    # total_score_time_frag=total_score_time_frag +time_score
                    
            if index == 1:
                if "Blas" in dict_manual_msg['Div_Time'] and str(dict_manual_msg['Div_Time']["Blas"]) != '' and str(dict_manual_msg['Div_Time']["Blas"]) != 'nan' and str(dict_manual_msg['Div_Time']["Blas"]) != 'NaN' and self.floatTryParse(float(dict_manual_msg['Div_Time']["Blas"])):                                       
                    # time = str(int(float(dict_manual_msg["Blas"]) * 100.0) / 100.0)
                    # time_score = (int(float(dict_manual_msg['Blas']) * 100.0) / 100.0)/2
                    time = round( float(dict_manual_msg['Div_Time']["Blas"]) ,2)
                    interval_time_suc_false = abs(self.divisionTime_avg_false[index+7]-self.divisionTime_avg_success[index+7])
                    # print('interval_time_suc_false',interval_time_suc_false)
                    time_score=''
                    # print('interval time',interval_time_suc_false)
                    if abs(float(time)-self.divisionTime_avg_success[index+7])> interval_time_suc_false:
                        time_score = 0
                        # print('div_score',time_score)
                    else:
                        # print('div_score r',time_score)
                        # print('abs(float(time)-self.divisionTime_avg_success[index+7] )/interval_time_suc_false',abs(float(time)-self.divisionTime_avg_success[index+7] )/interval_time_suc_false)
                        time_score= round((1-(abs(float(time)-self.divisionTime_avg_success[index+7] )/interval_time_suc_false))*100,2)
                        # div_score = round(float(div_time)/2,2)
                
            
            label_l_analysis_blas = EmbryoImageLabel(150, 150, [str(time), str(time_score)])


            self.table_blas_info.AddManualRow(index, label_l_analysis_blas)





                             
        
        dic_cbo_rdo_button_info = read_EmbryoViewer_combobox_qradio_info(chamber_id,dish_id)



        #init radiobutton or checkbox status to empty
        self.qradio_pn_group.setExclusive(False)
        for i in range(len(self.qradio_pn_choices)):
            
            self.qradio_pn_choices[i].setChecked(False)
        self.qradio_pn_group.setExclusive(True)

        self.qradio_location_group.setExclusive(False)
        for i in range(len(self.qradio_location_choices)):
            self.qradio_location_choices[i].setChecked(False)
        self.qradio_location_group.setExclusive(True)

        for i in range(len(self.qradio_morphological_choices)):
            self.qradio_morphological_choices[i].setChecked(False)

        for i in range(len(self.qradio_divisiontime_choices)):
            self.qradio_divisiontime_choices[i].setChecked(False)
        
        self.qradio_ICM_group.setExclusive(False)
        for i in range(len(self.qradio_ICM_choices)):
            self.qradio_ICM_choices[i].setChecked(False)
        self.qradio_ICM_group.setExclusive(True)

        self.qradio_TE_group.setExclusive(False)
        for i in range(len(self.qradio_TE_choices)):
            self.qradio_TE_choices[i].setChecked(False)
        self.qradio_TE_group.setExclusive(True)
    
 

        # radiobutton checkbox set values 
        if dic_cbo_rdo_button_info['cbo_PN']!='':
            cbo_PN_index=self.combobox_pn_choices.index(dic_cbo_rdo_button_info['cbo_PN'])
            self.qradio_pn_choices[cbo_PN_index].setChecked(True)
        
            
            
            
        if dic_cbo_rdo_button_info['cbo_Loction']!='':
            cbo_Location_index=self.combobox_location_choices.index(dic_cbo_rdo_button_info['cbo_Loction'])
            self.qradio_location_choices[cbo_Location_index].setChecked(True)
        
            
        
        if dic_cbo_rdo_button_info['rdo_Morphological']!='':
            for i in range(len(dic_cbo_rdo_button_info['rdo_Morphological'])):
                
                cbo_Morphological_index=self.combobox_morphological_choices.index(dic_cbo_rdo_button_info['rdo_Morphological'][i])
                self.qradio_morphological_choices[cbo_Morphological_index].setChecked(True)
        
            
        
        if dic_cbo_rdo_button_info['rdo_DivisionTime']!='':
            for i in range(len(dic_cbo_rdo_button_info['rdo_DivisionTime'])):
                cbo_Divisiontime_index=self.combobox_divisiontime_choices.index(dic_cbo_rdo_button_info['rdo_DivisionTime'][i])
                self.qradio_divisiontime_choices[cbo_Divisiontime_index].setChecked(True)
        
            

        if dic_cbo_rdo_button_info['cbo_ICM']!='':
            cbo_ICM_index=self.combobox_ICM_TE_choices.index(dic_cbo_rdo_button_info['cbo_ICM'])
            self.qradio_ICM_choices[cbo_ICM_index].setChecked(True)

        
           
        
        if dic_cbo_rdo_button_info['cbo_TE']!='':
            cbo_TE_index=self.combobox_ICM_TE_choices.index(dic_cbo_rdo_button_info['cbo_TE'])
            self.qradio_TE_choices[cbo_TE_index].setChecked(True)
       

        #write pn number into pn table
        pn_label_list= ['NPN','1PN','2PN','3PN','Poly-PN'] 
        if dic_cbo_rdo_button_info['cbo_PN'] != '':
            pn_number = pn_label_list.index(dic_cbo_rdo_button_info['cbo_PN'])
            item_data_PN = QtWidgets.QTableWidgetItem(str(pn_number))
            item_data_PN.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_data_PN.setFlags(QtCore.Qt.ItemIsEnabled)
            self.table_pn.setItem(2, 4, item_data_PN)
        


        # sub score in table(t2-t8) add to total score
        #system

        
        self.GetSystemManualAvgScore()

        # total_score_system = []
        # # if self.table_pn.item(2, 6).text()!='':


        # for i in range (7):
        #     if self.table_img_left.item(i*2+1, 6).text()!='':
        #         total_score_system.append(float(self.table_img_left.item(i*2+1, 6).text()))
        # total_score_manual = []
        # for i in range (7):
        #     if self.table_img_left.item(i*2+2, 6).text()!='':
        #         total_score_manual.append(float(self.table_img_left.item(i*2+2, 6).text()))
        
        # total_score_system_avg = sum(total_score_system)/len(total_score_system)
        # total_score_manual_avg = sum(total_score_manual)/len(total_score_manual)
        # print('total_score_system_avg',total_score_system_avg)
        # print('total_score_manual_avg',total_score_manual_avg)

     
    # def LoadEmbryoData(self, patient_id, chamber_id, dish_id):
    #     print ('LoadEmbryoData')
    #     #_, filename_dic, timespend_dic, percent_dic = get_each_stage_result(chid, wid)
         
    #     #{'Xlsx': {'pn': 7.469999999999999, 't2': 9.629999999999999, 't3': 25.129999999999995, 't4': 26.129999999999995, 't5': 42.47, 't6': 44.129999999999995, 't7': 45.300000000000004, 't8': 51.300000000000004, 'morula': 83.46000000000001, 'blas': nan}, 'Predict': {'pn': 0.0, 't2': 5.83, 't3': 20.67, 't4': 22.33, 't5': nan, 't6': 33.0, 't7': 47.5, 't8': 48.33, 'morula': 76.17, 'blas': 79.17, 'comp': nan}, 'Fragment': {'pn': 0.5311904761904762, 't2': 1.1187142857142856, 't3': 3.8090625, 't4': 1.9507042253521132, 't5': 3.500714285714285, 't6': 1.88358024691358, 't7': 2.2823333333333333, 't8': 2.1847499999999997, 'morula': 1.927297297297297, 'blas': 2.9246296296296292}, 'Cham_id': '6', 'Dish_id': '5', 'Patient_id': 'MTL-0245-13A1-9874', 'Dict_key': ['pn', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 'morula', 'blas']}
    #     dict_msg = get_xlsx_predict_division_time(patient_id, chamber_id, dish_id)
    #     print(dict_msg)
    #     total_score = 0
    #     count = 0   
        
    #     #Left table               
    #     for n in range(5):
    #         #Analysis            
    #         grade = '-'
    #         score = '-'
    #         time = '-'
    #         #Find grade time
    #         if n == 0:
    #             if "pn" in dict_msg["Predict"] and str(dict_msg["Predict"]["pn"]) != 'nan' and str(dict_msg["Predict"]["pn"]) != 'NaN' and self.intTryParse(dict_msg["Predict"]["pn"]):
    #                 time = str(int(dict_msg["Predict"]["pn"] * 100.0) / 100.0) 
    #             if "pn" in dict_msg["Fragment"] and str(dict_msg["Fragment"]["pn"]) != 'nan' and str(dict_msg["Fragment"]["pn"]) != 'NaN' and self.intTryParse(dict_msg["Fragment"]["pn"]):  
    #                 grade = self.MapGradeValue(int(dict_msg["Fragment"]["pn"]))
    #                 score = 100 - (4 * int(dict_msg["Fragment"]["pn"]))
    #             print('score',score)                 
    #             if score != '-':
    #                 total_score = total_score + score
    #                 count += 1
    #         if n >= 1:
    #             if 't' + str(n + 1) in dict_msg["Predict"] and str(dict_msg["Predict"]['t' + str(n + 1)]) != 'nan' and str(dict_msg["Predict"]['t' + str(n + 1)]) != 'NaN' and self.intTryParse(dict_msg["Predict"]['t' + str(n + 1)]):
    #                 time = str(int(dict_msg["Predict"]['t' + str(n + 1)] * 100.0) / 100.0)  
    #             if 't' + str(n + 1) in dict_msg["Fragment"] and str(dict_msg["Fragment"]['t' + str(n + 1)]) != 'nan' and str(dict_msg["Fragment"]['t' + str(n + 1)]) != 'NaN' and self.intTryParse(dict_msg["Fragment"]['t' + str(n + 1)]):  
    #                 grade = self.MapGradeValue(math.ceil(dict_msg["Fragment"]['t' + str(n + 1)]))
    #                 score = 100 - (4 * math.ceil(dict_msg["Fragment"]['t' + str(n + 1)]))               
    #             if score != '-':
    #                 total_score = total_score + score
    #                 count += 1            
    #         label_l_analysis = EmbryoImageLabel(150, 150, [str(grade), str(time), str(score)]) 
            
    #         #View              
    #         time = '-'
    #         #Find grade time
    #         if n == 0 and "pn" in dict_msg["Xlsx"] and str(dict_msg["Xlsx"]["pn"]) != 'nan' and str(dict_msg["Xlsx"]["pn"]) != 'NaN' and self.intTryParse(dict_msg["Xlsx"]["pn"]):
    #             time = str(int(dict_msg["Xlsx"]["pn"] * 100.0) / 100.0)                
    #         if n >= 1 and 't' + str(n + 1) in dict_msg["Xlsx"] and str(dict_msg["Xlsx"]['t' + str(n + 1)]) != 'nan' and str(dict_msg["Xlsx"]['t' + str(n + 1)]) != 'NaN' and self.intTryParse(dict_msg["Xlsx"]['t' + str(n + 1)]):   
    #             time = str(int(dict_msg["Xlsx"]['t' + str(n + 1)] * 100.0) / 100.0)                                     
    #         label_l_view = EmbryoImageLabel(150, 150, ['-', str(time), '-'])   
            
    #         #Insert data      
    #         self.table_img_left.AddRow(n, label_l_analysis, label_l_view)  
                         
    #     #Right table
    #     for n in range(5):
    #         grade = '-'   
    #         score = '-'
    #         time = '-'            
    #         #Find grade time            
    #         if n < 3: 
    #             if 't' + str(n + 6) in dict_msg["Predict"] and str(dict_msg["Predict"]['t' + str(n + 6)]) != 'nan' and str(dict_msg["Predict"]['t' + str(n + 6)]) != 'NaN' and self.intTryParse(dict_msg["Predict"]['t' + str(n + 6)]):
    #                 time = str(int(dict_msg["Predict"]['t' + str(n + 6)] * 100.0) / 100.0)                    
    #             if 't' + str(n + 6) in dict_msg["Fragment"] and str(dict_msg["Fragment"]['t' + str(n + 6)]) != 'nan' and str(dict_msg["Fragment"]['t' + str(n + 6)]) != 'NaN' and self.intTryParse(dict_msg["Fragment"]['t' + str(n + 6)]):
    #                 grade = self.MapGradeValue(math.ceil(dict_msg["Fragment"]['t' + str(n + 6)]))
    #                 score = 100 - (4 * math.ceil(dict_msg["Fragment"]['t' + str(n + 6)]))                
    #             if score != '-':
    #                 total_score = total_score + score
    #                 count += 1
                    
    #         if n == 3:
    #             if "morula" in dict_msg["Predict"] and str(dict_msg["Predict"]["morula"]) != 'nan' and str(dict_msg["Predict"]["morula"]) != 'NaN' and self.intTryParse(dict_msg["Predict"]["morula"]):                             
    #                 time = str(int(dict_msg["Predict"]["morula"] * 100.0) / 100.0)
    #             if "morula" in dict_msg["Fragment"] and str(dict_msg["Fragment"]["morula"]) != 'nan' and str(dict_msg["Fragment"]["morula"]) != 'NaN' and self.intTryParse(dict_msg["Fragment"]["morula"]):       
    #                 grade = self.MapGradeValue(math.ceil(dict_msg["Fragment"]["morula"]))
    #                 score = 100 - (4 * math.ceil(dict_msg["Fragment"]["morula"]))
                   
    #         if n == 4:
    #             if "blas" in dict_msg["Predict"] and str(dict_msg["Predict"]["blas"]) != 'nan' and str(dict_msg["Predict"]["blas"]) != 'NaN' and self.intTryParse(dict_msg["Predict"]["blas"]):                                       
    #                 time = str(int(dict_msg["Predict"]["blas"] * 100.0) / 100.0)
                                       
    #         #View           
    #         time_ = '-'
    #         #Find grade time
    #         if n < 3: 
    #             if 't' + str(n + 6) in dict_msg["Xlsx"] and str(dict_msg["Xlsx"]['t' + str(n + 6)]) != 'nan' and str(dict_msg["Xlsx"]['t' + str(n + 6)]) != 'NaN' and self.intTryParse(dict_msg["Xlsx"]['t' + str(n + 6)]):                
    #                 time_ = str(int(dict_msg["Xlsx"]['t' + str(n + 6)] * 100.0) / 100.0)
                                    
    #         if n == 3:
    #             if "morula" in dict_msg["Xlsx"] and str(dict_msg["Xlsx"]["morula"]) != 'nan' and str(dict_msg["Xlsx"]["morula"]) != 'NaN' and self.intTryParse(dict_msg["Xlsx"]["morula"]):
    #                 time_ = str(int(dict_msg["Xlsx"]["morula"] * 100.0) / 100.0)
                   
    #         if n == 4:
    #             if "blas" in dict_msg["Xlsx"] and str(dict_msg["Xlsx"]["blas"]) != 'nan' and str(dict_msg["Xlsx"]["blas"]) != 'NaN' and self.intTryParse(dict_msg["Xlsx"]["blas"]):                                 
    #                 time_ = str(int(dict_msg["Xlsx"]["blas"] * 100.0) / 100.0)
                                             
                  
    #         #Insert data 
    #         # self.table_img_right.SetChamberIdPid(chamber_id, dish_id)
    #         if n < 4:
    #             label_r_view = EmbryoImageLabel(150, 150, ['-', str(time_), '-'])
    #             label_r_analysis = EmbryoImageLabel(150, 150, [str(grade), str(time), str(score)])                           
    #         else:
    #             label_r_view = EmbryoImageLabel(150, 150, [str(time_), '-', '-'])
    #             label_r_analysis = EmbryoImageLabel(150, 150, [str(time), "ICM", "TE"])
    #         # self.table_img_right.AddRow(n, label_r_analysis, label_r_view) 
                        
    #     #Insert info data
    #     if count != 0:
    #         val = str(int((float(total_score) / float(count)) * 100) / 100)
    #     else:
    #         val = 0
                
    #     self.edit_info.clear()
    #     self.edit_info.insertPlainText('Overall Scoring: {}\n'.format(val))
    #     self.edit_info.insertPlainText('Event:')
      
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
    def floatTryParse(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False
       
       