# -*- coding: utf-8 -*-
"""
Created on Mon May 25 14:55:45 2020

@author: minghung
"""
from PyQt5 import QtCore, QtWidgets, QtGui 
from Ui_Function import * 

class EmbryoImageLabel(QtWidgets.QLabel):
    def __init__(self, w, h, infos, antialiasing=False):
        super(EmbryoImageLabel, self).__init__()
        self.infos = infos
        self.Antialiasing = antialiasing        
        self.setFixedSize(w,h)
        self.radius = w/2
  
      
class EmbryoInfoTable(QtWidgets.QTableWidget):
    def __init__(self, row, column, labels, parent=None):
        super(EmbryoInfoTable, self).__init__(row * 4, column, parent)        
        self.setStyleSheet('background-color:white; font-size: 12pt;')         
        self.verticalScrollBar().setStyleSheet("QScrollBar:vertical {Background-color:lightgray;}")          
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.labels = labels
        self.column_labels = ['Analysis' , 'View']
        self.row_labels = ['', 'Grade', 'Time', 'Score']
        self.row_labels_ = ['', 'Time', 'ICM', 'TE']
        self.chid = 0
        self.wid = 0      
        self.selector_icm = None
        self.selector_te = None
        
        
        for i in range(row):    
            #Column 0      
            item_data = QtWidgets.QTableWidgetItem(self.labels[i])
            item_data.setBackground(QtGui.QColor(245, 198, 240))
            item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_data.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(i * 4, 0, item_data)      
            
            for j in range(4):
                self.setRowHeight(4*i + j, 42)
                #Column 1                 
                if 'Morula' in self.labels and 'Blastocyst' in self.labels and (i == row - 1):
                    item_data = QtWidgets.QTableWidgetItem(self.row_labels_[j])
                    item_data.setBackground(QtGui.QColor(218,241,252))
                    item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    item_data.setFlags(QtCore.Qt.ItemIsEnabled)
                    self.setItem(4*i + j, 1, item_data)  
                else:
                    item_data = QtWidgets.QTableWidgetItem(self.row_labels[j])
                    item_data.setBackground(QtGui.QColor(218,241,252))
                    item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    item_data.setFlags(QtCore.Qt.ItemIsEnabled)
                    self.setItem(4*i + j, 1, item_data)  
                
            #Row 1   
            for j in range(2):
                item_data = QtWidgets.QTableWidgetItem(self.column_labels[j])
                item_data.setBackground(QtGui.QColor(218,241,252))
                item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item_data.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(4*i, 2 + j, item_data)    
            
            self.setSpan(4*i, 0, 4, 1)             
        self.setColumnWidth(0, 117)

    def AddRow(self, row, embryo_label_anaylsis, embryo_label_view):              
        #Column 3               
        if 'ICM' in embryo_label_anaylsis.infos:            
            for i, info in enumerate(embryo_label_anaylsis.infos):                
                if 'ICM' in info or 'TE' in info: 
                    widget = QtWidgets.QWidget() 
                    print(info)
                    #Analysis
                    if 'ICM' in info:  
                        print('b=' + info)
                        self.selector_icm = QtWidgets.QComboBox(widget)                                 
                        self.selector_icm.setStyleSheet("background-color:#55cbcd;selection-background-color: darkblue") 
                        self.selector_icm.setGeometry(20, 5, 50, 30)   
                        for a in ['A', 'B', 'C']:
                            self.selector_icm.addItem(a)
                        self.SetIcmTe()
                        self.selector_icm.currentIndexChanged.connect(self.WriteInfoToCsv)                        
                    else:
                        self.selector_te = QtWidgets.QComboBox(widget)                         
                        self.selector_te.setStyleSheet("background-color:#55cbcd;selection-background-color: darkblue") 
                        self.selector_te.setGeometry(20, 5, 50, 30)   
                        for a in ['A', 'B', 'C']:
                            self.selector_te.addItem(a)
                        self.SetIcmTe()
                        self.selector_te.currentIndexChanged.connect(self.WriteInfoToCsv)
                    self.setCellWidget(row * 4 + i + 1, 2, widget)
                    
                    #View
                    item_data = QtWidgets.QTableWidgetItem('-')
                    item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    self.setItem(row * 4 + i + 1, 3, item_data)                   
                    
                else:
                    #Time
                    #Analysis
                    item_data = QtWidgets.QTableWidgetItem(info)
                    item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    self.setItem(row * 4 + i + 1, 2, item_data)
                    #View
                    item_data = QtWidgets.QTableWidgetItem(embryo_label_view.infos[i])
                    item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    self.setItem(row * 4 + i + 1, 3, item_data)                   
            
        else:
            for i, info in enumerate(embryo_label_anaylsis.infos):
                #Analysis
                item_data = QtWidgets.QTableWidgetItem(info)
                item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item_data.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(row * 4 + i + 1, 2, item_data)
                
                #View
                item_data = QtWidgets.QTableWidgetItem(embryo_label_view.infos[i])
                item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item_data.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(row * 4 + i + 1, 3, item_data)
                                         
            
    def DeleteRow(self, row_number):
        self.removeRow(row_number)  
        
    def SetChamberIdPid(self, chid, wid):
        self.chid = int(chid)
        self.wid = int(wid)
        
    def SetIcmTe(self):
        icm, te = read_analy_csv_icm_te(self.chid, self.wid)       
        if icm != '' and self.selector_icm != None:
            idxs = [i for i,d in enumerate(['A', 'B', 'C']) if d.lower() in icm or d.upper() in icm]
            if idxs != []:
                self.selector_icm.setCurrentIndex(idxs[0])
        if te != '' and self.selector_te != None:
            idxs = [i for i,d in enumerate(['A', 'B', 'C']) if d.lower() in te or d.upper() in te]
            if idxs != []:
                self.selector_te.setCurrentIndex(idxs[0])
        
    def WriteInfoToCsv(self):
        if self.chid != 0 and self.wid != 0 and self.selector_icm != None and self.selector_te != None:
            write_analy_csv_icm_te(self.chid, self.wid, str(self.selector_icm.currentText()), str(self.selector_te.currentText()))
  



      
