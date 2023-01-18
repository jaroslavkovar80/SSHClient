from GUI.qt5TCMonitorMainWindow import Ui_MainWindow
from PyQt5.QtWidgets import (QApplication, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt
import time

class TCMonitorMainWindow(Ui_MainWindow):
    def __init__(self, window):

        self.setupUi(window)

        #buttons to change index of current tab
        self.btnTab1.clicked.connect(self.nav_to_tab0)
        self.btnTab2.clicked.connect(self.nav_to_tab1)
        self.btnTab3.clicked.connect(self.nav_to_tab2)
        self.btnTab4.clicked.connect(self.nav_to_tab3)

        #butttons of memory table
        self.btnAddRecordToMemoryTable.clicked.connect(self.addOneRowToMemoryTable)
        self.btnDelRecordFromMemoryTable.clicked.connect(self.delRowFromMemoryTable)
        self.btnClearMemoryTable.clicked.connect(self.clearMemoryTable)

    def nav_to_tab0(self):
        self.tabWidget.setCurrentIndex(0)

    def nav_to_tab1(self):
        self.tabWidget.setCurrentIndex(1)

    def nav_to_tab2(self):
        self.tabWidget.setCurrentIndex(2)

    def nav_to_tab3(self):
        self.tabWidget.setCurrentIndex(3)

    def addOneRowToMemoryTable(self):

        #TODO
        self.addRowToMemoryTable(["apple", "banana", "cherry","apple", "banana2", "cherry","apple", "banana3", "cherry"])

    def addRowToMemoryTable(self, parList):

        #add new empty row
        rowCount = self.tablewMemoryOverview.rowCount()
        self.tablewMemoryOverview.insertRow(rowCount)

        #add current time to first column
        columnIdx = 0
        currentTime = time.strftime('%X %x')
        rowItem = QTableWidgetItem(currentTime)
        rowItem.setTextAlignment(0x0080 | 0x0004)
        self.tablewMemoryOverview.setItem(rowCount, columnIdx, rowItem)

        #fill rest of column from received list
        columnIdx += 1
        for item in parList:
            rowItem = QTableWidgetItem(item)
            rowItem.setTextAlignment(0x0080|0x0004)
            self.tablewMemoryOverview.setItem(rowCount,columnIdx,rowItem)
            columnIdx += 1

    def delRowFromMemoryTable(self):

        # if row is selected remove selected row
        rowCount = self.tablewMemoryOverview.currentRow()

        # if row is not selected, remove last row
        if(rowCount==-1):
            rowCount = self.tablewMemoryOverview.rowCount()-1

        #valid index of the row? -> remove row
        if rowCount > -1:
            self.tablewMemoryOverview.removeRow(rowCount)

        #print(str(rowCount))

    def clearMemoryTable(self):

        self.tablewMemoryOverview.setRowCount(0)
