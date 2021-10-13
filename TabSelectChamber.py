# -*- coding: utf-8 -*-
"""
Created on Fri May 29 13:55:00 2020

@author: minghung
"""
import os, io, math, subprocess
from configparser import RawConfigParser
from Calendar import Calendar
import time, queue
from datetime import datetime
from PyQt5 import QtCore, QtWidgets, QtGui 

from SelectCellDish import SelectCellDish
from Ui_Function import *
from UnixSocketServer import UnixSocketServer
from UnixSocketClient import UnixSocketClient
from ImportSqliteDialog import ImportSqliteDialog
#from extract_sqlite import *
from Class_Extract_Sqlite import Extract_Sqlite
from Chamber_inference_Class import Chamber_Inference


# from DateWithTime import DateWithTime


class TimeCountThread(QtCore.QThread):
    #update = QtCore.pyqtSignal()
    def __init__(self, edit_time, chamber_id, parent=None):
        super(TimeCountThread, self).__init__(parent=parent)
        self.chamber_id  = chamber_id
        self.b_stop = False
        self.b_pause = False
        self.edit_time = edit_time
        
    def run(self):
        while not self.b_stop:
            #print (self.edit_time)
            if not self.b_pause:
                self.count()
            #self.update.emit(self.count())  
            time.sleep(1)
            
    def count(self):       
        time = str(self.edit_time.text()).split(':')
        hr = int(time[0])
        mins = int(time[1])
        sec = int(time[2])
        new_mins = mins
        new_sec = sec + 1
        if new_sec >= 60:
            new_sec = 0            
            new_mins = new_mins + 1
        if new_mins >=60:
            new_mins = 0
            hr += 1
        self.edit_time.setText(str(hr).zfill(3) + ':' + str(new_mins).zfill(2) + ':' + str(new_sec).zfill(2))
           
    def Stop(self):        
        self.b_stop = True
        
    def Pause(self):
        self.b_pause = True
        
    def Continue(self):
        self.b_pause = False
               
        
class ExtractSqliteThread(QtCore.QThread):
    finished = QtCore.pyqtSignal(str, str)
    def __init__(self, patient_id, chamber_id, client, parent=None):
        super(ExtractSqliteThread, self).__init__(parent=parent)  
        self.patient_id = patient_id
        self.chamber_id = chamber_id 
        self.client = client
        self.b_stop = False
        
        dir_path = '/home/n200/D-slot/20201221_ivf_data/'         
        self.extract_sqlite = Extract_Sqlite(dir_path + self.patient_id, self.chamber_id, self.client)
                
    def run(self):       
        self.extract_sqlite.start_extract()
        if not self.b_stop:
            self.finished.emit(self.patient_id, self.chamber_id) 
        
    def Stop(self):
        self.b_stop = True
        self.extract_sqlite.stop()   
         
        
 
class ExportDialog(QtWidgets.QDialog):    
    def __init__(self, parent=None):
        super(ExportDialog, self).__init__(parent=parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)                
        self.resize(180, 130)        
        self.setWindowTitle("System Info")         
        label = QtWidgets.QLabel('Export...',self)
        label.setFont(QtGui.QFont('Arial', 16))
        label.setGeometry(10, 10, 190, 40)
        
        self.setStyleSheet("background-color:#ff90b1;")
        self.label_loading = QtWidgets.QLabel(self)        
        self.label_loading.setGeometry(QtCore.QRect(60, 50, 70, 70))
           
        self.processing_movie = QtGui.QMovie("processing.gif") 
        self.processing_movie.setScaledSize(QtCore.QSize(70, 70))          
        self.label_loading.setMovie(self.processing_movie)
        self.processing_movie.start() 
               

class ExportThread(QtCore.QThread):
    finished = QtCore.pyqtSignal(str, str)
    def __init__(self, patient_id, chamber_id, date, parent=None):
        super(ExportThread, self).__init__(parent=parent)  
        self.patient_id = patient_id
        self.chamber_id = chamber_id 
        self.date = date
        self.parent = parent
        
    def run(self):       
        move_select_cham_dish_folder(self.patient_id, self.date, int(self.chamber_id))
        clear_cham_dish_data_csv(int(self.chamber_id))
        if self.parent != None:
            self.parent.export_dialog.close()
        
       