class EmbryoHistoryInfoTableBox(QtWidgets.QWidget):
    def __init__(self, well_id,x,y,width,height, parent=None):
        super(EmbryoHistoryInfoTableBox, self).__init__(parent)
        self.well_id = well_id
        self.table = EmbryoHistoryInfoTable(well_id, self)  
        self.table.setGeometry(x, y, width, height)        
        # self.setFixedSize(1180, 405)
        
    def SetItem(self, row, col, value, readonly):
        #print(row, col)
        #print('set=' + str(value))
        item_data = QtWidgets.QTableWidgetItem(str(value))        
        item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        # item_data.setBackground(QtGui.QColor(218,241,252))
        if readonly:
            item_data.setFlags(QtCore.Qt.ItemIsEnabled)
        self.table.setItem(row, col, item_data)
    def SetItemTitle(self, row, col, value, readonly):
        item_data = QtWidgets.QTableWidgetItem(str(value))        
        item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item_data.setBackground(QtGui.QColor(218,241,252))
        if readonly:
            item_data.setFlags(QtCore.Qt.ItemIsEnabled)
        self.table.setItem(row, col, item_data)
        
    def SetIcmTe(self):     
        self.table.SetIcmTe()

    def SetPgsChoices(self,combobox_list,dish_number):
        combo = QtWidgets.QComboBox()
        for t in combobox_list:
            combo.addItem(t)
        
        self.table.setCellWidget(dish_number+1,19,combo)
        
        
    def setDecision(self, result, prob):        
        try:
            idxs = [i for i,d in enumerate(self.table.decisions) if d.lower() == result.lower()]
            if idxs != []:
                self.table.selector_decision.setCurrentIndex(idxs[0])
            if str(prob) != '' and str(prob).lower() != 'nan':      
                self.table.label_decision_prob.setText(str(int(float(prob) * 100)) + '%')
        except:
            self.table.selector_decision.setCurrentIndex(0)
            
    def setPGS(self, result):        
        try:
            idxs = [i for i,d in enumerate(self.table.pgs) if d.lower() == result.lower()]           
            if idxs != []:
                self.table.selector_pgs.setCurrentIndex(idxs[0])                
        except:
            self.table.selector_pgs.setCurrentIndex(0)
            
    def SetPidDate(self, patient_id, timelapse_id, patient_time):
        self.table.patient_id = patient_id
        self.table.timelapse_id = timelapse_id

        self.table.patient_time = patient_time
        
    def SetChamberID(self, chamber_id):
        self.table.chamber_id = int(chamber_id)
        
    def SaveChangeItem(self):
        self.table.SaveChangeItem()

    #Clear all text in table
    def CleanAllText(self):
        col_num=len(self.table.division_status)
        row_num = len(self.table.wells_id)
        for i in range(2,row_num+2):
            for j in range(1,col_num+1):
                self.SetItem(i,j,'',True)
      
   
        
