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
from EmbryoBoxInfo import EmbryoHistoryInfoTableBox,EmbryoHistoryInfoTable
from Ui_Function import * 
from ReadSqlDataHistoryPath  import ReadSqlInfoPath


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
        _,self.mnt_history_path = ReadSqlInfoPath()

        self.excel_output_path = './excel_output/'
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
        self.button_save.clicked.connect(self.WriteTableInfoToCsv)
        # self.button_save.setDisabled(True)
        

        self.button_load = QtWidgets.QPushButton('Load', self)
        self.button_load.setGeometry(1600, 10, 80, 40)
        self.button_load.setStyleSheet('QPushButton {background-color:lightblue;border-radius: 20px;}  QPushButton:hover{color:black;background:bisque;} QPushButton:pressed {background:lightcoral}')
        self.button_load.clicked.connect(self.FileLoad)
        # self.button_save.setDisabled(True)


        
        
        self.embryo_info_qframe = QtWidgets.QFrame(self)
        # self.embryo_info_qframe = QtWidgets.QFrame(self)        
        self.embryo_info_qframe.setFrameShape(QtWidgets.QFrame.StyledPanel)
        # self.embryo_info_qframe.setGeometry(10, 5, 1580, 60)
        self.embryo_info_qframe.setGeometry(QtCore.QRect(10, 70, 1910, 900))
        self.AddTableBox(self.embryo_info_qframe)
        
    

    def ReadTableInfoFromCsv(self,table,patient_id,timelapse_id_time,tabel_index):
        csv_table_title_path = os.path.join(self.excel_output_path,patient_id +'_'+timelapse_id_time+'.csv')
        # print('csv_table_title_path',csv_table_title_path)
        if os.path.isfile(csv_table_title_path):
            df = pd.read_csv(csv_table_title_path, encoding='utf-8-sig')
            # print(df)
            # print(df['PGS'])
            # print(df['Command'])
            # print(df.iloc[1][20])

            # if {'Command'}.issubset(df.columns):
            #     print('Command',df['Command'])
            if 'PGS' in df:
                # print(df['PGS'])
                for i in range(14):
                    if table.cellWidget(i+2, 20) is not None:
                        # print(table.cellWidget(i+2, 20))
                        # print(str(df['PGS'].values[i]),i)
                        table.cellWidget(i+2, 20).setCurrentText(str(df['PGS'].values[i]))


                
                # for i in range(2,14):

                    
                #     if df.iloc[i][20] is not None:
                #         print('df item',df.iloc[i][20])
                #         print('i',i)
                #         if table.cellWidget(i+1, 20) is not None:
                            
                #             table.cellWidget(i+1, 20).setCurrentText(str(df.iloc[i][20]))



    def WriteTableInfoToCsv(self):
        
        Command_temp_list = []
        
        for i in range(len(self.embryo_info_array)):
            table = self.embryo_info_array[i]

            table_title_name = table.item(0,0).text()
            if table_title_name!='':
                csv_table_title_path = os.path.join(self.excel_output_path,self.selector_pid.currentText() +'_'+table_title_name+'.csv')

                #read csv command line items
                if os.path.exists(csv_table_title_path):
               
                    df_csv = pd.read_csv(csv_table_title_path, encoding='utf-8-sig')
                    if {'Command'}.issubset(df_csv.columns):
                        Command_temp_list=df_csv['Command'].values.tolist()
                        
                
            
                data_pd = pd.DataFrame(columns=['Well id','Final score','rank','Age','PN_Fading','2cell','3cell','4cell','5cell','6cell','7cell','8cell','Morula','Blastocyst','PNnum','Location','Morphological','Division','Time','ICM','TE','PGS','Command'],index=list(range(14)))
                for row in range(2,table.rowCount()):
                    for column in range(table.columnCount()):
                        if column==20:
                            
                            if table.cellWidget(row, column) is not None:
                                data_pd.iloc[row-2, column+1] = table.cellWidget(row, column).currentText()
                        else:
                            
                            data_pd.iloc[row-2, column] = table.item(row, column).text()
                if len(Command_temp_list)!=0:
                    
                    data_pd['Command']=Command_temp_list
                    
                data_pd.to_csv(csv_table_title_path,index=False,encoding='utf_8_sig')



                       
            #     with open(csv_table_title_path, 'w',encoding='gb2312') as stream:                  # 'w'
            #         writer = csv.writer(stream, lineterminator='\n')          # + , lineterminator='\n'
            #         for row in range(1,table.rowCount()):
            #             print('table row count',table.rowCount())
            #             rowdata = []
            #             for column in range(1,table.columnCount()):
            #                 if   column ==20 and row !=1:
            #                     # test=table.item(row,column)
            #                     if table.cellWidget(row, column) is not None:
            #                         test = table.cellWidget(row, column).currentText()
            #                         # print(test)
            #                         item =test
            #                         rowdata.append(item)
            #                 else:
                                
            #                     item = table.item(row, column)
            #                     if item is not None:
            # #                       rowdata.append(unicode(item.text()).encode('utf8'))
            #                         rowdata.append(item.text())                   # +
            #                         # print('rowdata',item.text(),row,column)
            #                     else:
            #                         rowdata.append('')

            #             if len(Command_temp_list)!=0:
                            
            #                 if row ==1:
            #                     rowdata.append('Command')
            #                 else:

            #                     print(Command_temp_list[row-2])
            #                     rowdata.append(Command_temp_list[row-2])
            #             else:
            #                 if row==1:
            #                     rowdata.append('Command') 
                                    
                                

            #             writer.writerow(rowdata)

    def AddTableBox(self, parent):
        self.embryo_info_array = []
        for i in range(2):
            

            self.table = EmbryoHistoryInfoTable(i, parent)  
            self.table.setGeometry(0, i*400+5, 1910, 400)
            self.embryo_info_array.append(self.table)         

        # vert_lay = QtWidgets.QGridLayout(parent)         
        # self.embryo_info_array = []
        # for j in range(2):
            
        #         #if len(self.embryo_info_array) < self.well_number:
        #         embryo_info = EmbryoHistoryInfoTableBox(j + 1)                  
        #         self.embryo_info_array.append(embryo_info)  
        #         vert_lay.addWidget(embryo_info, j, 0 , 1, 1)              
        # vert_lay.setSpacing(1)
    
    def ReadAgeFromIni(self,pid):
        ini_dir_path = os.path.join(self.mnt_history_path,pid)
        # print('ini_dir_path',ini_dir_path)

        for filename in os.listdir(ini_dir_path):
            # print('filename',filename)
            if filename.endswith('.ini'):
                ini_path = os.path.join(ini_dir_path,filename)
                # print('ini_path',ini_path)
                self.logger.info('Read file=' + ini_path)
                # if not os.path.exists(path):
                cfg = RawConfigParser()  
                # if os.path.exists(ini_path):
                cfg.read(ini_path)   
                age = cfg.get('PitentInfo','age') 
                return age
            # else:
            #     return ''

            
        
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



            #Clear all table
            for tableclean in self.embryo_info_array:
                tableclean.CleanAllText()

                
            for tabel_index,timelapse_id_time in enumerate(self.selector_files.getCheckItem()):

                # print(tabel_index)
                timelapse_id = timelapse_id_time.split('->')[0]
                fertilizationtime = timelapse_id_time.split('->')[1]
                get_dic= search_history_csv(str(self.selector_pid.currentText()), timelapse_id,fertilizationtime)
                # print('get dict:',get_dic)
                self.InsertInfomationToTable(str(self.selector_pid.currentText()),timelapse_id,fertilizationtime ,timelapse_id_time,tabel_index, get_dic)
                
                
                
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
                      
    # search select info file and insert to table
    def InsertInfomationToTable(self, patient_id,timelapse_id, date, timelapse_id_time ,tabel_index, dict_msg):   


        morphological_choices = ['Refractile Body', 'Central Darkness','Abnormality','Large pb']
        morphological_simple_choices=['RB','CD','ABN','Lpb']
        divisiontime_choices = ['Asymmetry', 'Multinucleation', 'Reverse Cleavage', 'Direct Uneven Cleavage','Vacuolated','Chaos']
        divisiontime_simple_choices=['As','Mul','RC','DUC','Va','Ch']    

        pgs_combobox_choices=['Euploid','Aneuploid','Low Mosaic','High Mosaic']
        
        
        table = self.embryo_info_array[tabel_index]

        # get select timelapse->time name and put in title
        table.SetItemTitle(0, 0, timelapse_id_time,readonly=True)
        
        table.SetPidDate(patient_id,timelapse_id, date)
        # table.CleanAllText()
        # print('tabel index',tabel_index)
        # print('dict msg',dict_msg["DishList"][0].keys())
        dish_number_max = 14

        #get score rank list
        rank_list = []
        rank_index_list = []
        for dish_number in range(1,dish_number_max+1):
            for dic_dishid in range(len(dict_msg["DishList"])):
                if dict_msg["DishList"][dic_dishid]['DishId']==str(dish_number):
                    if dict_msg["DishList"][dic_dishid]['OtherInfo']!={}:
                        if dict_msg["DishList"][dic_dishid]['OtherInfo']['Total_Score'] !='':

                            rank_list.append(float(dict_msg["DishList"][dic_dishid]['OtherInfo']['Total_Score'] ))
                        else:
                            rank_list.append(-1)
                    else:
                        rank_list.append(-1)
        
        
        rank_index_list=sorted(range(len(rank_list)),key=lambda k:rank_list[k],reverse=True)
        rank_index_list = [i+1 for i in rank_index_list ]
        
        dic_rank = {}
        for i in rank_index_list:
            dic_rank[str(i)]=rank_index_list.index(i)

        age = self.ReadAgeFromIni(patient_id)
        
        #put info into table
        for dish_number in range(1,dish_number_max+1):
            for dic_dishid in range(len(dict_msg["DishList"])):
                # print('dict_msg["DishList"][dic_dishid]',dict_msg["DishList"][dic_dishid])
                if dict_msg["DishList"][dic_dishid]['DishId']==str(dish_number):
                    
                    
                    # each stage division time fill in table
                    if dict_msg["DishList"][dic_dishid]['Info']!={}:
                        
                        # print(dict_msg["DishList"][dic_dishid]['Info']['PN_Fading'])
                        self.set_embryo_table_item(table, dish_number+1, 4,dict_msg["DishList"][dic_dishid]['Info']['PN_Fading'] )
                        self.set_embryo_table_item(table, dish_number+1, 5,dict_msg["DishList"][dic_dishid]['Info']['t2'] )
                        self.set_embryo_table_item(table, dish_number+1, 6,dict_msg["DishList"][dic_dishid]['Info']['t3'] )
                        self.set_embryo_table_item(table, dish_number+1, 7,dict_msg["DishList"][dic_dishid]['Info']['t4'] )
                        self.set_embryo_table_item(table, dish_number+1, 8,dict_msg["DishList"][dic_dishid]['Info']['t5'] )
                        self.set_embryo_table_item(table, dish_number+1, 9,dict_msg["DishList"][dic_dishid]['Info']['t6'] )
                        self.set_embryo_table_item(table, dish_number+1, 10,dict_msg["DishList"][dic_dishid]['Info']['t7'] )
                        self.set_embryo_table_item(table, dish_number+1, 11,dict_msg["DishList"][dic_dishid]['Info']['t8'] )
                        self.set_embryo_table_item(table, dish_number+1, 12,dict_msg["DishList"][dic_dishid]['Info']['Morula'] )
                        self.set_embryo_table_item(table, dish_number+1, 13,dict_msg["DishList"][dic_dishid]['Info']['Blas'] )
                        # print('dish number',dish_number)
                        self.set_embryo_table_item(table, dish_number+1, 20,'', readonly=False)
                        table.SetPgsChoices(pgs_combobox_choices,dish_number)
                        

                    if dict_msg["DishList"][dic_dishid]['OtherInfo']!={}:

                        self.set_embryo_table_item(table, dish_number+1, 15,dict_msg["DishList"][dic_dishid]['OtherInfo']['cbo_Loction'] )
                        self.set_embryo_table_item(table, dish_number+1, 14,dict_msg["DishList"][dic_dishid]['OtherInfo']['cbo_PN'] )
                        
                        morpho_simple = self.ListItemAbbreviation(morphological_choices,dict_msg["DishList"][dic_dishid]['OtherInfo']['rdo_Morphological'],morphological_simple_choices)

                        self.set_embryo_table_item(table, dish_number+1, 16, morpho_simple)
                        divisiontime_simple = self.ListItemAbbreviation(divisiontime_choices,dict_msg["DishList"][dic_dishid]['OtherInfo']['rdo_DivisionTime'],divisiontime_simple_choices)
                        self.set_embryo_table_item(table, dish_number+1, 17,divisiontime_simple )
                        self.set_embryo_table_item(table, dish_number+1, 18,dict_msg["DishList"][dic_dishid]['OtherInfo']['cbo_ICM'] )
                        self.set_embryo_table_item(table, dish_number+1, 19,dict_msg["DishList"][dic_dishid]['OtherInfo']['cbo_TE'] )
                        self.set_embryo_table_item(table, dish_number+1, 1,dict_msg["DishList"][dic_dishid]['OtherInfo']['Total_Score'] )
                        self.set_embryo_table_item(table, dish_number+1, 3,age )
                        if dict_msg["DishList"][dic_dishid]['OtherInfo']['Total_Score']!='':
                            # self.set_embryo_table_item(table, dish_number+1,2,rank_index_list[dish_number-1])
                            # print(dict_msg["DishList"][dic_dishid]['OtherInfo']['Total_Score'])
                            # print('dic dishid',dish_number)
                            # print('dic',dic_rank[str(dish_number)])
                            self.set_embryo_table_item(table, dish_number+1,2,dic_rank[str(dish_number)]+1)
            
        self.ReadTableInfoFromCsv(table,patient_id,timelapse_id_time,tabel_index)              

        
    def ListItemAbbreviation(self,combobox_list,ori_list,abbreviation_list):
        output_str = ''
        if ori_list!=0:
            for i in range(len(ori_list)):
                abbre=abbreviation_list[combobox_list.index(ori_list[i])]
                output_str =output_str+abbre+','

            return output_str

        else:
            return ''
    
    def set_embryo_table_item(self, table, row, col, value, readonly=True):
        if str(value).lower() != 'nan':
            table.SetItem(row, col, value, readonly)        
        
    def SaveTableChangeToFile(self):       
        for i,table in enumerate(self.embryo_info_array):
            if i < self.well_number:
                table.SaveChangeItem()
               





