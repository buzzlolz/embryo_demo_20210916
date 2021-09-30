# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 16:40:23 2020

@author: minghung
"""

import sys

from datetime import datetime
import calendar

from PyQt5.QtWidgets import QApplication, QWidget, QCalendarWidget
from PyQt5 import QtCore, QtWidgets
#from PyQt5.QtCore import QDate

from PyQt5.QtWidgets import QTimeEdit,QLabel
class AnotherWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    # def __init__(self):
    #     super().__init__()
    #     layout = QVBoxLayout()
    #     self.label = QLabel("Another Window % d" % randint(0,100))
    #     layout.addWidget(self.label)
    #     self.setLayout(layout)
    def __init__(self):
        super().__init__()
  
        # setting title
        self.setWindowTitle("Python ")
  
        # setting geometry
        self.setGeometry(1450, 200, 230, 50)
        self.setStyleSheet("background-color:#ff90b1;")
        self.button_ok = QtWidgets.QPushButton(self)
        self.button_ok.setGeometry(160, 0, 40, 40)
        self.button_ok.setText('OK')
        self.button_ok.setStyleSheet('background-color:lightblue;')
        self.button_ok.clicked.connect(self.select_finish)
        self.final_time = ''
  
        # calling method
        self.UiComponents()
  
        # showing all the widgets
        self.show()
  
    # method for components
    def UiComponents(self):
  
        # creating a QDateEdit widget
        # self.date.setDisplayFormat('hh:mm:ss.zzz')
        self.date = QTimeEdit(self)
        self.date.setDisplayFormat('hh:mm:ss')
        # setting geometry of the date edit
        self.date.setGeometry(0, 0, 150, 40)
  
        # creating a label
        # label = QLabel("GeeksforGeeks", self)
  
        # setting geometry
        # label.setGeometry(100, 150, 200, 60)
  
        # making label multiline
        # label.setWordWrap(True)
  
        # adding action to the date when enter key is pressed
        self.button_ok.clicked.connect(self.select_finish)
  
        # method called by date edit
        # def date_method():
  
        #     # getting the date
        #     value = date.time()
  
        #     # setting text to the label
        #     # label.setText("Selected Date : " + str(value))

        #     print(value)
    def select_finish(self):
        self.final_time = self.date.time()
        self.final_time=self.final_time.toString("hhmmss")
        print(self.final_time)
        self.close()



class Calendar(QtWidgets.QDialog):
    def __init__(self, tab, item=None, parent=None):
        super(Calendar, self).__init__(parent=parent)

        
        self.parent = parent
        self.tab = tab        
        self.item = item
        self.currentMonth = datetime.now().month
        self.currentYear = datetime.now().year
        self.setWindowTitle('Calendar')
        self.setGeometry(1000, 200, 400, 200)
        self.initUI()
        self.w = None
        self.show_new_window()

    def initUI(self):
        self.calendar = QtWidgets.QCalendarWidget(self)
        self.calendar.move(0, 0)
        self.calendar.setGridVisible(True)

        self.calendar.setMinimumDate(QtCore.QDate(self.currentYear, self.currentMonth - 1, 1))
        self.calendar.setMaximumDate(QtCore.QDate(self.currentYear, self.currentMonth + 1, calendar.monthrange(self.currentYear, self.currentMonth)[1]))

        self.calendar.setSelectedDate(QtCore.QDate(self.currentYear, self.currentMonth, 1))

        self.calendar.clicked.connect(self.printDateInfo)

        # self.calendar.clicked.connect(self.show_new_window)

    def show_new_window(self):
        if self.w is None:
            self.w = AnotherWindow()
        self.w.show()

    def printDateInfo(self, qDate):
        
        date = '{0}{1}{2}'.format(qDate.year(), str(qDate.month()).zfill(2), str(qDate.day()).zfill(2))
        time_get = self.w.final_time
        print(time_get)

        # date = date + '_' + datetime.strftime(datetime.now(), '%H%M%S')
        if self.tab == 'select':            
            date = date + '_' + time_get
            listsMyQLineEdit = self.parent.chambers[int(self.item) - 1].findChildren(QtWidgets.QLineEdit)
            listsMyQLineEdit[1].setText(date)
            print(time_get)
            print (date)
        if self.tab == 'history':
            date = date + '_' + datetime.strftime(datetime.now(), '%H%M%S')
            if self.item == 'start':
                self.parent.edit_startTime.setText(date + ' 00:00:00')
            if self.item == 'end':
                self.parent.edit_endTime.setText(date + ' 24:00:00')
        self.close()
        

        


        
        
        