class EmbryoHistoryInfoTable(QtWidgets.QTableWidget):
    def __init__(self, well_id, parent=None):

        self.wells_id = ['well %s'%str(i) for i in range(1,15)]
        
        #self.cell_names = ['2cell', '3cell', '4cell', '5cell', '6cell', '7cell', '8cell',]
        self.division_status = ['Final score','rank','PN_Fading', '2cell', '3cell', '4cell', '5cell', '6cell', '7cell', '8cell',  'Morula', 'Blastocyst','PNnum' ,'Location','Morphological','Division Time','ICM','TE', 'PGS']        
        self.decisions = ['', 'Transfer', 'Discard', 'Freeze']
        self.dec_bcolors = ['white','lightgreen', '#ff968a', '#abdee6']
        self.pgs = ['', 'Mosaicism', 'Aneuploidy', 'Euploidy']
        super(EmbryoHistoryInfoTable, self).__init__(len(self.wells_id) + 2, len(self.division_status), parent)        
        
        self.setStyleSheet('background-color:white; font-size: 13pt;')         
        self.verticalScrollBar().setStyleSheet("QScrollBar:vertical {Background-color:lightgray;}")      
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.patient_id = ''
        self.timelapse_id=''
        self.patient_time = ''
        self.chamber_id = 0
        self.well_id = well_id
       
        # self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        # self.horizontalHeader().setSectionResizeMode(1)
        # self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
       
        self.setRowCount(len(self.wells_id) + 2)
        self.setColumnCount(len(self.division_status) + 1)
        for i in range(len(self.division_status) + 1):
            self.setRowHeight(i, 25)
        self.setRowHeight(len(self.division_status) + 1, 30)
        self.setRowHeight(len(self.division_status) + 2, 30)            
        
        # for i in range(len(self.wells_id) + 2):
        #     self.setColumnWidth(i, 30) 
          
        # #Span
        # for i in range(len(self.division_status) + 2):
        #     #if i != len(self.cell_names) + 1 and i != len(self.cell_names) + 2:
        #     self.setSpan(i, 0, 1, 2)
        #     self.setSpan(i, 2, 1, 2)
        #     self.setColumnWidth(i, 10) 
        self.setSpan(0, 0, 1, len(self.division_status) + 2)
        
        # #Blas.
        # self.setSpan(len(self.division_status) - 4, 2, 2, 2)
        
        # #Event
        # self.setSpan(len(self.division_status) - 2, 2, 1, 3)
        
        # #Finial score, decision, pgs        
        # self.setSpan(len(self.division_status) - 1, 2, 1, 3)
        # self.setSpan(len(self.division_status), 2, 1, 3)
        # self.setSpan(len(self.division_status) + 1, 2, 1, 3)        
        
        self.initContent()
        
        #self.cellChanged.connect(self.CellClicked)
        

    def initContent(self):     
        # header = self.horizontalHeader()
        # header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        # header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)    
        #Header
        item_data = QtWidgets.QTableWidgetItem('')
        item_data.setTextAlignment(QtCore.Qt.AlignHCenter)
        item_data.setFlags(QtCore.Qt.ItemIsEnabled)
        item_data.setBackground(QtGui.QColor(218,241,252))        
        self.setItem(0, 0, item_data)   


        

        
        #Title
        for i in range(len(self.division_status)):                        
            
            
            if i==1 or i ==3 or i==12 : 
                self.setColumnWidth(i, 100) 
            elif i== 14:
                self.setColumnWidth(i, 120) 
            elif i==15 or i==16: 
                self.setColumnWidth(i, 200) 
            else:
                self.setColumnWidth(i, 40) 
            item_data = QtWidgets.QTableWidgetItem(self.division_status[i])
            item_data.setTextAlignment(QtCore.Qt.AlignHCenter)
            item_data.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(1, i+1, item_data)            
        for i in range(len(self.wells_id)): 
            
            item_data = QtWidgets.QTableWidgetItem(self.wells_id[i])
            item_data.setTextAlignment(QtCore.Qt.AlignHCenter)    
            item_data.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(i + 2, 0, item_data)
        for r in range(len(self.division_status)):    
            for c in range(len(self.wells_id)): 
                item_data_empty =QtWidgets.QTableWidgetItem()
                item_data_empty.setTextAlignment(QtCore.Qt.AlignHCenter)    
                item_data_empty.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(r + 2, c+1, item_data_empty)
        



        
        # #Blas. icm te
        # frameWidget = QtWidgets.QWidget()               
        # self.selector_icm = QtWidgets.QComboBox(frameWidget)                                 
        # self.selector_icm.setStyleSheet("background-color:#55cbcd;selection-background-color: darkblue") 
        # self.selector_icm.setGeometry(20, 2, 50, 25)       
        # for a in ['', 'A', 'B', 'C']:
        #     self.selector_icm.addItem(a)                        
        # self.setCellWidget(len(self.division_status) - 4, 4, frameWidget)  
        
        # frameWidget = QtWidgets.QWidget()               
        # self.selector_te = QtWidgets.QComboBox(frameWidget)                                 
        # self.selector_te.setStyleSheet("background-color:#55cbcd;selection-background-color: darkblue") 
        # self.selector_te.setGeometry(20, 2, 50, 25)       
        # for a in ['', 'A', 'B', 'C']:
        #     self.selector_te.addItem(a)
        
        # self.selector_icm.currentIndexChanged.connect(self.WriteInfoToCsv)
        # self.selector_te.currentIndexChanged.connect(self.WriteInfoToCsv)              
        # self.setCellWidget(len(self.division_status) - 3, 4, frameWidget)  
        
        # #Decision row
        # frameWidget = QtWidgets.QWidget()               
        # self.selector_decision = QtWidgets.QComboBox(frameWidget)         
        # self.selector_decision.setStyleSheet("background-color:lightgreen;selection-background-color: darkblue")#.format(self.dec_bcolors[0]))    
        # self.selector_decision.setGeometry(50, 2 ,150, 25) 
        
        # self.label_decision_prob = QtWidgets.QLabel(frameWidget)         
        # self.label_decision_prob.setGeometry(220, 2 ,100, 25) 
        # self.label_decision_prob.setText('0%')
        
        # for i in range(len(self.decisions)):            
        #     self.selector_decision.addItem(self.decisions[i]) 
        #     self.selector_decision.model().item(i).setBackground(QtGui.QColor(self.dec_bcolors[i]))   
        #     #self.selector_decision.model().item(i).setForeground(QtGui.QColor(self.dec_wcolors[i])) 
        # self.selector_decision.currentIndexChanged.connect(self.combo_changed_decision)         
        # self.setCellWidget(len(self.division_status), 2, frameWidget)       
        
        # #PGS row
        # frameWidget = QtWidgets.QWidget()
        # self.selector_pgs = QtWidgets.QComboBox(frameWidget)         
        # self.selector_pgs.setStyleSheet("background-color:lightgreen;selection-background-color: darkblue")#.format(self.dec_bcolors[0]))    
        # self.selector_pgs.setGeometry(50, 2 ,150, 25)        
        # for i in range(len(self.pgs)):            
        #     self.selector_pgs.addItem(self.pgs[i]) 
        #     self.selector_pgs.model().item(i).setBackground(QtGui.QColor(self.dec_bcolors[i])) 
        # self.selector_pgs.currentIndexChanged.connect(self.combo_changed_pgs)            
        # self.setCellWidget(len(self.division_status) + 1, 2, frameWidget)
                   
    def SetIcmTe(self):
        icm, te = read_analy_csv_icm_te(self.chamber_id, self.well_id)   
        
        if str(icm) != '' and 'NaN' not in str(icm) and self.selector_icm != None:
            idxs = [i for i,d in enumerate(['A', 'B', 'C']) if d.lower() in icm or d.upper() in icm]
            if idxs != []:
                self.selector_icm.setCurrentIndex(idxs[0] + 1)
                            
        if str(te) != '' and 'NaN' not in str(te) and self.selector_te != None:
            idxs = [i for i,d in enumerate(['A', 'B', 'C']) if d.lower() in te or d.upper() in te]
            if idxs != []:
                self.selector_te.setCurrentIndex(idxs[0] + 1)
            
                
    def WriteInfoToCsv(self):        
        if self.chamber_id != 0 and self.well_id != 0 and self.selector_icm != None and self.selector_te != None:
            write_analy_csv_icm_te(self.chamber_id, self.well_id, str(self.selector_icm.currentText()), str(self.selector_te.currentText()))

    def CellClicked(self, r, c):
        it = self.item(r, c)
        print(it.text())
        
    def SaveChangeItem(self):
        status=None
        t2=None
        t3=None
        t4=None
        t5=None
        t6=None
        t7=None
        t8=None
        morula=None
        blas=None
        comp=None
        pn_fading=None
        icm=None
        te=None
        pgs=None
        prob=None
        for r in range(len(self.division_status) - 2):
            
            key = str(self.item(r + 2, 0).text())
            print(r + 2, key)
            if key == '2cell':
                t2 = str(self.item(r + 2, 2).text())
            if key == '3cell':
                t3 = str(self.item(r + 2, 2).text())
            if key == '4cell':
                t4 = str(self.item(r + 2, 2).text())
            if key == '5cell':
                t5 = str(self.item(r + 2, 2).text())
            if key == '6cell':
                t6 = str(self.item(r + 2, 2).text())
            if key == '7cell':
                t7 = str(self.item(r + 2, 2).text())
            if key == '8cell':
                t8 = str(self.item(r + 2, 2).text())
            if key == 'Morula':
                morula = str(self.item(r + 2, 2).text())
            if key == 'Blastocyst_ICM':                
                blas = str(self.item(r + 2, 2).text())
                icm =  str(self.selector_icm.currentText())
            if key == 'Blastocyst_TE':                      
                te =  str(self.selector_te.currentText())
            if key == 'comp':
                comp = str(self.item(r + 2, 2).text())
            if key == 'PN_Fading':
                pn_fading = str(self.item(r + 2, 2).text())
        
        status = str(self.selector_decision.currentText())                 
        pgs = str(self.selector_pgs.currentText())
        prob = float(str(self.label_decision_prob.text()).replace('%', '')) / 100
        print(t2, t3)
        #print(str(self.item(10, 2).text()))
        #print(str(self.item(11, 2).text()))
        
        write_his_all_element(self.patient_id, self.patient_time, self.well_id, status, t2, t3, t4, t5, t6, t7, t8, morula, blas, comp, pn_fading, icm, te, pgs, prob)    
        xgboost_inf_write_blas_morula_pnfading(self.patient_id, self.patient_time, self.chamber_id, self.well_id)
        
        
    def combo_changed_decision(self):
        color = self.dec_bcolors[self.selector_decision.currentIndex()]       
        self.selector_decision.setStyleSheet("background-color:{};selection-background-color: darkblue".format(color)) 
        write_his_status_pgs(self.patient_id, self.patient_time, self.well_id, status=str(self.selector_decision.currentText()), pgs=None)
        
    def combo_changed_pgs(self):
        color = self.dec_bcolors[self.selector_pgs.currentIndex()]       
        self.selector_pgs.setStyleSheet("background-color:{};selection-background-color: darkblue".format(color)) 
        write_his_status_pgs(self.patient_id, self.patient_time, self.well_id, status=None, pgs=str(self.selector_pgs.currentText()))




    #add top that function----------------------- 
    def SetItem(self, row, col, value, readonly):
        #print(row, col)
        #print('set=' + str(value))
        item_data = QtWidgets.QTableWidgetItem(str(value))        
        item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        # item_data.setBackground(QtGui.QColor(218,241,252))
        if readonly:
            item_data.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setItem(row, col, item_data)
    def SetItemTitle(self, row, col, value, readonly):
        item_data = QtWidgets.QTableWidgetItem(str(value))        
        item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item_data.setBackground(QtGui.QColor(218,241,252))
        if readonly:
            item_data.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setItem(row, col, item_data)
        
    def SetIcmTe(self):     
        self.SetIcmTe()

    def SetPgsChoices(self,combobox_list,dish_number):
        combo = QtWidgets.QComboBox()
        for t in combobox_list:
            combo.addItem(t)
        
        self.setCellWidget(dish_number+1,19,combo)
        
        
    def setDecision(self, result, prob):        
        try:
            idxs = [i for i,d in enumerate(self.table.decisions) if d.lower() == result.lower()]
            if idxs != []:
                self.selector_decision.setCurrentIndex(idxs[0])
            if str(prob) != '' and str(prob).lower() != 'nan':      
                self.label_decision_prob.setText(str(int(float(prob) * 100)) + '%')
        except:
            self.selector_decision.setCurrentIndex(0)
            
    def setPGS(self, result):        
        try:
            idxs = [i for i,d in enumerate(self.table.pgs) if d.lower() == result.lower()]           
            if idxs != []:
                self.selector_pgs.setCurrentIndex(idxs[0])                
        except:
            self.selector_pgs.setCurrentIndex(0)
            
    def SetPidDate(self, patient_id, timelapse_id, patient_time):
        self.patient_id = patient_id
        self.timelapse_id = timelapse_id

        self.patient_time = patient_time
        
    def SetChamberID(self, chamber_id):
        self.chamber_id = int(chamber_id)
        
    def SaveChangeItem(self):
        self.SaveChangeItem()

    #Clear all text in table
    def CleanAllText(self):
        col_num=len(self.division_status)
        row_num = len(self.wells_id)
        for i in range(2,row_num+2):
            for j in range(1,col_num+1):
                self.SetItem(i,j,'',True) 
        
            




