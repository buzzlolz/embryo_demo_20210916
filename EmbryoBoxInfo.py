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
            item_data.setBackground(QtGui.QColor(218,241,252))
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
    def __init__(self, well_id, parent=None):
        super(EmbryoHistoryInfoTableBox, self).__init__(parent)
        self.well_id = well_id
        self.table = EmbryoHistoryInfoTable(well_id, self)  
        self.table.setGeometry(0, 0, 510, 435)        
        self.setFixedSize(515, 440)
        
    def SetItem(self, row, col, value, readonly):
        #print(row, col)
        #print('set=' + str(value))
        item_data = QtWidgets.QTableWidgetItem(str(value))        
        item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item_data.setBackground(QtGui.QColor(218,241,252))
        if readonly:
            item_data.setFlags(QtCore.Qt.ItemIsEnabled)
        self.table.setItem(row, col, item_data)
        
    def SetIcmTe(self):     
        self.table.SetIcmTe()
        
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
            
    def SetPidDate(self, patient_id,  patient_time):
        self.table.patient_id = patient_id
        self.table.patient_time = patient_time
        
    def SetChamberID(self, chamber_id):
        self.table.chamber_id = int(chamber_id)
        
    def SaveChangeItem(self):
        self.table.SaveChangeItem()
      
   
        