#video player function use part --------------------------------------------------------

    # def keyPressEvent(self, event):    
    #     position = self.position_val
    #     if event.key() == QtCore.Qt.Key_Left:
    #         position = self.position_val - 1000/6
    #     if event.key() == QtCore.Qt.Key_Right:
    #         position = self.position_val + 1000/6
    #     self.positionChanged(position)
    #     self.setPosition(position)
       
    # #Search file to show    
    # def initSelector(self):
    #     #self.logger.info(self.Directory + pid)        
    #     folders = [f for f in os.listdir('./') if os.path.isdir(f)]
    #     folders.sort()                 
    #     self.selector_folder.clear()
    #     for f in folders:
    #         self.selector_folder.addItem(f)        
        
    # #Set video source    
    # def initSource(self, pid, chid, wid):
    #     self.LoadEmbryoDataPnNew(pid, chid, wid)
    #     #img_to_video(chid, wid)
        
    #     path = os.path.abspath(load_video_path_with_7fp(pid, chid, wid, int(str(self.selector_fp.currentText())) - 1))
    #     #path = os.path.abspath('./video/MTL-0245-11FD-1774/cham1/dish10/MTL-0245-11FD-1774_cham1_dish10_FP0.avi')
        
    #     if not path:
    #         return
    #     self.playButton.setEnabled(True)
    #     #print(path)
    #     self.player.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(path)))
        
    #     self.patient_id = str(pid)
    #     self.chamber_id = str(chid)
    #     self.well_id = str(wid)
        


    
    # #Play video
    # def play(self):               
    #     if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
    #         self.player.pause()
    #     else:
    #         self.player.play()
            
    # def mediaStateChanged(self, state):        
    #     if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
    #         self.playButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPause))            
    #     else:
    #         self.playButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
    
    # #Video position                
    # def positionChanged(self, position):
    #     self.slider.setValue(position)
    #     self.position_val = position
      
    # def durationChanged(self, duration):
    #     self.slider.setRange(0, duration)    
    #     self.slider.setTickInterval(1000/6)     
    #     self.slider.setSingleStep(1000/6)   

    # def setPosition(self, position):
    #     self.player.setPosition(position)            
                
    
    # def handleError(self):
    #     #self.playButton.setEnabled(False)
    #     #self.errorLabel.setText("Error: " + self.player.errorString())
    #     print("Error: " + self.player.errorString())    
    
                    
        