class EmbryoNewInfoTable(QtWidgets.QTableWidget):
    def __init__(self, row, column, labels, parent=None):
        super(EmbryoNewInfoTable, self).__init__(row * 2+1, column, parent)        
        self.setStyleSheet('background-color:white; font-size: 12pt;')         
        self.verticalScrollBar().setStyleSheet("QScrollBar:vertical {Background-color:lightgray;}")          
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.labels = labels
        self.column_labels = ['div time' , 'div score','frag','frag score','sub score']
        self.row_labels = [ 'System', 'Manual']
        self.row_labels_ = ['', 'Time', 'ICM']
        self.chid = 0
        self.wid = 0      
        self.selector_icm = None
        self.selector_te = None

        manual_row_index=[2,4,6,8,10,12,14]

        #init table space part with ''
        for i in range(1,row*2+1):
            for j in range(2,column):
                item_data_space=QtWidgets.QTableWidgetItem('')
                item_data_space.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                self.setItem(i, j, item_data_space) 


        #first line space part
        for space_ind  in range(2):
            item_data_title=QtWidgets.QTableWidgetItem()
            item_data_title.setBackground(QtGui.QColor(171, 222, 230))
            item_data_title.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_data_title.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(0, space_ind, item_data_title)
        
        #column label title
        for space_ind in range(len(self.column_labels)):

            item_data_title = QtWidgets.QTableWidgetItem(self.column_labels[space_ind])
            item_data_title.setBackground(QtGui.QColor(171, 222, 230))
            item_data_title.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_data_title.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(0, space_ind+2, item_data_title)

            # #system row cant be modified
            # for label_ind in range(len(labels)):
            #     item_data = QtWidgets.QTableWidgetItem()
            #     # item_data.setBackground(QtGui.QColor(245, 198, 240))
            #     item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            #     if not (space_ind in manual_row_index and label_ind==2):
            #         item_data.setFlags(QtCore.Qt.ItemIsEnabled)
            #     self.setItem(label_ind * 2+1, space_ind+2, item_data)  
        
            
        #row label title
        for i in range(row):    
            #Column 0      
            item_data = QtWidgets.QTableWidgetItem(self.labels[i])
            # item_data.setBackground(QtGui.QColor(245, 198, 240))
            item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_data.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(i * 2+1, 0, item_data)  
            
            
            for j in range(2):
                self.setRowHeight(2*i , 25)
                
                item_data = QtWidgets.QTableWidgetItem(self.row_labels[j])
                # item_data.setBackground(QtGui.QColor(218,241,252))
                item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item_data.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(2*i + j+1, 1, item_data)  
                
                
            
            
            self.setSpan(2*i+1, 0, 2, 1)   
        
        #init all table element '' and cant modify (only manual line can )
        for a in range(1,row*2+1):
            for b in range(2,column):
                item_data_empty= QtWidgets.QTableWidgetItem('')
                # item_data.setBackground(QtGui.QColor(245, 198, 240))
                item_data_empty.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                if not (a in manual_row_index and (b==2 or b==4)):
                    item_data_empty.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(a, b, item_data_empty) 

        

        
        self.setColumnWidth(0, 100)

    def AddSystemRow(self, row, embryo_label_anaylsis):   
        # print('embryo_label_anaylsis info:',embryo_label_anaylsis.infos)           

        for i, info in enumerate(embryo_label_anaylsis.infos):
                
                #Analysis
                item_data = QtWidgets.QTableWidgetItem(info)
                item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                # item_data.setBackground(QtGui.QColor(241,252,218))
                item_data.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(row*2+1,2+i, item_data)

    def AddManualRow(self, row, embryo_label_anaylsis):   
        # print('embryo_label_anaylsis info:',embryo_label_anaylsis.infos)           

        for i, info in enumerate(embryo_label_anaylsis.infos):
                # print('RRRRRRRr',i,info)
                #Analysis
                item_data = QtWidgets.QTableWidgetItem(info)
                item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                if not (i+2==2 or i+2==4):
                    item_data.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(row*2+2,2+i, item_data)
               
                                         
            
    def DeleteRow(self, row_number):
        self.removeRow(row_number)  
        
    def SetChamberIdPid(self, chid, wid):
        self.chid = int(chid)
        self.wid = int(wid)
        
    def SetIcmTe(self):
        icm, te = read_analy_csv_icm_te(self.chid, self.wid)       
        if icm != '' and self.selector_icm != None:
            idxs = [i for i,d in enumerate(['A', 'B', 'C']) if d.lower() in icm or d.upper() in icm]
            if idxs != []:
                self.selector_icm.setCurrentIndex(idxs[0])
        if te != '' and self.selector_te != None:
            idxs = [i for i,d in enumerate(['A', 'B', 'C']) if d.lower() in te or d.upper() in te]
            if idxs != []:
                self.selector_te.setCurrentIndex(idxs[0])
        
    def WriteInfoToCsv(self):
        if self.chid != 0 and self.wid != 0 and self.selector_icm != None and self.selector_te != None:
            write_analy_csv_icm_te(self.chid, self.wid, str(self.selector_icm.currentText()), str(self.selector_te.currentText()))
  