class EmbryoHistoryInfoTable(QtWidgets.QTableWidget):
    def __init__(self, well_id, parent=None):
        self.titles = ['Status', 'Division Time', 'Score']
        #self.cell_names = ['2cell', '3cell', '4cell', '5cell', '6cell', '7cell', '8cell',]
        self.cell_names = ['PN_Fading', '2cell', '3cell', '4cell', '5cell', '6cell', '7cell', '8cell',  'Morula', 'Blastocyst_ICM', 'Blastocyst_TE', 'Event', 'Final score', 'Decision', 'PGS']        
        self.decisions = ['', 'Transfer', 'Discard', 'Freeze']
        self.dec_bcolors = ['white','lightgreen', '#ff968a', '#abdee6']
        self.pgs = ['', 'Mosaicism', 'Aneuploidy', 'Euploidy']
        super(EmbryoHistoryInfoTable, self).__init__(len(self.cell_names) + 2, len(self.titles), parent)        
        
        self.setStyleSheet('background-color:white; font-size: 13pt;')         
        self.verticalScrollBar().setStyleSheet("QScrollBar:vertical {Background-color:lightgray;}")      
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.patient_id = ''
        self.patient_time = ''
        self.chamber_id = 0
        self.well_id = well_id
       
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(1)
       
        self.setRowCount(len(self.cell_names) + 2)
        self.setColumnCount(len(self.titles) + 2)
        for i in range(len(self.cell_names) + 1):
            self.setRowHeight(i, 25)
        self.setRowHeight(len(self.cell_names) + 1, 30)
        self.setRowHeight(len(self.cell_names) + 2, 30)            
        
        for i in range(len(self.titles) + 2):
            self.setColumnWidth(i, 75) 
          
        #Span
        for i in range(len(self.cell_names) + 2):
            #if i != len(self.cell_names) + 1 and i != len(self.cell_names) + 2:
            self.setSpan(i, 0, 1, 2)
            self.setSpan(i, 2, 1, 2)
            self.setColumnWidth(i, 10) 
        self.setSpan(0, 0, 1, len(self.titles) + 2)
        
        #Blas.
        self.setSpan(len(self.cell_names) - 4, 2, 2, 2)
        
        #Event
        self.setSpan(len(self.cell_names) - 2, 2, 1, 3)
        
        #Finial score, decision, pgs        
        self.setSpan(len(self.cell_names) - 1, 2, 1, 3)
        self.setSpan(len(self.cell_names), 2, 1, 3)
        self.setSpan(len(self.cell_names) + 1, 2, 1, 3)        
        
        self.initContent()
        #self.cellChanged.connect(self.CellClicked)
        

    def initContent(self):     
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)    
        #Header
        item_data = QtWidgets.QTableWidgetItem('Well ' + str(self.well_id))
        item_data.setTextAlignment(QtCore.Qt.AlignHCenter)
        item_data.setFlags(QtCore.Qt.ItemIsEnabled)
        item_data.setBackground(QtGui.QColor(218,241,252))        
        self.setItem(0, 0, item_data)   
        
        #Title
        for i in range(len(self.titles)):                        
            if i == 1:
                self.setColumnWidth(i, 150)
            else:
                self.setColumnWidth(i, 50) 
            item_data = QtWidgets.QTableWidgetItem(self.titles[i])
            item_data.setTextAlignment(QtCore.Qt.AlignHCenter)
            item_data.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(1, i*2, item_data)            
        for i in range(len(self.cell_names)):
            item_data = QtWidgets.QTableWidgetItem(self.cell_names[i])
            item_data.setTextAlignment(QtCore.Qt.AlignHCenter)    
            item_data.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(i + 2, 0, item_data)  
            
        #Blas. icm te
        frameWidget = QtWidgets.QWidget()               
        self.selector_icm = QtWidgets.QComboBox(frameWidget)                                 
        self.selector_icm.setStyleSheet("background-color:#55cbcd;selection-background-color: darkblue") 
        self.selector_icm.setGeometry(20, 2, 50, 25)       
        for a in ['', 'A', 'B', 'C']:
            self.selector_icm.addItem(a)                        
        self.setCellWidget(len(self.cell_names) - 4, 4, frameWidget)  
        
        frameWidget = QtWidgets.QWidget()               
        self.selector_te = QtWidgets.QComboBox(frameWidget)                                 
        self.selector_te.setStyleSheet("background-color:#55cbcd;selection-background-color: darkblue") 
        self.selector_te.setGeometry(20, 2, 50, 25)       
        for a in ['', 'A', 'B', 'C']:
            self.selector_te.addItem(a)
        
        self.selector_icm.currentIndexChanged.connect(self.WriteInfoToCsv)
        self.selector_te.currentIndexChanged.connect(self.WriteInfoToCsv)              
        self.setCellWidget(len(self.cell_names) - 3, 4, frameWidget)  
        
        #Decision row
        frameWidget = QtWidgets.QWidget()               
        self.selector_decision = QtWidgets.QComboBox(frameWidget)         
        self.selector_decision.setStyleSheet("background-color:lightgreen;selection-background-color: darkblue")#.format(self.dec_bcolors[0]))    
        self.selector_decision.setGeometry(50, 2 ,150, 25) 
        
        self.label_decision_prob = QtWidgets.QLabel(frameWidget)         
        self.label_decision_prob.setGeometry(220, 2 ,100, 25) 
        self.label_decision_prob.setText('0%')
        
        for i in range(len(self.decisions)):            
            self.selector_decision.addItem(self.decisions[i]) 
            self.selector_decision.model().item(i).setBackground(QtGui.QColor(self.dec_bcolors[i]))   
            #self.selector_decision.model().item(i).setForeground(QtGui.QColor(self.dec_wcolors[i])) 
        self.selector_decision.currentIndexChanged.connect(self.combo_changed_decision)         
        self.setCellWidget(len(self.cell_names), 2, frameWidget)       
        
        #PGS row
        frameWidget = QtWidgets.QWidget()
        self.selector_pgs = QtWidgets.QComboBox(frameWidget)         
        self.selector_pgs.setStyleSheet("background-color:lightgreen;selection-background-color: darkblue")#.format(self.dec_bcolors[0]))    
        self.selector_pgs.setGeometry(50, 2 ,150, 25)        
        for i in range(len(self.pgs)):            
            self.selector_pgs.addItem(self.pgs[i]) 
            self.selector_pgs.model().item(i).setBackground(QtGui.QColor(self.dec_bcolors[i])) 
        self.selector_pgs.currentIndexChanged.connect(self.combo_changed_pgs)            
        self.setCellWidget(len(self.cell_names) + 1, 2, frameWidget)
                   
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
        for r in range(len(self.cell_names) - 2):
            
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
        
        
            




