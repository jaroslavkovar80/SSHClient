from GUI.qt5TCMonitorMainWindow import Ui_MainWindow
from GUI.qt5TCMonitorAboutWindow import Ui_Dialog
from PyQt5.QtWidgets import (QApplication, QTableWidget, QTableWidgetItem, QDialog)
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
import time

from TCMonitorLogic import PUViewer


class TCMonitorAboutWindow(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlag(Qt.SplashScreen)


class TCMonitorMainWindow(Ui_MainWindow):
    def __init__(self, window):

        self.setupUi(window)

        # create instace of logic class
        self.viewerLogic = PUViewer()
        self._timerMemoryLogging = QTimer()

        # create instace of another windows
        self._dlgAbout = TCMonitorAboutWindow()


        # buttons to change index of current tab
        self.btnTab1.clicked.connect(self.nav_to_tab0)
        self.btnTab2.clicked.connect(self.nav_to_tab1)
        self.btnTab3.clicked.connect(self.nav_to_tab2)
        self.btnTab4.clicked.connect(self.nav_to_tab3)

        # butttons of memory table
        self.btnAddRecordToMemoryTable.clicked.connect(self.addOneRowToMemoryTable)
        self.btnDelRecordFromMemoryTable.clicked.connect(self.delRowFromMemoryTable)
        self.btnClearMemoryTable.clicked.connect(self.clearMemoryTable)
        self.btnStartMemoryLogging.clicked.connect(self._memoryLoggingManagement)

        # estabilish connection logic
        self.btnCheckConnection.clicked.connect(self._connectToTarget)

        self.actionAbout.triggered.connect(self._showAbout)

        self.btnCallCmd.clicked.connect(self._callCommand)

        # update status
        self._updateStatus()

    def _showAbout(self):
        self._dlgAbout.exec()

    def _connectToTarget(self):
        if self.viewerLogic.isConnected():
            self.viewerLogic.disconnect()
        else:
            self.viewerLogic.getConnection(host=self.edTargetHost.text())
        self._updateStatus()

    def _updateStatus(self):


        self.statusbar.showMessage(self.viewerLogic.getConnectionStatus())
        self._updateGUI()


    def _updateGUI(self):
        self.statusbar.showMessage(self.viewerLogic.getConnectionStatus())

        if self.viewerLogic.isConnected():
            self.btnCheckConnection.setText('disconnect')
        else:
            self.btnCheckConnection.setText('connect')

        if self._timerMemoryLogging.isActive():
            self.btnStartMemoryLogging.setText('stop logging')
        else:
            self.btnStartMemoryLogging.setText('start logging')

    def nav_to_tab0(self):
        self.tabWidget.setCurrentIndex(0)

    def nav_to_tab1(self):
        self.tabWidget.setCurrentIndex(1)

    def nav_to_tab2(self):
        self.tabWidget.setCurrentIndex(2)

    def nav_to_tab3(self):
        self.tabWidget.setCurrentIndex(3)

    def addOneRowToMemoryTable(self):

        list = self.viewerLogic.getMemory()

        print(list[1])

        if list[1] != "-1":
            self.addRowToMemoryTable(list)
        elif self._timerMemoryLogging.isActive():
            self._timerMemoryLogging.stop()
            self._updateGUI()

    def _callCommand(self):
        self.viewerLogic.getJournalCtl(self.lineEdit.text())
        print(self.lineEdit.text())

    def addRowToMemoryTable(self, parList):

        # add new empty row
        rowCount = self.tablewMemoryOverview.rowCount()
        self.tablewMemoryOverview.insertRow(rowCount)

        # add current time to first column
        columnIdx = 0
        currentTime = time.strftime('%X %x')
        rowItem = QTableWidgetItem(currentTime)
        rowItem.setTextAlignment(0x0080 | 0x0004)
        self.tablewMemoryOverview.setItem(rowCount, columnIdx, rowItem)

        # fill rest of column from received list
        columnIdx += 1
        for item in parList:
            rowItem = QTableWidgetItem(item)
            rowItem.setTextAlignment(0x0080 | 0x0004)
            self.tablewMemoryOverview.setItem(rowCount, columnIdx, rowItem)
            columnIdx += 1

            # in visu there is only 10 column available, if more items in list -> break it
            if (columnIdx == 10):
                break

    def delRowFromMemoryTable(self):

        # if row is selected remove selected row
        rowCount = self.tablewMemoryOverview.currentRow()

        # if row is not selected, remove last row
        if (rowCount == -1):
            rowCount = self.tablewMemoryOverview.rowCount() - 1

        # valid index of the row? -> remove row
        if rowCount > -1:
            self.tablewMemoryOverview.removeRow(rowCount)

        # print(str(rowCount))

    def clearMemoryTable(self):

        self.tablewMemoryOverview.setRowCount(0)

    def _memoryLoggingManagement(self):

        # loggingTime = int(self.spinBoxLoggingTime.value,default=1)

        loggingTime = self.spinBoxLoggingTime.value()

        # print(loggingTime)
        if self._timerMemoryLogging.isActive():
            self._timerMemoryLogging.stop()
        elif self.viewerLogic.isConnected():
            self._timerMemoryLogging.timeout.connect(self.cyclicLogic)
            self._timerMemoryLogging.start(loggingTime * 60 * 1000)
            self.addOneRowToMemoryTable()

        self._updateGUI()

    def cyclicLogic(self):
        # print("tick:" + str(time.strftime('%X %x %Z')))
        # time.sleep(60.0 - ((time.time() - self._startTime) % 60.0))
        # if (60.0 - ((time.time() - self._startTime) % 60.0)) == 0:
        # print("tick:" + str(time.strftime('%X %x %Z')))
        # time.sleep(30)
        self.addOneRowToMemoryTable()