class EmbryoPnTable(QtWidgets.QTableWidget):
    def __init__(self, row, column, labels, parent=None):
        super(EmbryoPnTable, self).__init__(row * 2+1, column, parent)        
        self.setStyleSheet('background-color:white; font-size: 12pt;')         
        self.verticalScrollBar().setStyleSheet("QScrollBar:vertical {Background-color:lightgray;}")          
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.labels = labels
        self.column_labels = ['fading time' , 'fading score','pn number']
        self.row_labels = [ 'System', 'Manual']
        self.row_labels_ = ['', 'Time', 'ICM']
        self.chid = 0
        self.wid = 0      
        self.selector_icm = None
        self.selector_te = None
         
        
        #init table with ''

        for i in range(1,row*2+1):
            for j in range(2,column):
                item_data_space=QtWidgets.QTableWidgetItem('')
                item_data_space.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                self.setItem(i, j, item_data_space) 



        for i in range(len(self.column_labels)):

            item_data_title = QtWidgets.QTableWidgetItem(self.column_labels[i])
            item_data_title.setBackground(QtGui.QColor(171, 222, 230))
            item_data_title.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_data_title.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(0, i+2, item_data_title)
        for i  in range(2):
            item_data_title=QtWidgets.QTableWidgetItem()
            item_data_title.setBackground(QtGui.QColor(171, 222, 230))
            item_data_title.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_data_title.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(0, i, item_data_title)
            
        for i in range(row):    
            #Column 0      
            item_data = QtWidgets.QTableWidgetItem(self.labels[i])
            # item_data.setBackground(QtGui.QColor(218,241,252))
            item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_data.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(i * 2+1, 0, item_data)      
            
            for j in range(2):
                self.setRowHeight(2*i , 25)
                
                item_data = QtWidgets.QTableWidgetItem(self.row_labels[j])
                # item_data.setBackground(QtGui.QColor(218,241,252))
                item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item_data.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(2*i + j+1, 1, item_data)  
                
            
            
            self.setSpan(2*i+1, 0, 2, 1)  
        #make system row cant be modify
        for i in range(2,5):    
            item_data_disable = QtWidgets.QTableWidgetItem()
        
            item_data_disable.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            # item_data_disable.setBackground(QtGui.QColor(241,252,218))
            item_data_disable.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(1,i, item_data_disable)  

        for i in range(len(self.column_labels)+2):
            self.setColumnWidth(i,140)

       
        

    def AddRow(self, pn_time, pn_score,pn_number):   

        item_data_pn_time=QtWidgets.QTableWidgetItem(pn_time)
        item_data_pn_time.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item_data_pn_score=QtWidgets.QTableWidgetItem(pn_score)
        item_data_pn_score.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item_data_pn_number=QtWidgets.QTableWidgetItem(pn_number)
        item_data_pn_number.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item_data_pn_time.setFlags(QtCore.Qt.ItemIsEnabled)
        item_data_pn_score.setFlags(QtCore.Qt.ItemIsEnabled)
        item_data_pn_number.setFlags(QtCore.Qt.ItemIsEnabled)
        # item_data_pn_time.setBackground(QtGui.QColor(241,252,218))
        # item_data_pn_score.setBackground(QtGui.QColor(241,252,218))
        # item_data_pn_number.setBackground(QtGui.QColor(241,252,218))


        self.setItem(1,2, item_data_pn_time)
        self.setItem(1,3, item_data_pn_score)
        self.setItem(1,4, item_data_pn_number)
    
    def AddManualRow(self, embryo_label_anaylsis):   
        # print('embryo_label_anaylsis info:',embryo_label_anaylsis.infos)           
        
        for i, info in enumerate(embryo_label_anaylsis.infos):
                
                #Analysis
                item_data = QtWidgets.QTableWidgetItem(info)
                # item_data.setBackground(QtGui.QColor(241,252,218))
                item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                # item_data.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(2,2+i, item_data)

        
            
    def DeleteRow(self, row_number):
        self.removeRow(row_number)  
        
    def SetChamberIdPid(self, chid, wid):
        self.chid = int(chid)
        self.wid = int(wid)
        
    # def SetIcmTe(self):
    #     icm, te = read_analy_csv_icm_te(self.chid, self.wid)       
    #     if icm != '' and self.selector_icm != None:
    #         idxs = [i for i,d in enumerate(['A', 'B', 'C']) if d.lower() in icm or d.upper() in icm]
    #         if idxs != []:
    #             self.selector_icm.setCurrentIndex(idxs[0])
    #     if te != '' and self.selector_te != None:
    #         idxs = [i for i,d in enumerate(['A', 'B', 'C']) if d.lower() in te or d.upper() in te]
    #         if idxs != []:
    #             self.selector_te.setCurrentIndex(idxs[0])
        
    # def WriteInfoToCsv(self):
    #     if self.chid != 0 and self.wid != 0 and self.selector_icm != None and self.selector_te != None:
    #         write_analy_csv_icm_te(self.chid, self.wid, str(self.selector_icm.currentText()), str(self.selector_te.currentText()))
  


