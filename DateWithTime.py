
import sys
from datetime import datetime
import calendar

#from PyQt5.QtWidgets import QApplication, QWidget, QCalendarWidget
from PyQt5 import QtCore, QtWidgets
#from PyQt5.QtCore import QDate




class DateWithTime(QtWidgets.QDialog):
    def __init__(self, tab, item=None, parent=None):
        super(DateWithTime, self).__init__(parent=parent)
        self.parent = parent
        self.tab = tab        
        self.item = item
        self.currentMonth = datetime.now().month
        self.currentYear = datetime.now().year
        self.setWindowTitle('Calendar')
        self.setGeometry(1000, 200, 400, 200)
        self.initUI()

    def initUI(self):
        
        self.date_with_time = QtWidgets.QTimeEdit(self)
        self.date_with_time.setCalendarPopup(True)
        # self.calendar = QtWidgets.QCalendarWidget(self)
        # self.calendar.move(0, 0)
        # self.calendar.setGridVisible(True)

        # self.calendar.setMinimumDate(QtCore.QDate(self.currentYear, self.currentMonth - 1, 1))
        # self.calendar.setMaximumDate(QtCore.QDate(self.currentYear, self.currentMonth + 1, calendar.monthrange(self.currentYear, self.currentMonth)[1]))

        # self.calendar.setSelectedDate(QtCore.QDate(self.currentYear, self.currentMonth, 1))

        # self.calendar.clicked.connect(self.printDateInfo)

    def printDateInfo(self, qDate):
        date = '{0}{1}{2}'.format(qDate.year(), str(qDate.month()).zfill(2), str(qDate.day()).zfill(2))
        
        
        date = date + '_' + datetime.strftime(datetime.now(), '%H%M%S')
        if self.tab == 'select':            
            listsMyQLineEdit = self.parent.chambers[int(self.item) - 1].findChildren(QtWidgets.QLineEdit)
            listsMyQLineEdit[2].setText(date)
            # print (date)
        if self.tab == 'history':
            if self.item == 'start':
                self.parent.edit_startTime.setText(date + ' 00:00:00')
            if self.item == 'end':
                self.parent.edit_endTime.setText(date + ' 24:00:00')
        self.close()