class EmbryoNewInfoTable(QtWidgets.QTableWidget):
    def __init__(self, row, column, labels, parent=None):
        super(EmbryoNewInfoTable, self).__init__(row * 2+1, column, parent)        
        self.setStyleSheet('background-color:white; font-size: 12pt;')         
        self.verticalScrollBar().setStyleSheet("QScrollBar:vertical {Background-color:lightgray;}")          
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.labels = labels
        self.column_labels = ['div time' , 'div score','frag','frag score','total score']
        self.row_labels = [ 'System', 'Manual']
        self.row_labels_ = ['', 'Time', 'ICM']
        self.chid = 0
        self.wid = 0      
        self.selector_icm = None
        self.selector_te = None

        #first line space part
        for space_ind  in range(2):
            item_data_title=QtWidgets.QTableWidgetItem()
            item_data_title.setBackground(QtGui.QColor(218,241,252))
            item_data_title.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_data_title.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(0, space_ind, item_data_title)
        
        #column label title
        for space_ind in range(len(self.column_labels)):

            item_data_title = QtWidgets.QTableWidgetItem(self.column_labels[space_ind])
            item_data_title.setBackground(QtGui.QColor(218,241,252))
            item_data_title.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_data_title.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(0, space_ind+2, item_data_title)
        
            
        for i in range(row):    
            #Column 0      
            item_data = QtWidgets.QTableWidgetItem(self.labels[i])
            item_data.setBackground(QtGui.QColor(218,241,252))
            item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_data.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(i * 2+1, 0, item_data)  
            
            
            for j in range(2):
                self.setRowHeight(2*i , 37)
                #Column 1                 
                # if 'Morula' in self.labels and 'Blastocyst' in self.labels and (i == row - 1):
                #     item_data = QtWidgets.QTableWidgetItem(self.row_labels_[j])
                #     item_data.setBackground(QtGui.QColor(218,241,252))
                #     item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                #     item_data.setFlags(QtCore.Qt.ItemIsEnabled)
                #     self.setItem(2*i + j+1, 1, item_data)  
                # else:
                item_data = QtWidgets.QTableWidgetItem(self.row_labels[j])
                item_data.setBackground(QtGui.QColor(218,241,252))
                item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item_data.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(2*i + j+1, 1, item_data)  
                
            #Row 1   
            # for j in range(5):
            #     item_data = QtWidgets.QTableWidgetItem(self.column_labels[j])
            #     item_data.setBackground(QtGui.QColor(218,241,252))
            #     item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            #     item_data.setFlags(QtCore.Qt.ItemIsEnabled)
            #     self.setItem(3*i, 2 + j, item_data)    
            
            self.setSpan(2*i+1, 0, 2, 1)             
        self.setColumnWidth(0, 100)

    def AddRow(self, row, embryo_label_anaylsis):   
        # print('embryo_label_anaylsis info:',embryo_label_anaylsis.infos)           

        for i, info in enumerate(embryo_label_anaylsis.infos):
                
                #Analysis
                item_data = QtWidgets.QTableWidgetItem(info)
                item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
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


        for test in range(len(self.column_labels)):

            item_data_title = QtWidgets.QTableWidgetItem(self.column_labels[test])
            item_data_title.setBackground(QtGui.QColor(218,241,252))
            item_data_title.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_data_title.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(0, test+2, item_data_title)
        for r  in range(2):
            item_data_title=QtWidgets.QTableWidgetItem()
            item_data_title.setBackground(QtGui.QColor(218,241,252))
            item_data_title.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_data_title.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(0, r, item_data_title)
            
        for i in range(row):    
            #Column 0      
            item_data = QtWidgets.QTableWidgetItem(self.labels[i])
            item_data.setBackground(QtGui.QColor(218,241,252))
            item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_data.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(i * 2+1, 0, item_data)      
            
            for j in range(2):
                self.setRowHeight(2*i , 37)
                #Column 1                 
                # if 'Morula' in self.labels and 'Blastocyst' in self.labels and (i == row - 1):
                #     item_data = QtWidgets.QTableWidgetItem(self.row_labels_[j])
                #     item_data.setBackground(QtGui.QColor(218,241,252))
                #     item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                #     item_data.setFlags(QtCore.Qt.ItemIsEnabled)
                #     self.setItem(2*i + j+1, 1, item_data)  
                # else:
                item_data = QtWidgets.QTableWidgetItem(self.row_labels[j])
                item_data.setBackground(QtGui.QColor(218,241,252))
                item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item_data.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(2*i + j+1, 1, item_data)  
                
            #Row 1   
            # for j in range(5):
            #     item_data = QtWidgets.QTableWidgetItem(self.column_labels[j])
            #     item_data.setBackground(QtGui.QColor(218,241,252))
            #     item_data.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            #     item_data.setFlags(QtCore.Qt.ItemIsEnabled)
            #     self.setItem(3*i, 2 + j, item_data)    
            
            self.setSpan(2*i+1, 0, 2, 1)             
        self.setColumnWidth(0, 100)

    def AddRow(self, pn_time, pn_score,pn_number):    
        
        self.setItem(1,2, QtWidgets.QTableWidgetItem(pn_time))
        self.setItem(1,3, QtWidgets.QTableWidgetItem(pn_score))
        self.setItem(1,4, QtWidgets.QTableWidgetItem(pn_number))

        
            
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
  