class EmbryoBlasTable(QtWidgets.QTableWidget):
    def __init__(self, row, column, labels, parent=None):
        super(EmbryoBlasTable, self).__init__(row * 2+1, column, parent)        
        self.setStyleSheet('background-color:white; font-size: 12pt;')         
        self.verticalScrollBar().setStyleSheet("QScrollBar:vertical {Background-color:lightgray;}")          
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.labels = labels
        self.column_labels = ['div time' , 'div score']
        self.row_labels = [ 'System', 'Manual']
        self.chid = 0
        self.wid = 0      
        self.selector_icm = None
        self.selector_te = None
         
        
        


        #table title fill('div time' , 'div score','grade')
        for i in range(len(self.column_labels)):

            item_data_title = QtWidgets.QTableWidgetItem(self.column_labels[i])
            item_data_title.setBackground(QtGui.QColor(171, 222, 230))
            item_data_title.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_data_title.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(0, i+2, item_data_title)
        
        #table title fill(space)

        for i  in range(2):
            item_data_title=QtWidgets.QTableWidgetItem()
            item_data_title.setBackground(QtGui.QColor(171, 222, 230))
            item_data_title.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_data_title.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(0, i, item_data_title)
        
            
        for i in range(row):    
            #Column 0      
            item_data = QtWidgets.QTableWidgetItem(self.labels[i])
            # item_data.setBackground(QtGui.QColor(218,241,252))
            item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_data.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(i * 2+1, 0, item_data)      
            
            for j in range(2):
                self.setRowHeight(2*i , 25)
                
                item_data = QtWidgets.QTableWidgetItem(self.row_labels[j])
                # item_data.setBackground(QtGui.QColor(218,241,252))
                item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item_data.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(2*i + j+1, 1, item_data)  
                
            
            
            self.setSpan(2*i+1, 0, 2, 1)  

        #make system row cant be modify
        #init table with ''

        for i in range(1,row*2+1):
            for j in range(2,column):
                item_data_space=QtWidgets.QTableWidgetItem('')
                item_data_space.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                if not ((i==2 and j==2) or (i==4 and j==2)):
                    item_data_space.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(i, j, item_data_space) 
           
        

        for i in range(len(self.column_labels)+2):
            self.setColumnWidth(i,175)

       
        

    
    
    def AddManualRow(self,row, embryo_label_anaylsis):   
        # print('embryo_label_anaylsis info:',embryo_label_anaylsis.infos)           
        
        for i, info in enumerate(embryo_label_anaylsis.infos):
                
                #Analysis
                item_data = QtWidgets.QTableWidgetItem(info)
                # item_data.setBackground(QtGui.QColor(241,252,218))
                item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                if not i+2==2:
                    item_data.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(row*2+2,2+i, item_data)

    def AddSystemRow(self, row, embryo_label_anaylsis):   
        # print('embryo_label_anaylsis info:',embryo_label_anaylsis.infos)           

        for i, info in enumerate(embryo_label_anaylsis.infos):
                
                #Analysis
                item_data = QtWidgets.QTableWidgetItem(info)
                item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                # item_data.setBackground(QtGui.QColor(241,252,218))
                item_data.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(row*2+1,2+i, item_data)
            
    def DeleteRow(self, row_number):
        self.removeRow(row_number)  
        
    def SetChamberIdPid(self, chid, wid):
        self.chid = int(chid)
        self.wid = int(wid)
        
    def SetIcmTe(self):
        icm, te = read_analy_csv_icm_te(self.chid, self.wid)       
        if icm != '' and self.selector_icm != None:
            idxs = [i for i,d in enumerate(['A', 'B', 'C']) if d.lower() in icm or d.upper() in icm]
            if idxs != []:
                self.selector_icm.setCurrentIndex(idxs[0])
        if te != '' and self.selector_te != None:
            idxs = [i for i,d in enumerate(['A', 'B', 'C']) if d.lower() in te or d.upper() in te]
            if idxs != []:
                self.selector_te.setCurrentIndex(idxs[0])
        
    def WriteInfoToCsv(self):
        if self.chid != 0 and self.wid != 0 and self.selector_icm != None and self.selector_te != None:
            write_analy_csv_icm_te(self.chid, self.wid, str(self.selector_icm.currentText()), str(self.selector_te.currentText()))
  