class TabSelectChamber(QtWidgets.QWidget):
    def __init__(self, logger, main_widget, parent=None):
        super(TabSelectChamber, self).__init__(parent=parent)        
        self.main_widget = main_widget
        self.logger = logger


        self.mnt_history_path = './history/'
        self.maunal_timeset_check = False
        
        self.threads = []
        self.extract_thread = []
        self.analysis_thread = []
        
        self.unix_socket_client = UnixSocketClient('bind_test', logger) 
        
        self.unix_socket_server = UnixSocketServer('bind_test', logger)
        self.unix_socket_server.finished.connect(self.ProcessUnixsocketMsg)
        self.unix_socket_server.start()
        
        self.import_dialog = ImportSqliteDialog(self)        
        
        self.analysis_embryo = Chamber_Inference(self.unix_socket_client, self.logger, self)
        self.analysis_embryo.finished.connect(self.ReadyExport)
        self.analysis_embryo.start()
        
        self.initUI()      
               
    def initUI(self):        
        self.frame_chamber = QtWidgets.QFrame(self) 
        self.frame_chamber.setGeometry(10, 10, 1800, 960)   
        self.frame_chamber.setFrameShape(QtWidgets.QFrame.StyledPanel)        
        self.layout_chamber = QtWidgets.QGridLayout(self.frame_chamber)           
        # self.AddOnlineOfflineMode()
        
        
    def GetPatientID(self, chamber_id):
        listsMyQLineEdit = self.chambers[int(chamber_id) - 1].findChildren(QtWidgets.QLineEdit)
        return str(listsMyQLineEdit[0].text())    

    def AddOnlineOfflineModeCheckbox(self):
        
        Mode_widget = QtWidgets.QWidget()
        Mode_widget.setFixedSize(QtCore.QSize(800, 20))
        # label_mode = QtWidgets.QLabel('Mode Select:', a)
        # label_mode.setFont(QtGui.QFont('Arial', 12))
        # label_mode.setGeometry(10, 0, 140, 10)


        label_mode = QtWidgets.QLabel('Mode Select:', Mode_widget)
        label_mode.setFont(QtGui.QFont('Arial', 12))
        label_mode.setGeometry(0, 0, 140, 20) 

        
        qbutton_online = QtWidgets.QRadioButton('online',Mode_widget)
        qbutton_online.setGeometry(150, 0, 150, 20)
        qbutton_online.setFont(QtGui.QFont('Arial', 12)) 
        qbutton_online.toggled.connect(lambda:self.ClickSetmanualCheckbox(False))

        qbutton_offline = QtWidgets.QRadioButton('offline',Mode_widget)
        qbutton_offline.setGeometry(300, 0, 150, 20) 
        qbutton_offline.setFont(QtGui.QFont('Arial', 12))
        qbutton_offline.toggled.connect(lambda:self.ClickSetmanualCheckbox(True))


        


        qbuttongroup_mode = QtWidgets.QButtonGroup(Mode_widget)
        qbuttongroup_mode.addButton(qbutton_online, 1)
        qbuttongroup_mode.addButton(qbutton_offline, 2)
        self.layout_chamber.addWidget(Mode_widget, 0, 0,1,3)
          
    def AddWells(self, chamber_number, well_number):
        #Clear
        while self.layout_chamber.count():
            item = self.layout_chamber.takeAt(0)
            widget = item.widget()
            widget.deleteLater()
        
        self.chamber_number = chamber_number
        self.chamber_wells = []       
        self.edit_well_time = []   
        self.chambers = []

        self.AddOnlineOfflineModeCheckbox()
        


        
        count = 0      
        for frame_row in range(3):            
            for i in range(3):               
                if count >= chamber_number:                    
                    continue  
                #Add chamber frame
                widget_chamber, group_chamber = self.AddChamberFrameLayout(frame_row, i)                        
                
                #Add dishs
                select_dishs = []
                count_well = 0
                for c in range(8):
                    for well_row in range(2):                    
                        if count_well >= well_number:
                            continue
                        dish = SelectCellDish(count + 1, count_well + 1, self.main_widget, group_chamber)
                        dish.setGeometry(5 + 65 * c + 12 * c, 290 + well_row * 50 + 12 * well_row, 60, 60)
                        count_well += 1                      
                        select_dishs.append(dish)                        
                        
                self.chamber_wells.append(select_dishs)
                print('frame row col number',frame_row+1,i)
                self.layout_chamber.addWidget(widget_chamber, frame_row+1, i)
                
                self.chambers.append(group_chamber)
                count += 1
                
        self.LoadSetting()        
                
    def AddChamberFrameLayout(self, row, col):
        #Chamber selection
        widget_chamber = QtWidgets.QWidget()
        group_chamber = QtWidgets.QGroupBox(widget_chamber)                
        #group_chamber.setFrameShape(QtWidgets.QFrame.StyledPanel)
        group_chamber.setFixedSize(QtCore.QSize(550, 520))
        group_chamber.setGeometry(10, 0, 550, 420) 
        #group_chamber.setGeometry(10 + i*440 + 5*i, 0 + 200*frame_row + 5*frame_row, 440, 200)
        
        label_choose = QtWidgets.QLabel('Chamber Number:' + str(3*row + col + 1), group_chamber)
        label_choose.setFont(QtGui.QFont('Arial', 12))
        label_choose.setGeometry(10, 10, 250, 40)              
                
        label_pid = QtWidgets.QLabel('Patient ID:', group_chamber)
        label_pid.setFont(QtGui.QFont('Arial', 12))
        label_pid.setGeometry(10, 50, 100, 40)
        
        edit_pid = QtWidgets.QLineEdit(group_chamber)
        edit_pid.setGeometry(110, 50, 280, 40)
        edit_pid.setStyleSheet('background-color:white;')  
        edit_pid.setReadOnly(True)                       
        
        label_fertilizationTime = QtWidgets.QLabel('Fertilization Time:', group_chamber)
        label_fertilizationTime.setFont(QtGui.QFont('Arial', 12))
        label_fertilizationTime.setGeometry(10, 95, 160, 35)        
        edit_fertilizationTime = QtWidgets.QLineEdit(group_chamber)
        edit_fertilizationTime.setGeometry(170, 95, 160, 35)
        edit_fertilizationTime.setStyleSheet('background-color:white;')          
        #edit_fertilizationTime.setReadOnly(True)   
        
        button_import = QtWidgets.QPushButton('Import', group_chamber)
        button_import.setGeometry(395, 50, 100, 40)
        button_import.setStyleSheet('QPushButton {background-color:lightblue;border-radius: 20px;}  QPushButton:hover{color:black;background:bisque;} QPushButton:pressed {background:lightcoral}')
        button_import.clicked.connect(lambda: self.ImportData(str(3*row + col + 1)))
        
        button_calendar = QtWidgets.QPushButton(group_chamber)
        button_calendar.setGeometry(350, 95, 40, 35)
        button_calendar.setStyleSheet('background-color:lightblue;')
        button_calendar.setIcon(QtGui.QIcon('CalenderIcon.png'))
        button_calendar.setIconSize(QtCore.QSize(130,130))
        button_calendar.clicked.connect(lambda: self.SelectDate(str(3*row + col + 1),self.maunal_timeset_check))             


        # checkbox_hourminsec_mode = QtWidgets.QCheckBox('set manual',group_chamber)
        # checkbox_hourminsec_mode.setGeometry(395,100,120,35)
        # checkbox_hourminsec_mode.stateChanged.connect(self.ClickSetmanualCheckbox)
               
        label_durationTime = QtWidgets.QLabel('Duration Time:', group_chamber)
        label_durationTime.setFont(QtGui.QFont('Arial', 12))
        label_durationTime.setGeometry(10, 140, 140, 35)  

        label_startTime= QtWidgets.QLabel('Offset Time:', group_chamber)
        label_startTime.setFont(QtGui.QFont('Arial', 12))
        label_startTime.setGeometry(10, 195, 140, 35)



        

        qtime_startTime = QtWidgets.QTimeEdit(group_chamber)
        qtime_startTime.setDisplayFormat('hh:mm:ss')
        # setting geometry of the date edit
        qtime_startTime.setGeometry(200, 195, 150, 30)
        qtime_startTime.setVisible(True)
        
        # qbuttongroup_mode.setGeometry(160, 195, 140, 35) 

        

         

        edit_wellDurationTime = QtWidgets.QLineEdit(group_chamber)
        edit_wellDurationTime.setGeometry(150, 140, 90, 35)
        edit_wellDurationTime.setStyleSheet('background-color:#b2fbe5;')         
        edit_wellDurationTime.setText('000:00:00')
        edit_wellDurationTime.setAlignment(QtCore.Qt.AlignRight)
        edit_wellDurationTime.setReadOnly(True)
        button_start = QtWidgets.QPushButton('Start', group_chamber)
        button_start.setGeometry(245, 140, 100, 40)
        button_start.setStyleSheet('QPushButton {background-color:lightblue;border-radius: 20px;}  QPushButton:hover{color:black;background:bisque;} QPushButton:pressed {background:lightcoral}')
        button_start.setDisabled(True)
        button_start.clicked.connect(lambda: self.Start(str(3*row + col + 1)))
        
        button_export = QtWidgets.QPushButton('Export', group_chamber)
        button_export.setGeometry(350, 140, 100, 40)
        button_export.setStyleSheet('QPushButton {background-color:lightblue;border-radius: 20px;}  QPushButton:hover{color:black;background:bisque;} QPushButton:pressed {background:lightcoral}')
        button_export.setDisabled(True)
        button_export.clicked.connect(lambda:  self.SaveToHistory(str(3*row + col + 1)))  


        
        label_age= QtWidgets.QLabel('Age:', group_chamber)
        label_age.setFont(QtGui.QFont('Arial', 12))
        label_age.setGeometry(10, 245, 60, 35) 


        edit_age = QtWidgets.QLineEdit(group_chamber)
        edit_age.setGeometry(80, 245, 80, 35)
        edit_age.setStyleSheet('background-color:white;')  
        
        progress = QtWidgets.QProgressBar(group_chamber)
        progress.setGeometry(10, 420, 520, 25)
        progress.setMaximum(100)
        progress.setProperty("value", 0)
        #progress.setValue(50)
                       
        return widget_chamber, group_chamber   

    def  ClickSetmanualCheckbox(self,bool_show):
        for i in range(6):
            listsMyQButton=self.chambers[i].findChildren(QtWidgets.QTimeEdit)
            for j in range(len(listsMyQButton)):
                listsMyQButton[j].setEnabled(bool_show)

    # def ImportData(self, cid):
    #     listsMyQButton = self.chambers[int(cid) - 1].findChildren(QtWidgets.QPushButton)
    #     if str(listsMyQButton[0].text()) == 'Import':
    #         self.import_dialog.cid = cid
    #         self.import_dialog.show()
    #     if str(listsMyQButton[0].text()) == 'Clear':
    #         print('clear')            
    #         self.StopExtractAndAnalysis(cid)

    
    def DisableOrEnableAllElementByChamberID(self, chamber_id, set):
        listsMyQLineEdit = self.chambers[int(chamber_id) - 1].findChildren(QtWidgets.QLineEdit)
        for j in range(len(listsMyQLineEdit)):
            listsMyQLineEdit[j].setDisabled(set)
           
        listsMyQButton = self.chambers[int(chamber_id) - 1].findChildren(QtWidgets.QPushButton) 
        for j in range(len(listsMyQButton)):
            if j != 0 and j != 2:
                listsMyQButton[j].setDisabled(set)
                
        listsMySelectCellDish = self.chambers[int(chamber_id) - 1].findChildren(SelectCellDish)
        for j in range(len(listsMySelectCellDish)):
            listsMySelectCellDish[j].setDisabled(set)

    #Calendar diagon
    def SelectDate(self, chamber_id,timeset_checkbox_bool):
        # status=''
        # if timeset_checkbox_bool:
        #     status='manual set'
        # else:
        #     status='select'
        status='select'
        calendar = Calendar(status, chamber_id,self)
        calendar.show()
        calendar.exec_()    
        
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
            # self.AddOnlineOfflineMode()
            self.AddWells(sel_machine[0][1], sel_machine[0][2])   
            
    def ProcessUnixsocketMsg(self, query):
        if "check_isboundary" in query:
            print(query)
            self.UpdateWellStatus(query)
        if "percentage" in query and "dish_id" not in query:
            self.UpdateExtractProgressive(query)
        if "percentage" in query and "dish_id" in query:
            self.UpdateAnalysisProgressive(query)
            
    def UpdateWellStatus(self, query):
        #{"chamber_id":'3' , "dish_id":'1',"check_isboundary":True} 
        print(query)        
        chamber_id = query["chamber_id"]
        well_id = query["dish_id"]
        isboundary = query["check_isboundary"]
        
        if isboundary:
            self.chamber_wells[int(chamber_id) - 1][int(well_id) - 1].setEnable('d')
        else:
            self.chamber_wells[int(chamber_id) - 1][int(well_id) - 1].setEnable('t')
            
    def UpdateExtractProgressive(self, query):
        if "percentage" in query and "chamber_id" in query:
            listsMyQProgressBar = self.chambers[int(query["chamber_id"]) - 1].findChildren(QtWidgets.QProgressBar) 
            listsMyQProgressBar[0].setValue(int(query["percentage"]))
            
    def UpdateAnalysisProgressive(self, query):
        if "percentage" in query and "chamber_id" in query:
            listsMyQProgressBar = self.chambers[int(query["chamber_id"]) - 1].findChildren(QtWidgets.QProgressBar) 
            listsMyQProgressBar[0].setValue(int(query["percentage"]))
            
            if "dish_id" in query:
                listsMySelectCellDish = self.chambers[int(query["chamber_id"]) - 1].findChildren(SelectCellDish)                              
                if (int(query["dish_id"]) - 1) < len(listsMySelectCellDish) and listsMySelectCellDish[int(query["dish_id"]) - 1].status == 't':
                    listsMySelectCellDish[int(query["dish_id"]) - 1].setDisabled(False)
                    listsMySelectCellDish[int(query["dish_id"]) - 1].setEnable('f')
            
        
    #Load config        
    def LoadSetting(self):    
        print('load')    
        #Read chamber setting
        chamber_settings = self.ReadChamberConfig()
        for cid, pid in chamber_settings.items():
            listsMyQLineEdit = self.chambers[int(cid) - 1].findChildren(QtWidgets.QLineEdit)
            listsMyQLineEdit[0].setText(pid)
            listsMyQLineEdit[1].setText(datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S'))
            
            listsMyQButton = self.chambers[int(cid) - 1].findChildren(QtWidgets.QPushButton) 
            listsMyQButton[0].setText('Clear')                     
            listsMyQButton[2].setDisabled(False)        
           
            #Read well setting
            patient_setting, decision_setting, duration, timestamp = self.ReadPatientConfig(pid)
            print(patient_setting)
            print(len(self.chamber_wells[0]))
            if patient_setting != {}:
                for pcid, well_ids in patient_setting.items():                    
                    if pcid == cid:
                        for j in range(len(self.chamber_wells[0])):
                            if (j + 1) in well_ids:
                                if str(j + 1) in decision_setting['discard']:
                                    self.chamber_wells[int(pcid) - 1][j].setEnable('d')
                                if str(j + 1) in decision_setting['transfer']:
                                    self.chamber_wells[int(pcid) - 1][j].setEnable('t')
                                if str(j + 1) in decision_setting['freeze']:
                                    self.chamber_wells[int(pcid) - 1][j].setEnable('f')
                #duration
                total_time_offset = int(time.time()) - int(timestamp)                  
                duration = self.cal_time_offset(duration, total_time_offset)                               
              
                listsMyQLineEdit = self.chambers[int(cid) - 1].findChildren(QtWidgets.QLineEdit)
                #listsMyQLineEdit[2].setText(duration)
                listsMyQLineEdit[2].setText('000:00:00')                
                   
        print('read end')           
        
    #Read config file        
    def ReadChamberConfig(self): 
        path = './config/config_chamber.ini'
        self.logger.info('Read file=' + path)
        if not os.path.exists(path):
            print('Not found file=' + path) 
            self.logger.error('Not found file=' + path)                               
            return {}
        try:
            cfg = RawConfigParser()   
            cfg.read(path)
            results = {}
            for i in range(len(cfg.items('ChamberInfo'))):
                if 'chamber_' + str(i + 1) in [item[0] for item in cfg.items('ChamberInfo')]:
                    setting = cfg.get('ChamberInfo','chamber_' + str(i + 1))
                    if setting == '' or setting == '[]':
                        continue
                    results[str(i + 1)] = setting
                else:
                    print('not found chamber')
            return results
        except:
            print('Read config error')
            return {}           
    
    #Read config file        
    def ReadPatientConfig(self, pid): 
        path = './config/config_' + pid + '.ini'
        self.logger.info('Read file=' + path)
        if not os.path.exists(path):
            print('Not found file=' + path) 
            self.logger.error('Not found file=' + path)                               
            return {},{},'',''
        try:
            cfg = RawConfigParser()   
            cfg.read(path)
            well_results = {}
            duration = ''
            timestamp = ''
            for i in range(len(cfg.items('DishInfo'))):
                if 'chamber_' + str(i + 1) in [item[0] for item in cfg.items('DishInfo')]:
                    settings = cfg.get('DishInfo','chamber_' + str(i + 1))
                    if settings == '' or settings == '[]':
                        continue                                                                  
                    well_results[str(i + 1)] = [int(n) for n in settings.split(',')]
                else:
                    print('not found dish')
                
                #Set time
                if 'duration' in  [item[0] for item in cfg.items('DishInfo')]:
                    duration = cfg.get('DishInfo','duration')
                if 'timestamp' in  [item[0] for item in cfg.items('DishInfo')]:
                    timestamp = cfg.get('DishInfo','timestamp')
            
            #Show results        
            decision_results = {}
            for i in range(len(cfg.items('DecisionInfo'))):
                if 'discard' in [item[0] for item in cfg.items('DecisionInfo')]:
                    settings = cfg.get('DecisionInfo','discard')                    
                    decision_results['discard'] = settings.split(',')
                if 'transfer' in [item[0] for item in cfg.items('DecisionInfo')]:
                    settings = cfg.get('DecisionInfo','transfer')                    
                    decision_results['transfer'] = settings.split(',')
                if 'freeze' in [item[0] for item in cfg.items('DecisionInfo')]:
                    settings = cfg.get('DecisionInfo','freeze')                    
                    decision_results['freeze'] = settings.split(',')
            return well_results, decision_results, duration, timestamp
        except:
            print('error:' + str(sys.exc_info()[1]))
            return {},{},'', ''            
        print('read p end')
        
    #write config file        
    def WriteChamberConfig(self, cid, pid): 
        path = './config/config_chamber.ini'
        self.logger.info('Read file=' + path)
        if not os.path.exists(path):
            print('Not found file=' + path) 
            self.logger.error('Not found file=' + path)                               
            return 
        try:
            cfg = RawConfigParser()   
            cfg.read(path)            
            for i in range(len(cfg.items('ChamberInfo'))):
                if 'chamber_' + str(i + 1) in [item[0] for item in cfg.items('ChamberInfo')]:
                    print(cid, str(i + 1))
                    if str(cid) == str(i + 1):
                        cfg.set('ChamberInfo','chamber_' + str(i + 1), pid)  
                        with io.open(path, 'w') as f:
                            cfg.write(f)
                        break
        except:
            print('chamber config write error')           
            
    #write config file        
    def WritePatientConfig(self, cid, pid, dish_list): 
        path = './config/config_' + pid + '.ini'
        self.logger.info('Read file=' + path)
        if not os.path.exists(path):
            try:
            #if True:
                cfg = RawConfigParser()
                cfg.add_section('DishInfo')
                for i in range(6):
                    if str(cid) == str(i + 1):
                        cfg.set('DishInfo', 'chamber_' + str(i + 1), ','.join(dish_list)) 
                    else:
                        cfg.set('DishInfo', 'chamber_' + str(i + 1), '') 
                cfg.set('DishInfo', 'duration', '000:00:00') 
                cfg.set('DishInfo', 'timestamp', str(int(time.time())))
                cfg.add_section('DecisionInfo')
                cfg.set('DecisionInfo', 'discard', '')
                cfg.set('DecisionInfo', 'transfer', ','.join(dish_list))
                cfg.set('DecisionInfo', 'freeze', '')
                with io.open(path, 'w') as f:
                    cfg.write(f)
            except:
                print('config write error')
                     
              
    #write config file        
    def WritePatientTimeToConfig(self, cid, pid): 
        listsMyQLineEdit = self.chambers[int(cid) - 1].findChildren(QtWidgets.QLineEdit)
        duration = str(listsMyQLineEdit[2].text())  
        if duration == None:
            return
        
        path = './config/config_' + pid + '.ini'
        self.logger.info('Read file=' + path)
        if not os.path.exists(path):
            print('Not found file=' + path) 
            self.logger.error('Not found file=' + path)                               
            
        try:
            cfg = RawConfigParser()
            cfg.read(path)            
            if 'duration' in  [item[0] for item in cfg.items('DishInfo')]:
                cfg.set('DishInfo', 'duration', duration)
            if duration != '000:00:00':
                if 'timestamp' in  [item[0] for item in cfg.items('DishInfo')]:
                    cfg.set('DishInfo', 'timestamp', str(int(time.time())))
            with io.open(path, 'w') as f:
                cfg.write(f)
            print('succ save')
        except:
            pass
                
    #Export to history
    def SaveToHistory(self, chamber_id):   
        self.export_dialog = ExportDialog(self)       
        #Process data to history    
        listsMyQLineEdit = self.chambers[int(chamber_id) - 1].findChildren(QtWidgets.QLineEdit)
        pid = str(listsMyQLineEdit[0].text())
        date = str(listsMyQLineEdit[1].text())
        if pid != '' and date != '':
            #move_select_cham_dish_folder(pid, date, int(chamber_id))
            #clear_cham_dish_data_csv(int(chamber_id))
            export_thread = ExportThread(pid, chamber_id, date, self)
            export_thread.start()
            self.export_dialog.exec_()

        #Clear element
        listsMyQLineEdit = self.chambers[int(chamber_id) - 1].findChildren(QtWidgets.QLineEdit)
        listsMyQLineEdit[0].setText('')
        listsMyQLineEdit[1].setText('')
        listsMyQLineEdit[2].setText('000:00:00')
        
        listsMyQButton = self.chambers[int(chamber_id) - 1].findChildren(QtWidgets.QPushButton)      
        listsMyQButton[0].setText('Import')  
        
        listsMyQProgressBar = self.chambers[int(chamber_id) - 1].findChildren(QtWidgets.QProgressBar) 
        listsMyQProgressBar[0].setValue(0)
            
        for i in range(len(self.chamber_wells[0])):                    
            self.chamber_wells[int(chamber_id) - 1][i].setEnable('c')  
            
        #pid config       
        path = './config/config_' + pid + '.ini'        
        self.WriteChamberConfig(chamber_id, '')
        if os.path.isfile(path):
            os.remove(path)
            
    def Start(self, chamber_id):
        self.StartTimeCount(chamber_id)
        self.StartAnalysis(chamber_id) 
        
    def StartTimeCount(self, chamber_id):    
        listsMyQLineEdit = self.chambers[int(chamber_id) - 1].findChildren(QtWidgets.QLineEdit)
        time_thread_cids = [int(th.chamber_id) for th in self.threads]
        if int(chamber_id) in time_thread_cids:
            idx = time_thread_cids.index(int(chamber_id))
            self.threads[idx].Continue()
        else:
            cth = TimeCountThread(listsMyQLineEdit[2], chamber_id, self)       
            cth.start()
            self.threads.append(cth)  
        
        listsMyQButton = self.chambers[int(chamber_id) - 1].findChildren(QtWidgets.QPushButton)
        #listsMyQButton[0].setDisabled(True)
        #listsMyQButton[2].setDisabled(True)
        
        listsMyQProgressBar = self.chambers[int(chamber_id) - 1].findChildren(QtWidgets.QProgressBar) 
        listsMyQProgressBar[0].setValue(0)       
        
    def StartAnalysis(self, chamber_id):     
        print('StartAnalysis')
        self.analysis_embryo.PutChamberID(chamber_id)
        
    def cal_time_offset(self, duration, offset):        
        if duration == '000:00:00':
            return '000:00:00'        
            
        time = str(duration).split(':')
        hr = int(time[0])
        mins = int(time[1])
        sec = int(time[2])
        new_mins = mins
        new_sec = sec        
        while offset > 0:
            new_sec += 1
            if new_sec >= 60:
                new_sec = 0            
                new_mins = new_mins + 1
            if new_mins >=60:
                new_mins = 0
                hr += 1            
            offset = offset - 1
        return str(hr).zfill(3) + ':' + str(new_mins).zfill(2) + ':' + str(new_sec).zfill(2)
        
    def GetCurrentPatientIDs(self):
        pids_history = []
        history_dirs = os.listdir(self.mnt_history_path)        
        for dd in history_dirs:
            if os.path.isdir(self.mnt_history_path + dd):
                pids_history.append(dd)
         
        pids = []
        for i in range(len(self.chambers)): 
            listsMyQLineEdit = self.chambers[i].findChildren(QtWidgets.QLineEdit)
            if str(listsMyQLineEdit[0].text()) != '':
                pids.append(str(listsMyQLineEdit[0].text()))        
        
        return pids_history + list(set(pids) - set(pids_history)) 
       
    def ImportData(self, cid):
        listsMyQButton = self.chambers[int(cid) - 1].findChildren(QtWidgets.QPushButton)
        if str(listsMyQButton[0].text()) == 'Import':
            self.import_dialog.cid = cid
            self.import_dialog.show()
        if str(listsMyQButton[0].text()) == 'Clear':
            print('clear')            
            self.StopExtractAndAnalysis(cid)
    
    #Dialog call    
    def CallExtractSqlite(self, patient_id, chamber_id):
        print(patient_id)
        print(chamber_id)
        if str(patient_id) == '':
            return           
            
        #Button
        listsMyQButton = self.chambers[int(chamber_id) - 1].findChildren(QtWidgets.QPushButton)
        listsMyQButton[0].setText('Clear')  
            
        listsMyQLineEdit = self.chambers[int(chamber_id) - 1].findChildren(QtWidgets.QLineEdit)
        listsMyQLineEdit[0].setText(patient_id)
        self.DisableOrEnableAllElementByChamberID(chamber_id, True)
        
        thread = ExtractSqliteThread(str(patient_id), str(chamber_id), self.unix_socket_client, self)
        thread.finished.connect(self.excute_extract_sqlite)
        thread.start()             
        self.extract_thread.append(thread)
        
        self.StartTimeCount(chamber_id)  
     
    #Finish extract sqlite    
    def excute_extract_sqlite(self, patient_id, chamber_id):       
        #Search directorys for image file exist    
        print('Finish extract sqlite')     
        well_ids = []        
        dish_dirs = os.listdir('./data/ori_img/cham' + str(chamber_id))
        for dd in dish_dirs:
            print (dd)
            if os.path.isdir('./data/ori_img/cham' + str(chamber_id) + '/' + dd):
                files = os.listdir('./data/ori_img/cham' + str(chamber_id) + '/' + dd)                
                if len(files) > 0:
                    well_ids.append(int(dd[4:])) 
     
        #Write to config     
        well_ids.sort()
        well_ids = [str(i) for i in well_ids]
        self.WritePatientConfig(chamber_id, patient_id, well_ids)
        self.WriteChamberConfig(chamber_id, patient_id)
        for i,d in enumerate(well_ids):
            self.chamber_wells[int(chamber_id) - 1][int(d) - 1].setEnable('t')        
               
        self.DisableOrEnableAllElementByChamberID(chamber_id, False)    
        #duration
        listsMyQLineEdit = self.chambers[int(chamber_id) - 1].findChildren(QtWidgets.QLineEdit)        
        listsMyQLineEdit[1].setText(datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S'))
        #listsMyQLineEdit[2].setText('000:00:00')
        
        #Remove extract thread       
        for eth in self.extract_thread:
            if eth.chamber_id == str(chamber_id):
                self.extract_thread.remove(eth)       
               
        #Start analysis        
        self.StartAnalysis(chamber_id)
    
    #Stop    
    def StopExtractAndAnalysis(self, chamber_id):
        #Stop and remove extract thread        
        for eth in self.extract_thread:
            if eth.chamber_id == str(chamber_id):
                eth.Stop()
                self.extract_thread.remove(eth)
                break  
            
        self.analysis_embryo.StopAnalysisChamberID(chamber_id)                   
        self.ClearChamber(chamber_id)        
        
    def ClearChamber(self, chamber_id):
        dish_dirs = os.listdir('./data/ori_img/cham' + str(chamber_id))
        for dd in dish_dirs:            
            if os.path.isdir('./data/ori_img/cham' + str(chamber_id) + '/' + dd):
                files = os.listdir('./data/ori_img/cham' + str(chamber_id) + '/' + dd)                 
                for f in files:
                    os.remove('./data/ori_img/cham' + str(chamber_id) + '/' + dd + '/' + f)
                    print (f)

        dish_dirs = os.listdir('./data/crop_img/cham' + str(chamber_id))
        for dd in dish_dirs:            
            if os.path.isdir('./data/crop_img/cham' + str(chamber_id) + '/' + dd):
                files = os.listdir('./data/crop_img/cham' + str(chamber_id) + '/' + dd)                 
                for f in files:
                    os.remove('./data/crop_img/cham' + str(chamber_id) + '/' + dd + '/' + f)
                    print (f)        
                    
        dish_dirs = os.listdir('./csv/cham' + str(chamber_id))
        for dd in dish_dirs:            
            if os.path.isdir('./csv/cham' + str(chamber_id) + '/' + dd):
                files = os.listdir('./csv/cham' + str(chamber_id) + '/' + dd)                 
                for f in files:
                    os.remove('./csv/cham' + str(chamber_id) + '/' + dd + '/' + f)
                    print (f)
                    
        #Stop count
        for th in self.threads:
            print ('th=' + str(th.chamber_id))
            if int(th.chamber_id) == int(chamber_id):
                print ('pause=' + str(chamber_id))
                th.Pause()           
                     
        print('chid' + str(chamber_id))            
        #Gui element
        listsMyQLineEdit = self.chambers[int(chamber_id) - 1].findChildren(QtWidgets.QLineEdit)
        patient_id = str(listsMyQLineEdit[0].text())       
        listsMyQLineEdit[0].setText('')
        listsMyQLineEdit[1].setText('')
        listsMyQLineEdit[2].setText('000:00:00')
        # print('listsMyQLineEdit[3]')
        # listsMyQLineEdit[3].setText('')
        listsMyQButton = self.chambers[int(chamber_id) - 1].findChildren(QtWidgets.QPushButton)      
        listsMyQButton[0].setText('Import')
        
        listsMyQProgressBar = self.chambers[int(chamber_id) - 1].findChildren(QtWidgets.QProgressBar) 
        listsMyQProgressBar[0].setValue(0)
                    
        for i in range(len(self.chamber_wells[0])):                    
            self.chamber_wells[int(chamber_id) - 1][i].setEnable('c')   
            
        #Clear config         
        self.WriteChamberConfig(chamber_id, '')
        path = './config/config_' + patient_id + '.ini'
        print('remove=' + path)
        if os.path.isfile(path):
            print('remove ok=' + path)
            os.remove(path)
        
        
    def ReadyExport(self, chamber_id):
        listsMySelectCellDish = self.chambers[int(chamber_id) - 1].findChildren(SelectCellDish)
        for j in range(len(listsMySelectCellDish)):
            listsMySelectCellDish[j].setDisabled(False)
        
        listsMyQButton = self.chambers[int(chamber_id) - 1].findChildren(QtWidgets.QPushButton) 
        #listsMyQButton[0].setDisabled(False)
        listsMyQButton[2].setDisabled(True)
        listsMyQButton[3].setDisabled(False)
        
        #Stop time counter
        for th in self.threads:
            if int(th.chamber_id) == int(chamber_id):   
                th.Pause()                
        
    def closeEvent(self, event):
        self.unix_socket_server.Stop()
        self.analysis_embryo.Stop()
        self.import_dialog.close()
        #Read chamber setting
        #chamber_settings = self.ReadChamberConfig()
        #for cid, pid in chamber_settings.items():            
        #    self.WritePatientTimeToConfig(cid, pid)

        #Stop time count
        for th in self.threads:
            th.Stop()
                    
        time.sleep(1)
        
  
        
        
        
        