class EmbryoTotalScoreTable(QtWidgets.QTableWidget):
    def __init__(self, row, column, parent=None):
        super(EmbryoTotalScoreTable, self).__init__(row * 2+1, column, parent)        
        self.setStyleSheet('background-color:white; font-size: 12pt;')         
        self.verticalScrollBar().setStyleSheet("QScrollBar:vertical {Background-color:lightgray;}")          
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        # self.labels = labels
        self.column_labels = ['Total Score']
        self.row_labels = [ 'System', 'Manual']
        self.chid = 0
        self.wid = 0      
        self.selector_icm = None
        self.selector_te = None
         
        
        #init table with ''

        for i in range(1,row*2+1):
            for j in range(1,column):
                item_data_space=QtWidgets.QTableWidgetItem('')
                item_data_space.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item_data_space.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(i, j, item_data_space) 


        #title (Total Score)
        for i in range(len(self.column_labels)):

            item_data_title = QtWidgets.QTableWidgetItem(self.column_labels[i])
            item_data_title.setBackground(QtGui.QColor(171, 222, 230))
            item_data_title.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_data_title.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(0, i+1, item_data_title)
        #title space(0,0)
        for i  in range(1):
            item_data_title_space=QtWidgets.QTableWidgetItem()
            item_data_title_space.setBackground(QtGui.QColor(171, 222, 230))
            item_data_title_space.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_data_title_space.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(0, i, item_data_title_space)

        
        


        for i in range(len(self.row_labels)):
           
            item_data_system_manual = QtWidgets.QTableWidgetItem(self.row_labels[i])
            item_data_system_manual.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_data_system_manual.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(i+1, 0, item_data_system_manual)  
                

        

        for i in range(len(self.column_labels)+2):
            self.setColumnWidth(i,100)

       
        

    def AddRow(self, pn_time, pn_score,pn_number):   

        item_data_pn_time=QtWidgets.QTableWidgetItem(pn_time)
        item_data_pn_score=QtWidgets.QTableWidgetItem(pn_score)
        item_data_pn_number=QtWidgets.QTableWidgetItem(pn_number)
        item_data_pn_time.setFlags(QtCore.Qt.ItemIsEnabled)
        item_data_pn_score.setFlags(QtCore.Qt.ItemIsEnabled)
        item_data_pn_number.setFlags(QtCore.Qt.ItemIsEnabled)
        item_data_pn_time.setBackground(QtGui.QColor(241,252,218))
        item_data_pn_score.setBackground(QtGui.QColor(241,252,218))
        item_data_pn_number.setBackground(QtGui.QColor(241,252,218))


        self.setItem(1,2, item_data_pn_time)
        self.setItem(1,3, item_data_pn_score)
        self.setItem(1,4, item_data_pn_number)
    
    def AddManualRow(self, embryo_label_anaylsis):   
        # print('embryo_label_anaylsis info:',embryo_label_anaylsis.infos)           
        
        for i, info in enumerate(embryo_label_anaylsis.infos):
                
                #Analysis
                item_data = QtWidgets.QTableWidgetItem(info)
                # item_data.setBackground(QtGui.QColor(241,252,218))
                item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                # item_data.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(2,2+i, item_data)

        
            
    def DeleteRow(self, row_number):
        self.removeRow(row_number)  
        
    def SetChamberIdPid(self, chid, wid):
        self.chid = int(chid)
        self.wid = int(wid)
        
    def SetIcmTe(self):
        icm, te = read_analy_csv_icm_te(self.chid, self.wid)       
        if icm != '' and self.selector_icm != None:
            idxs = [i for i,d in enumerate(['A', 'B', 'C']) if d.lower() in icm or d.upper() in icm]
            if idxs != []:
                self.selector_icm.setCurrentIndex(idxs[0])
        if te != '' and self.selector_te != None:
            idxs = [i for i,d in enumerate(['A', 'B', 'C']) if d.lower() in te or d.upper() in te]
            if idxs != []:
                self.selector_te.setCurrentIndex(idxs[0])
        
    def WriteInfoToCsv(self):
        if self.chid != 0 and self.wid != 0 and self.selector_icm != None and self.selector_te != None:
            write_analy_csv_icm_te(self.chid, self.wid, str(self.selector_icm.currentText()), str(self.selector_te.currentText()))
  




