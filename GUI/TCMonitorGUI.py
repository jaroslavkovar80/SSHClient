import sys
import PyQt5.QtGui
# import pandas as pd

from GUI.qt5TCMonitorMainWindow import Ui_MainWindow
from GUI.qt5TCMonitorAboutWindow import Ui_About
from PyQt5.QtWidgets import (QApplication, QTableWidget, QTableWidgetItem, QDialog, QMessageBox, QMainWindow)
from PyQt5.QtCore import QTimer, QPoint, QDateTime
from PyQt5.QtCore import Qt
from PyQt5.QtChart import (QBarCategoryAxis, QBarSeries, QBarSet, QChart, QChartView, QLineSeries, QValueAxis,
                           QDateTimeAxis)
from PyQt5.QtGui import QPainter, QFont

import time
from datetime import datetime
import subprocess
import os
import re

import math

from SSHConnectorLogic import SSHConnector, CMD_GET_DISK_USAGE, CMD_GET_DMESG, CMD_GET_JOURNAL, CMD_GET_PROCESS

SW_VERSION = "V 0.1.0"

# ---
# CLASS FOR About dialog
# ---
class TCMonitorAboutWindow(QDialog):
    """
    CLASS FOR About dialog
     TODO: empty
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_About()
        self.ui.setupUi(self)
        self.setWindowFlag(Qt.SplashScreen)
        self.ui.lbAbout_4.setText(SW_VERSION)


# ---
# CLASS FOR window with CHART
# ---
class chartWithTimeAxis(QMainWindow):

    """
    CLASS FOR window with CHART
     - X axis is represented by time
     - Y axis is represented by int value

     TODO: empty
    """

    def __init__(self, chartTitle, xTitle, yTitle):
        """
        chartTitle - General CHart title
        xTitle - x axis title + [unit]
        yTitle - Y axis title + [unit]
        """
        super().__init__()

        # ---
        # create and configure Chart
        self.chart = QChart()
        self.chart.setTitle(chartTitle)
        self.chart.setTitleFont(QFont('Roboroto', 14, weight=QFont.Bold))
        self.chart.setAnimationOptions(QChart.NoAnimation)
        self.chart.setAnimationDuration(1000)
        # self.chart.setTheme(QChart.ChartThemeBlueCerulean)
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)

        # ---
        # create axis X - type QDateTimeAxis()
        self._axis_x = QDateTimeAxis()
        self.chart.addAxis(self._axis_x, Qt.AlignBottom)
        self._axis_x.setTitleText(xTitle)
        self._axis_x.setTitleVisible(True)
        self._axis_x.setTickCount(5)
        self._axis_x.setLabelsAngle(0)
        self._axis_x.setFormat("h:mm:ss")
        self._axis_x.setMin(QDateTime.currentDateTime())
        self._axis_x.setMax(QDateTime.currentDateTime().addSecs(1))

        # ---
        # create axis Y
        self._axis_y = QValueAxis()
        self.chart.addAxis(self._axis_y, Qt.AlignLeft)
        self._axis_y.setRange(0, 120)
        self._axis_y.setTitleText(yTitle)
        self._axis_y.setTitleVisible(True)

        # ---
        # create chart view and assign it to widget
        self._chart_view = QChartView(self.chart)
        self._chart_view.setRenderHint(QPainter.Antialiasing)
        self.setCentralWidget(self._chart_view)

        # ---
        # create empty list of lineseries
        self._lineserie = []

    def addSeriesToChart(self, seriesTitle):

        """
        Creating and assigning new series to chart
        seriesTitle - title of series shown in chart with color
        """

        # ---
        # create empty series and append it to the list of series
        tempLineSeries = QLineSeries()
        self._lineserie.append(tempLineSeries)

        # ---
        # assign title name and starting point X/Y to the latest series
        idx = len(self._lineserie) - 1
        self._lineserie[idx].setName(seriesTitle)
        self._lineserie[idx].append(QDateTime.currentDateTime().toSecsSinceEpoch(), 0)

        # ---
        # add series to chart
        self.chart.addSeries(self._lineserie[idx])

        # ---
        # attach axis X/Y to the latest series
        self._lineserie[idx].attachAxis(self._axis_x)
        self._lineserie[idx].attachAxis(self._axis_y)

    def clearAllSeries(self):
        """
        Deleting all points fom all series
        """
        # ---
        # clear all existing series
        for x in self._lineserie:
            x.clear()

        # set limits back to default values
        self._axis_y.setRange(0, 120)
        self._axis_x.setMin(QDateTime.currentDateTime())
        self._axis_x.setMax(QDateTime.currentDateTime().addSecs(1))

    def addPointToSerie(self, series_idx, x_time, y_value=0):
        """
        add one point time/value to series
        -> series_idx - index of series in the list to where point should be added
        -> x_time - time value of the point
        -> y_value - y axis value of the point
        """

        # ---
        # add time (usually current one) and its value to series
        self._lineserie[series_idx].append(x_time.toMSecsSinceEpoch(), y_value)

        # ---
        # recalculate max and min value for X/Y axes
        t_min, t_max = min(x_time, self._axis_x.min()), max(x_time, (self._axis_x.max()))
        y_min, y_max = min(y_value - 10, self._axis_y.min()), max(y_value + 10, self._axis_y.max())

        # ---
        # set new min/max for X/Y
        self._axis_x.setRange(t_min, t_max)
        self._axis_y.setRange(y_min, y_max)


class TCMonitorMainWindow(Ui_MainWindow):
    def __init__(self, window):

        self.setupUi(window)

        # create instace of logic class
        self._linuxSSHConnector = SSHConnector()
        self._timerMemoryLogging = QTimer()

        # create instace of another windows
        self._dlgAbout = TCMonitorAboutWindow()

        # buttons to change index of current tab
        self.btnTab1.click()
        self.btnTab1.clicked.connect(self.nav_to_tab0)
        self.btnTab2.clicked.connect(self.nav_to_tab1)
        self.btnTab3.clicked.connect(self.nav_to_tab2)
        self.btnTab4.clicked.connect(self.nav_to_tab3)
        self.btnTab5.clicked.connect(self.nav_to_tab4)
        self.btnTab6.clicked.connect(self.nav_to_tab5)
        self.btnTab7.clicked.connect(self.nav_to_tab6)

        # set GUI from code
        self._setGUI()
        self.edTargetHost.textChanged.connect(self._checkHostValue)

        # butttons of memory table
        self.btnAddRecordToMemoryTable.clicked.connect(self.getAndAddMemorySnapshotToTable)
        self.btnDelRecordFromMemoryTable.clicked.connect(self._removeRowFromMemoryTable)
        self.btnClearMemoryTable.clicked.connect(self._clearMemoryTable)
        self.btnStartMemoryLogging.clicked.connect(self._cyclicLogicHandler)

        # loggers
        self.btnLoadDmesg.clicked.connect(self.getAndAddDmesgToTable)
        self.btnLoadJournal.clicked.connect(self.getAndAddJournalToTable)

        # estabilish connection logic
        self.btnCheckConnection.clicked.connect(self._connectToTarget)
        self.btnTakeSnapshot.clicked.connect(self.takeSystemSnapshot)

        # bar menu + logo button
        self.actionAbout.triggered.connect(self._showAbout)
        self.actionClose.triggered.connect(self._exit)
        self.actionExport.triggered.connect(self._exportToExcel)
        self.btnLogo.clicked.connect(self._showAbout)

        # TAB manual command
        self.btnCallCmd.clicked.connect(self._callCommand)
        self.cboxCommand.currentIndexChanged.connect(self._copyCommand)
        self.btnCommandClear.clicked.connect(self._clearCommandTable)

        # self.cboxCommand.setEditable(True)
        # line_edit = self.cboxCommand.lineEdit()
        # line_edit.setAlignment(Qt.AlignCenter)

        # disk usage tab
        self.btnAddDiskUsage.clicked.connect(self.getAndAddDiskUsageTable)
        self.btnRemoveDiskUsage.clicked.connect(self._removeRowDiskUsageTable)
        self.btnClearDiskUsage.clicked.connect(self._clearDiskUsageTable)

        # processs usage tab
        self.btnAddRecordToProcessTable.clicked.connect(self.getAndAddProcessUsageTable)
        self.btnDelRecordFromProcessTable.clicked.connect(self._removeRowProcessUsageTable)
        self.btnClearProcessTable.clicked.connect(self._clearProcessUsageTable)

        # update status
        self._updateStatusBar()

        # class for charts initalization and connect signal to show chart
        self._memoryChartInitalization()
        self.btnShowMemoryChart.clicked.connect(self._showMemoryChart)




    def _memoryChartInitalization(self):
        """
         Memory chart initalization,
         -> title of chart is added
         -> title of axis X/Y is added
         -> all series are created with titles
        """

        # create instance of chart
        self.windowMemoryChart = chartWithTimeAxis("Memory overview", "time", "Size [Mi]")

        # set Window title and its icon
        self.windowMemoryChart.setWindowTitle("SSH Client")
        self.windowMemoryChart.setWindowIcon(PyQt5.QtGui.QIcon('GUI/pictures/bar-chart-2.svg'))

        # define series
        self.windowMemoryChart.addSeriesToChart("total")
        self.windowMemoryChart.addSeriesToChart("used")
        self.windowMemoryChart.addSeriesToChart("free")
        self.windowMemoryChart.addSeriesToChart("shared")
        self.windowMemoryChart.addSeriesToChart("buff/cache")
        self.windowMemoryChart.addSeriesToChart("available")
        self.windowMemoryChart.addSeriesToChart("swap total")
        self.windowMemoryChart.addSeriesToChart("swap used")
        self.windowMemoryChart.addSeriesToChart("swap free")

    def _showMemoryChart(self):
        """
         Show window with memory overview Chart
        """
        self.windowMemoryChart.show()
        self.windowMemoryChart.resize(800, 600)

    def _addPointToMemoryChart(self, idx, raw_value):

        """
        Add new point to memory chart series, raw value is string, so value is cleared from units and converted to int
        -> idx - index of series you would like to add point to
        -> raw_value - y value
        """

        # check if series is in Gi or in Mi, racalculate if need it.
        multipleIndex = 1
        if raw_value.find('Gi') != -1:
            multipleIndex = 1024


        # clear units from string
        itemWithoutUnit = raw_value.translate({ord(i): None for i in 'GiMiB'})

        # recalculate it
        value = math.trunc(float(itemWithoutUnit) * multipleIndex)

        # get current time
        dt = QDateTime.currentDateTime()

        # send value to series
        self.windowMemoryChart.addPointToSerie(idx, dt, int(value))

    # ----------------------
    # TAB PROCESS USAGE OVERVIEW
    # ----------------------
    def getAndAddProcessUsageTable(self):
        # get data from Linux server
        processUsageHeader, processUsageRows = self._linuxSSHConnector.getCmdByLinesHeader(CMD_GET_PROCESS)

        # add them to GUI
        self._updateTableWidget(processUsageHeader, processUsageRows, self.tableProcessOverview)

        # update all elements in GUI
        self._updateGUI()

    def _clearProcessUsageTable(self):
        self._clearTableWidget(self.tableProcessOverview)

    def _removeRowProcessUsageTable(self):
        self._removeRowFromTable(self.tableProcessOverview)

    # ----------------------
    # TAB DISK USAGE OVERVIEW
    # ----------------------
    def getAndAddDiskUsageTable(self):

        # get data from Linux server
        diskUsageHeader, diskUsageRows = self._linuxSSHConnector.getCmdByLinesHeader(CMD_GET_DISK_USAGE)

        # add them to GUI
        self._updateTableWidget(diskUsageHeader, diskUsageRows, self.tableDiskUsage)

        # update all elements in GUI
        self._updateGUI()

    def _clearDiskUsageTable(self):

        self._clearTableWidget(self.tableDiskUsage)

    def _removeRowDiskUsageTable(self):

        self._removeRowFromTable(self.tableDiskUsage)

    # ----------------------
    # TAB MEMORY USAGE OVERVIEW
    # ----------------------

    def _clearMemoryTable(self):

        self._clearTableWidget(self.tablewMemoryOverview)
        self.windowMemoryChart.clearAllSeries()

    def _removeRowFromMemoryTable(self):

        self._removeRowFromTable(self.tablewMemoryOverview)

    def getAndAddMemorySnapshotToTable(self):

        list = self._linuxSSHConnector.getMemorySnapshot()

        if list[1] != "-1":
            self._addRowToMemoryTable(list)
        elif self._timerMemoryLogging.isActive():
            self._timerMemoryLogging.stop()

        self._updateGUI()

    def _addRowToMemoryTable(self, parList):

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

            # add value to serie as well
            self._addPointToMemoryChart(columnIdx - 1, item)

            columnIdx += 1

            # in visu there is only 10 column available, if more items in list -> break it
            if (columnIdx == 10):
                break

    # ----------------------
    # TAB CALL COMMAND
    # ----------------------
    def _callCommand(self):
        list = self._linuxSSHConnector.getCmdByLines(self.edCommand.text())
        self._addRowsToTable(list, self.tableCommand)

    def _copyCommand(self):
        index = self.cboxCommand.currentIndex()

        if index == 0:
            self.edCommand.setText('')
        elif index == 1:
            self.edCommand.setText('/sbin/shutdown -r now')
        elif index == 2:
            self.edCommand.setText('free -h')
        elif index == 3:
            self.edCommand.setText('df -h')
        elif index == 4:
            self.edCommand.setText('ps aux')

    def _clearCommandTable(self):
        self._clearTableWidget(self.tableCommand)

    # ----------------------
    # TAB JOURNAL LOG OVERVIEW
    # ----------------------
    def getAndAddJournalToTable(self):
        # list = ['-- Journal begins at Fri 2000-01-07 17:51:32 UTC, ends at Sat 2000-01-08 02:06:49 UTC. --\n', 'Jan 07 17:51:32 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:59858).\n', 'Jan 07 17:51:32 br-automation1 dropbear[26880]: Child connection from ::ffff:10.0.0.100:59858\n', 'Jan 07 17:51:32 br-automation1 dropbear[26880]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 17:51:32 br-automation1 dropbear[26880]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:59858\n", 'Jan 07 17:51:33 br-automation1 dropbear[26880]: Exit (root) from <::ffff:10.0.0.100:59858>: Exited normally\n', 'Jan 07 17:51:33 br-automation1 systemd[1]: dropbear@2668-10.0.0.73:22-10.0.0.100:59858.service: Succeeded.\n', 'Jan 07 17:52:32 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:60052).\n', 'Jan 07 17:52:32 br-automation1 dropbear[27363]: Child connection from ::ffff:10.0.0.100:60052\n', 'Jan 07 17:52:32 br-automation1 dropbear[27363]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 17:52:32 br-automation1 dropbear[27363]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:60052\n", 'Jan 07 17:52:32 br-automation1 dropbear[27363]: Exit (root) from <::ffff:10.0.0.100:60052>: Exited normally\n', 'Jan 07 17:52:32 br-automation1 systemd[1]: dropbear@2669-10.0.0.73:22-10.0.0.100:60052.service: Succeeded.\n', 'Jan 07 17:53:32 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:60248).\n', 'Jan 07 17:53:32 br-automation1 dropbear[27852]: Child connection from ::ffff:10.0.0.100:60248\n', 'Jan 07 17:53:32 br-automation1 dropbear[27852]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 17:53:32 br-automation1 dropbear[27852]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:60248\n", 'Jan 07 17:53:32 br-automation1 dropbear[27852]: Exit (root) from <::ffff:10.0.0.100:60248>: Exited normally\n', 'Jan 07 17:53:32 br-automation1 systemd[1]: dropbear@2670-10.0.0.73:22-10.0.0.100:60248.service: Succeeded.\n', 'Jan 07 17:54:32 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:60434).\n', 'Jan 07 17:54:32 br-automation1 dropbear[28337]: Child connection from ::ffff:10.0.0.100:60434\n', 'Jan 07 17:54:32 br-automation1 dropbear[28337]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 17:54:32 br-automation1 dropbear[28337]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:60434\n", 'Jan 07 17:54:32 br-automation1 dropbear[28337]: Exit (root) from <::ffff:10.0.0.100:60434>: Exited normally\n', 'Jan 07 17:54:32 br-automation1 systemd[1]: dropbear@2671-10.0.0.73:22-10.0.0.100:60434.service: Succeeded.\n', 'Jan 07 17:55:32 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:60611).\n', 'Jan 07 17:55:32 br-automation1 dropbear[28822]: Child connection from ::ffff:10.0.0.100:60611\n', 'Jan 07 17:55:32 br-automation1 dropbear[28822]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 17:55:32 br-automation1 dropbear[28822]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:60611\n", 'Jan 07 17:55:32 br-automation1 dropbear[28822]: Exit (root) from <::ffff:10.0.0.100:60611>: Error reading: Connection reset by peer\n', 'Jan 07 17:55:32 br-automation1 systemd[1]: dropbear@2672-10.0.0.73:22-10.0.0.100:60611.service: Succeeded.\n', 'Jan 07 17:56:32 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:60803).\n', 'Jan 07 17:56:32 br-automation1 dropbear[29305]: Child connection from ::ffff:10.0.0.100:60803\n', 'Jan 07 17:56:32 br-automation1 dropbear[29305]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 17:56:32 br-automation1 dropbear[29305]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:60803\n", 'Jan 07 17:56:32 br-automation1 dropbear[29305]: Exit (root) from <::ffff:10.0.0.100:60803>: Exited normally\n', 'Jan 07 17:56:32 br-automation1 systemd[1]: dropbear@2673-10.0.0.73:22-10.0.0.100:60803.service: Succeeded.\n', 'Jan 07 17:57:32 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:60997).\n', 'Jan 07 17:57:32 br-automation1 dropbear[29792]: Child connection from ::ffff:10.0.0.100:60997\n', 'Jan 07 17:57:32 br-automation1 dropbear[29792]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 17:57:32 br-automation1 dropbear[29792]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:60997\n", 'Jan 07 17:57:32 br-automation1 dropbear[29792]: Exit (root) from <::ffff:10.0.0.100:60997>: Exited normally\n', 'Jan 07 17:57:32 br-automation1 systemd[1]: dropbear@2674-10.0.0.73:22-10.0.0.100:60997.service: Succeeded.\n', 'Jan 07 17:58:32 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:61186).\n', 'Jan 07 17:58:32 br-automation1 dropbear[30277]: Child connection from ::ffff:10.0.0.100:61186\n', 'Jan 07 17:58:32 br-automation1 dropbear[30277]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 17:58:32 br-automation1 dropbear[30277]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:61186\n", 'Jan 07 17:58:32 br-automation1 dropbear[30277]: Exit (root) from <::ffff:10.0.0.100:61186>: Exited normally\n', 'Jan 07 17:58:32 br-automation1 systemd[1]: dropbear@2675-10.0.0.73:22-10.0.0.100:61186.service: Succeeded.\n', 'Jan 07 17:59:32 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:61375).\n', 'Jan 07 17:59:32 br-automation1 dropbear[30758]: Child connection from ::ffff:10.0.0.100:61375\n', 'Jan 07 17:59:32 br-automation1 dropbear[30758]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 17:59:32 br-automation1 dropbear[30758]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:61375\n", 'Jan 07 17:59:32 br-automation1 dropbear[30758]: Exit (root) from <::ffff:10.0.0.100:61375>: Exited normally\n', 'Jan 07 17:59:32 br-automation1 systemd[1]: dropbear@2676-10.0.0.73:22-10.0.0.100:61375.service: Succeeded.\n', 'Jan 07 18:00:32 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:61558).\n', 'Jan 07 18:00:32 br-automation1 dropbear[31241]: Child connection from ::ffff:10.0.0.100:61558\n', 'Jan 07 18:00:32 br-automation1 dropbear[31241]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:00:32 br-automation1 dropbear[31241]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:61558\n", 'Jan 07 18:00:32 br-automation1 dropbear[31241]: Exit (root) from <::ffff:10.0.0.100:61558>: Error reading: Connection reset by peer\n', 'Jan 07 18:00:32 br-automation1 systemd[1]: dropbear@2677-10.0.0.73:22-10.0.0.100:61558.service: Succeeded.\n', 'Jan 07 18:01:32 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:61738).\n', 'Jan 07 18:01:32 br-automation1 dropbear[31732]: Child connection from ::ffff:10.0.0.100:61738\n', 'Jan 07 18:01:32 br-automation1 dropbear[31732]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:01:32 br-automation1 dropbear[31732]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:61738\n", 'Jan 07 18:01:32 br-automation1 dropbear[31732]: Exit (root) from <::ffff:10.0.0.100:61738>: Exited normally\n', 'Jan 07 18:01:32 br-automation1 systemd[1]: dropbear@2678-10.0.0.73:22-10.0.0.100:61738.service: Succeeded.\n', 'Jan 07 18:02:32 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:61937).\n', 'Jan 07 18:02:32 br-automation1 dropbear[32214]: Child connection from ::ffff:10.0.0.100:61937\n', 'Jan 07 18:02:32 br-automation1 dropbear[32214]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:02:32 br-automation1 dropbear[32214]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:61937\n", 'Jan 07 18:02:32 br-automation1 dropbear[32214]: Exit (root) from <::ffff:10.0.0.100:61937>: Exited normally\n', 'Jan 07 18:02:32 br-automation1 systemd[1]: dropbear@2679-10.0.0.73:22-10.0.0.100:61937.service: Succeeded.\n', 'Jan 07 18:03:32 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:62127).\n', 'Jan 07 18:03:32 br-automation1 dropbear[32696]: Child connection from ::ffff:10.0.0.100:62127\n', 'Jan 07 18:03:32 br-automation1 dropbear[32696]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:03:32 br-automation1 dropbear[32696]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:62127\n", 'Jan 07 18:03:32 br-automation1 dropbear[32696]: Exit (root) from <::ffff:10.0.0.100:62127>: Exited normally\n', 'Jan 07 18:03:32 br-automation1 systemd[1]: dropbear@2680-10.0.0.73:22-10.0.0.100:62127.service: Succeeded.\n', 'Jan 07 18:04:32 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:62314).\n', 'Jan 07 18:04:32 br-automation1 dropbear[728]: Child connection from ::ffff:10.0.0.100:62314\n', 'Jan 07 18:04:32 br-automation1 dropbear[728]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:04:32 br-automation1 dropbear[728]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:62314\n", 'Jan 07 18:04:32 br-automation1 dropbear[728]: Exit (root) from <::ffff:10.0.0.100:62314>: Exited normally\n', 'Jan 07 18:04:32 br-automation1 systemd[1]: dropbear@2681-10.0.0.73:22-10.0.0.100:62314.service: Succeeded.\n', 'Jan 07 18:05:32 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:62500).\n', 'Jan 07 18:05:32 br-automation1 dropbear[1216]: Child connection from ::ffff:10.0.0.100:62500\n', 'Jan 07 18:05:32 br-automation1 dropbear[1216]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:05:32 br-automation1 dropbear[1216]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:62500\n", 'Jan 07 18:05:32 br-automation1 dropbear[1216]: Exit (root) from <::ffff:10.0.0.100:62500>: Exited normally\n', 'Jan 07 18:05:32 br-automation1 systemd[1]: dropbear@2682-10.0.0.73:22-10.0.0.100:62500.service: Succeeded.\n', 'Jan 07 18:06:32 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:62688).\n', 'Jan 07 18:06:32 br-automation1 dropbear[1702]: Child connection from ::ffff:10.0.0.100:62688\n', 'Jan 07 18:06:32 br-automation1 dropbear[1702]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:06:32 br-automation1 dropbear[1702]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:62688\n", 'Jan 07 18:06:32 br-automation1 dropbear[1702]: Exit (root) from <::ffff:10.0.0.100:62688>: Exited normally\n', 'Jan 07 18:06:32 br-automation1 systemd[1]: dropbear@2683-10.0.0.73:22-10.0.0.100:62688.service: Succeeded.\n', 'Jan 07 18:07:32 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:62901).\n', 'Jan 07 18:07:32 br-automation1 dropbear[2183]: Child connection from ::ffff:10.0.0.100:62901\n', 'Jan 07 18:07:32 br-automation1 dropbear[2183]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:07:32 br-automation1 dropbear[2183]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:62901\n", 'Jan 07 18:07:32 br-automation1 dropbear[2183]: Exit (root) from <::ffff:10.0.0.100:62901>: Exited normally\n', 'Jan 07 18:07:32 br-automation1 systemd[1]: dropbear@2684-10.0.0.73:22-10.0.0.100:62901.service: Succeeded.\n', 'Jan 07 18:08:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:63085).\n', 'Jan 07 18:08:31 br-automation1 dropbear[2666]: Child connection from ::ffff:10.0.0.100:63085\n', 'Jan 07 18:08:32 br-automation1 dropbear[2666]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:08:32 br-automation1 dropbear[2666]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:63085\n", 'Jan 07 18:08:32 br-automation1 dropbear[2666]: Exit (root) from <::ffff:10.0.0.100:63085>: Exited normally\n', 'Jan 07 18:08:32 br-automation1 systemd[1]: dropbear@2685-10.0.0.73:22-10.0.0.100:63085.service: Succeeded.\n', 'Jan 07 18:09:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:63275).\n', 'Jan 07 18:09:31 br-automation1 dropbear[3158]: Child connection from ::ffff:10.0.0.100:63275\n', 'Jan 07 18:09:32 br-automation1 dropbear[3158]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:09:32 br-automation1 dropbear[3158]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:63275\n", 'Jan 07 18:09:32 br-automation1 dropbear[3158]: Exit (root) from <::ffff:10.0.0.100:63275>: Exited normally\n', 'Jan 07 18:09:32 br-automation1 systemd[1]: dropbear@2686-10.0.0.73:22-10.0.0.100:63275.service: Succeeded.\n', 'Jan 07 18:10:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:63470).\n', 'Jan 07 18:10:31 br-automation1 dropbear[3639]: Child connection from ::ffff:10.0.0.100:63470\n', 'Jan 07 18:10:32 br-automation1 dropbear[3639]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:10:32 br-automation1 dropbear[3639]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:63470\n", 'Jan 07 18:10:32 br-automation1 dropbear[3639]: Exit (root) from <::ffff:10.0.0.100:63470>: Exited normally\n', 'Jan 07 18:10:32 br-automation1 systemd[1]: dropbear@2687-10.0.0.73:22-10.0.0.100:63470.service: Succeeded.\n', 'Jan 07 18:11:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:63651).\n', 'Jan 07 18:11:31 br-automation1 dropbear[4123]: Child connection from ::ffff:10.0.0.100:63651\n', 'Jan 07 18:11:32 br-automation1 dropbear[4123]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:11:32 br-automation1 dropbear[4123]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:63651\n", 'Jan 07 18:11:32 br-automation1 dropbear[4123]: Exit (root) from <::ffff:10.0.0.100:63651>: Exited normally\n', 'Jan 07 18:11:32 br-automation1 systemd[1]: dropbear@2688-10.0.0.73:22-10.0.0.100:63651.service: Succeeded.\n', 'Jan 07 18:12:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:63848).\n', 'Jan 07 18:12:31 br-automation1 dropbear[4609]: Child connection from ::ffff:10.0.0.100:63848\n', 'Jan 07 18:12:32 br-automation1 dropbear[4609]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:12:32 br-automation1 dropbear[4609]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:63848\n", 'Jan 07 18:12:32 br-automation1 dropbear[4609]: Exit (root) from <::ffff:10.0.0.100:63848>: Exited normally\n', 'Jan 07 18:12:32 br-automation1 systemd[1]: dropbear@2689-10.0.0.73:22-10.0.0.100:63848.service: Succeeded.\n', 'Jan 07 18:13:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:64039).\n', 'Jan 07 18:13:31 br-automation1 dropbear[5095]: Child connection from ::ffff:10.0.0.100:64039\n', 'Jan 07 18:13:32 br-automation1 dropbear[5095]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:13:32 br-automation1 dropbear[5095]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:64039\n", 'Jan 07 18:13:32 br-automation1 dropbear[5095]: Exit (root) from <::ffff:10.0.0.100:64039>: Error reading: Connection reset by peer\n', 'Jan 07 18:13:32 br-automation1 systemd[1]: dropbear@2690-10.0.0.73:22-10.0.0.100:64039.service: Succeeded.\n', 'Jan 07 18:14:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:64232).\n', 'Jan 07 18:14:31 br-automation1 dropbear[5578]: Child connection from ::ffff:10.0.0.100:64232\n', 'Jan 07 18:14:32 br-automation1 dropbear[5578]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:14:32 br-automation1 dropbear[5578]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:64232\n", 'Jan 07 18:14:32 br-automation1 dropbear[5578]: Exit (root) from <::ffff:10.0.0.100:64232>: Exited normally\n', 'Jan 07 18:14:32 br-automation1 systemd[1]: dropbear@2691-10.0.0.73:22-10.0.0.100:64232.service: Succeeded.\n', 'Jan 07 18:15:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:64421).\n', 'Jan 07 18:15:31 br-automation1 dropbear[6059]: Child connection from ::ffff:10.0.0.100:64421\n', 'Jan 07 18:15:32 br-automation1 dropbear[6059]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:15:32 br-automation1 dropbear[6059]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:64421\n", 'Jan 07 18:15:32 br-automation1 dropbear[6059]: Exit (root) from <::ffff:10.0.0.100:64421>: Error reading: Connection reset by peer\n', 'Jan 07 18:15:32 br-automation1 systemd[1]: dropbear@2692-10.0.0.73:22-10.0.0.100:64421.service: Succeeded.\n', 'Jan 07 18:16:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:64615).\n', 'Jan 07 18:16:31 br-automation1 dropbear[6550]: Child connection from ::ffff:10.0.0.100:64615\n', 'Jan 07 18:16:32 br-automation1 dropbear[6550]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:16:32 br-automation1 dropbear[6550]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:64615\n", 'Jan 07 18:16:32 br-automation1 dropbear[6550]: Exit (root) from <::ffff:10.0.0.100:64615>: Exited normally\n', 'Jan 07 18:16:32 br-automation1 systemd[1]: dropbear@2693-10.0.0.73:22-10.0.0.100:64615.service: Succeeded.\n', 'Jan 07 18:17:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:64807).\n', 'Jan 07 18:17:31 br-automation1 dropbear[7035]: Child connection from ::ffff:10.0.0.100:64807\n', 'Jan 07 18:17:32 br-automation1 dropbear[7035]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:17:32 br-automation1 dropbear[7035]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:64807\n", 'Jan 07 18:17:32 br-automation1 dropbear[7035]: Exit (root) from <::ffff:10.0.0.100:64807>: Exited normally\n', 'Jan 07 18:17:32 br-automation1 systemd[1]: dropbear@2694-10.0.0.73:22-10.0.0.100:64807.service: Succeeded.\n', 'Jan 07 18:18:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:64996).\n', 'Jan 07 18:18:31 br-automation1 dropbear[7516]: Child connection from ::ffff:10.0.0.100:64996\n', 'Jan 07 18:18:31 br-automation1 dropbear[7516]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:18:31 br-automation1 dropbear[7516]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:64996\n", 'Jan 07 18:18:32 br-automation1 dropbear[7516]: Exit (root) from <::ffff:10.0.0.100:64996>: Exited normally\n', 'Jan 07 18:18:32 br-automation1 systemd[1]: dropbear@2695-10.0.0.73:22-10.0.0.100:64996.service: Succeeded.\n', 'Jan 07 18:19:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:65182).\n', 'Jan 07 18:19:31 br-automation1 dropbear[7997]: Child connection from ::ffff:10.0.0.100:65182\n', 'Jan 07 18:19:31 br-automation1 dropbear[7997]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:19:31 br-automation1 dropbear[7997]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:65182\n", 'Jan 07 18:19:32 br-automation1 dropbear[7997]: Exit (root) from <::ffff:10.0.0.100:65182>: Exited normally\n', 'Jan 07 18:19:32 br-automation1 systemd[1]: dropbear@2696-10.0.0.73:22-10.0.0.100:65182.service: Succeeded.\n', 'Jan 07 18:20:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:65362).\n', 'Jan 07 18:20:31 br-automation1 dropbear[8486]: Child connection from ::ffff:10.0.0.100:65362\n', 'Jan 07 18:20:31 br-automation1 dropbear[8486]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:20:31 br-automation1 dropbear[8486]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:65362\n", 'Jan 07 18:20:32 br-automation1 dropbear[8486]: Exit (root) from <::ffff:10.0.0.100:65362>: Exited normally\n', 'Jan 07 18:20:32 br-automation1 systemd[1]: dropbear@2697-10.0.0.73:22-10.0.0.100:65362.service: Succeeded.\n', 'Jan 07 18:21:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:49167).\n', 'Jan 07 18:21:31 br-automation1 dropbear[8973]: Child connection from ::ffff:10.0.0.100:49167\n', 'Jan 07 18:21:31 br-automation1 dropbear[8973]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:21:31 br-automation1 dropbear[8973]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:49167\n", 'Jan 07 18:21:31 br-automation1 dropbear[8973]: Exit (root) from <::ffff:10.0.0.100:49167>: Error reading: Connection reset by peer\n', 'Jan 07 18:21:31 br-automation1 systemd[1]: dropbear@2698-10.0.0.73:22-10.0.0.100:49167.service: Succeeded.\n', 'Jan 07 18:22:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:49371).\n', 'Jan 07 18:22:31 br-automation1 dropbear[9454]: Child connection from ::ffff:10.0.0.100:49371\n', 'Jan 07 18:22:31 br-automation1 dropbear[9454]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:22:31 br-automation1 dropbear[9454]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:49371\n", 'Jan 07 18:22:31 br-automation1 dropbear[9454]: Exit (root) from <::ffff:10.0.0.100:49371>: Error reading: Connection reset by peer\n', 'Jan 07 18:22:31 br-automation1 systemd[1]: dropbear@2699-10.0.0.73:22-10.0.0.100:49371.service: Succeeded.\n', 'Jan 07 18:23:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:49847).\n', 'Jan 07 18:23:31 br-automation1 dropbear[9937]: Child connection from ::ffff:10.0.0.100:49847\n', 'Jan 07 18:23:31 br-automation1 dropbear[9937]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:23:31 br-automation1 dropbear[9937]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:49847\n", 'Jan 07 18:23:31 br-automation1 dropbear[9937]: Exit (root) from <::ffff:10.0.0.100:49847>: Exited normally\n', 'Jan 07 18:23:31 br-automation1 systemd[1]: dropbear@2700-10.0.0.73:22-10.0.0.100:49847.service: Succeeded.\n', 'Jan 07 18:24:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:50064).\n', 'Jan 07 18:24:31 br-automation1 dropbear[10426]: Child connection from ::ffff:10.0.0.100:50064\n', 'Jan 07 18:24:31 br-automation1 dropbear[10426]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:24:31 br-automation1 dropbear[10426]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:50064\n", 'Jan 07 18:24:31 br-automation1 dropbear[10426]: Exit (root) from <::ffff:10.0.0.100:50064>: Exited normally\n', 'Jan 07 18:24:31 br-automation1 systemd[1]: dropbear@2701-10.0.0.73:22-10.0.0.100:50064.service: Succeeded.\n', 'Jan 07 18:25:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:50246).\n', 'Jan 07 18:25:31 br-automation1 dropbear[10910]: Child connection from ::ffff:10.0.0.100:50246\n', 'Jan 07 18:25:31 br-automation1 dropbear[10910]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:25:31 br-automation1 dropbear[10910]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:50246\n", 'Jan 07 18:25:31 br-automation1 dropbear[10910]: Exit (root) from <::ffff:10.0.0.100:50246>: Exited normally\n', 'Jan 07 18:25:31 br-automation1 systemd[1]: dropbear@2702-10.0.0.73:22-10.0.0.100:50246.service: Succeeded.\n', 'Jan 07 18:26:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:50429).\n', 'Jan 07 18:26:31 br-automation1 dropbear[11394]: Child connection from ::ffff:10.0.0.100:50429\n', 'Jan 07 18:26:31 br-automation1 dropbear[11394]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:26:31 br-automation1 dropbear[11394]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:50429\n", 'Jan 07 18:26:31 br-automation1 dropbear[11394]: Exit (root) from <::ffff:10.0.0.100:50429>: Exited normally\n', 'Jan 07 18:26:31 br-automation1 systemd[1]: dropbear@2703-10.0.0.73:22-10.0.0.100:50429.service: Succeeded.\n', 'Jan 07 18:27:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:50628).\n', 'Jan 07 18:27:31 br-automation1 dropbear[11878]: Child connection from ::ffff:10.0.0.100:50628\n', 'Jan 07 18:27:31 br-automation1 dropbear[11878]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:27:31 br-automation1 dropbear[11878]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:50628\n", 'Jan 07 18:27:31 br-automation1 dropbear[11878]: Exit (root) from <::ffff:10.0.0.100:50628>: Exited normally\n', 'Jan 07 18:27:31 br-automation1 systemd[1]: dropbear@2704-10.0.0.73:22-10.0.0.100:50628.service: Succeeded.\n', 'Jan 07 18:28:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:50822).\n', 'Jan 07 18:28:31 br-automation1 dropbear[12366]: Child connection from ::ffff:10.0.0.100:50822\n', 'Jan 07 18:28:31 br-automation1 dropbear[12366]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:28:31 br-automation1 dropbear[12366]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:50822\n", 'Jan 07 18:28:31 br-automation1 dropbear[12366]: Exit (root) from <::ffff:10.0.0.100:50822>: Exited normally\n', 'Jan 07 18:28:31 br-automation1 systemd[1]: dropbear@2705-10.0.0.73:22-10.0.0.100:50822.service: Succeeded.\n', 'Jan 07 18:29:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:51010).\n', 'Jan 07 18:29:31 br-automation1 dropbear[12849]: Child connection from ::ffff:10.0.0.100:51010\n', 'Jan 07 18:29:31 br-automation1 dropbear[12849]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:29:31 br-automation1 dropbear[12849]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:51010\n", 'Jan 07 18:29:31 br-automation1 dropbear[12849]: Exit (root) from <::ffff:10.0.0.100:51010>: Exited normally\n', 'Jan 07 18:29:31 br-automation1 systemd[1]: dropbear@2706-10.0.0.73:22-10.0.0.100:51010.service: Succeeded.\n', 'Jan 07 18:30:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:51191).\n', 'Jan 07 18:30:31 br-automation1 dropbear[13330]: Child connection from ::ffff:10.0.0.100:51191\n', 'Jan 07 18:30:31 br-automation1 dropbear[13330]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:30:31 br-automation1 dropbear[13330]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:51191\n", 'Jan 07 18:30:31 br-automation1 dropbear[13330]: Exit (root) from <::ffff:10.0.0.100:51191>: Exited normally\n', 'Jan 07 18:30:31 br-automation1 systemd[1]: dropbear@2707-10.0.0.73:22-10.0.0.100:51191.service: Succeeded.\n', 'Jan 07 18:30:56 br-automation1 dropbear[2936]: Exit (root) from <::ffff:10.0.0.100:50843>: Exited normally\n', 'Jan 07 18:30:56 br-automation1 systemd[1]: dropbear@1614-10.0.0.73:22-10.0.0.100:50843.service: Succeeded.\n', 'Jan 07 18:31:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:51417).\n', 'Jan 07 18:31:31 br-automation1 dropbear[13818]: Child connection from ::ffff:10.0.0.100:51417\n', 'Jan 07 18:31:31 br-automation1 dropbear[13818]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:31:31 br-automation1 dropbear[13818]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:51417\n", 'Jan 07 18:31:31 br-automation1 dropbear[13818]: Exit (root) from <::ffff:10.0.0.100:51417>: Error reading: Connection reset by peer\n', 'Jan 07 18:31:31 br-automation1 systemd[1]: dropbear@2708-10.0.0.73:22-10.0.0.100:51417.service: Succeeded.\n', 'Jan 07 18:32:31 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:51621).\n', 'Jan 07 18:32:31 br-automation1 dropbear[14307]: Child connection from ::ffff:10.0.0.100:51621\n', 'Jan 07 18:32:31 br-automation1 dropbear[14307]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:32:31 br-automation1 dropbear[14307]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:51621\n", 'Jan 07 18:32:32 br-automation1 dropbear[14307]: Exit (root) from <::ffff:10.0.0.100:51621>: Exited normally\n', 'Jan 07 18:32:32 br-automation1 systemd[1]: dropbear@2709-10.0.0.73:22-10.0.0.100:51621.service: Succeeded.\n', 'Jan 07 18:38:17 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:52778).\n', 'Jan 07 18:38:17 br-automation1 dropbear[17093]: Child connection from ::ffff:10.0.0.100:52778\n', 'Jan 07 18:38:18 br-automation1 dropbear[17093]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:38:18 br-automation1 dropbear[17093]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:52778\n", 'Jan 07 18:38:27 br-automation1 dropbear[17093]: Exit (root) from <::ffff:10.0.0.100:52778>: Exited normally\n', 'Jan 07 18:38:27 br-automation1 systemd[1]: dropbear@2710-10.0.0.73:22-10.0.0.100:52778.service: Succeeded.\n', 'Jan 07 18:38:32 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:52814).\n', 'Jan 07 18:38:32 br-automation1 dropbear[17208]: Child connection from ::ffff:10.0.0.100:52814\n', 'Jan 07 18:38:32 br-automation1 dropbear[17208]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:38:32 br-automation1 dropbear[17208]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:52814\n", 'Jan 07 18:51:07 br-automation1 dropbear[17208]: Exit (root) from <::ffff:10.0.0.100:52814>: Error reading: Connection reset by peer\n', 'Jan 07 18:51:07 br-automation1 systemd[1]: dropbear@2711-10.0.0.73:22-10.0.0.100:52814.service: Succeeded.\n', 'Jan 07 18:55:17 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:60110).\n', 'Jan 07 18:55:17 br-automation1 dropbear[25277]: Child connection from ::ffff:10.0.0.100:60110\n', 'Jan 07 18:55:17 br-automation1 dropbear[25277]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:55:17 br-automation1 dropbear[25277]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:60110\n", 'Jan 07 18:55:17 br-automation1 dropbear[25277]: Exit (root) from <::ffff:10.0.0.100:60110>: Exited normally\n', 'Jan 07 18:55:17 br-automation1 systemd[1]: dropbear@2712-10.0.0.73:22-10.0.0.100:60110.service: Succeeded.\n', 'Jan 07 18:56:47 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:61427).\n', 'Jan 07 18:56:47 br-automation1 dropbear[26009]: Child connection from ::ffff:10.0.0.100:61427\n', 'Jan 07 18:56:47 br-automation1 dropbear[26009]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:56:47 br-automation1 dropbear[26009]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:61427\n", 'Jan 07 18:56:47 br-automation1 dropbear[26009]: Exit (root) from <::ffff:10.0.0.100:61427>: Error reading: Connection reset by peer\n', 'Jan 07 18:56:47 br-automation1 systemd[1]: dropbear@2713-10.0.0.73:22-10.0.0.100:61427.service: Succeeded.\n', 'Jan 07 18:57:46 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:61613).\n', 'Jan 07 18:57:46 br-automation1 dropbear[26492]: Child connection from ::ffff:10.0.0.100:61613\n', 'Jan 07 18:57:47 br-automation1 dropbear[26492]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:57:47 br-automation1 dropbear[26492]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:61613\n", 'Jan 07 18:57:47 br-automation1 dropbear[26492]: Exit (root) from <::ffff:10.0.0.100:61613>: Error reading: Connection reset by peer\n', 'Jan 07 18:57:47 br-automation1 systemd[1]: dropbear@2714-10.0.0.73:22-10.0.0.100:61613.service: Succeeded.\n', 'Jan 07 18:58:47 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:62843).\n', 'Jan 07 18:58:47 br-automation1 dropbear[26975]: Child connection from ::ffff:10.0.0.100:62843\n', 'Jan 07 18:58:47 br-automation1 dropbear[26975]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:58:47 br-automation1 dropbear[26975]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:62843\n", 'Jan 07 18:58:47 br-automation1 dropbear[26975]: Exit (root) from <::ffff:10.0.0.100:62843>: Exited normally\n', 'Jan 07 18:58:47 br-automation1 systemd[1]: dropbear@2715-10.0.0.73:22-10.0.0.100:62843.service: Succeeded.\n', 'Jan 07 18:59:46 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:63023).\n', 'Jan 07 18:59:46 br-automation1 dropbear[27456]: Child connection from ::ffff:10.0.0.100:63023\n', 'Jan 07 18:59:47 br-automation1 dropbear[27456]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 18:59:47 br-automation1 dropbear[27456]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:63023\n", 'Jan 07 18:59:47 br-automation1 dropbear[27456]: Exit (root) from <::ffff:10.0.0.100:63023>: Exited normally\n', 'Jan 07 18:59:47 br-automation1 systemd[1]: dropbear@2716-10.0.0.73:22-10.0.0.100:63023.service: Succeeded.\n', 'Jan 07 19:00:47 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:63223).\n', 'Jan 07 19:00:47 br-automation1 dropbear[27949]: Child connection from ::ffff:10.0.0.100:63223\n', 'Jan 07 19:00:47 br-automation1 dropbear[27949]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:00:47 br-automation1 dropbear[27949]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:63223\n", 'Jan 07 19:00:47 br-automation1 dropbear[27949]: Exit (root) from <::ffff:10.0.0.100:63223>: Exited normally\n', 'Jan 07 19:00:47 br-automation1 systemd[1]: dropbear@2717-10.0.0.73:22-10.0.0.100:63223.service: Succeeded.\n', 'Jan 07 19:01:46 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:64449).\n', 'Jan 07 19:01:46 br-automation1 dropbear[28429]: Child connection from ::ffff:10.0.0.100:64449\n', 'Jan 07 19:01:47 br-automation1 dropbear[28429]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:01:47 br-automation1 dropbear[28429]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:64449\n", 'Jan 07 19:01:47 br-automation1 dropbear[28429]: Exit (root) from <::ffff:10.0.0.100:64449>: Error reading: Connection reset by peer\n', 'Jan 07 19:01:47 br-automation1 systemd[1]: dropbear@2718-10.0.0.73:22-10.0.0.100:64449.service: Succeeded.\n', 'Jan 07 19:02:47 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:64636).\n', 'Jan 07 19:02:47 br-automation1 dropbear[28914]: Child connection from ::ffff:10.0.0.100:64636\n', 'Jan 07 19:02:47 br-automation1 dropbear[28914]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:02:47 br-automation1 dropbear[28914]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:64636\n", 'Jan 07 19:02:47 br-automation1 dropbear[28914]: Exit (root) from <::ffff:10.0.0.100:64636>: Error reading: Connection reset by peer\n', 'Jan 07 19:02:47 br-automation1 systemd[1]: dropbear@2719-10.0.0.73:22-10.0.0.100:64636.service: Succeeded.\n', 'Jan 07 19:03:46 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:64834).\n', 'Jan 07 19:03:46 br-automation1 dropbear[29395]: Child connection from ::ffff:10.0.0.100:64834\n', 'Jan 07 19:03:46 br-automation1 dropbear[29395]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:03:46 br-automation1 dropbear[29395]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:64834\n", 'Jan 07 19:03:47 br-automation1 dropbear[29395]: Exit (root) from <::ffff:10.0.0.100:64834>: Exited normally\n', 'Jan 07 19:03:47 br-automation1 systemd[1]: dropbear@2720-10.0.0.73:22-10.0.0.100:64834.service: Succeeded.\n', 'Jan 07 19:04:47 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:65012).\n', 'Jan 07 19:04:47 br-automation1 dropbear[29887]: Child connection from ::ffff:10.0.0.100:65012\n', 'Jan 07 19:04:47 br-automation1 dropbear[29887]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:04:47 br-automation1 dropbear[29887]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:65012\n", 'Jan 07 19:04:47 br-automation1 dropbear[29887]: Exit (root) from <::ffff:10.0.0.100:65012>: Exited normally\n', 'Jan 07 19:04:47 br-automation1 systemd[1]: dropbear@2721-10.0.0.73:22-10.0.0.100:65012.service: Succeeded.\n', 'Jan 07 19:05:46 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:65199).\n', 'Jan 07 19:05:46 br-automation1 dropbear[30368]: Child connection from ::ffff:10.0.0.100:65199\n', 'Jan 07 19:05:46 br-automation1 dropbear[30368]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:05:46 br-automation1 dropbear[30368]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:65199\n", 'Jan 07 19:05:46 br-automation1 dropbear[30368]: Exit (root) from <::ffff:10.0.0.100:65199>: Error reading: Connection reset by peer\n', 'Jan 07 19:05:46 br-automation1 systemd[1]: dropbear@2722-10.0.0.73:22-10.0.0.100:65199.service: Succeeded.\n', 'Jan 07 19:06:46 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:65379).\n', 'Jan 07 19:06:47 br-automation1 dropbear[30851]: Child connection from ::ffff:10.0.0.100:65379\n', 'Jan 07 19:06:47 br-automation1 dropbear[30851]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:06:47 br-automation1 dropbear[30851]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:65379\n", 'Jan 07 19:06:47 br-automation1 dropbear[30851]: Exit (root) from <::ffff:10.0.0.100:65379>: Error reading: Connection reset by peer\n', 'Jan 07 19:06:47 br-automation1 systemd[1]: dropbear@2723-10.0.0.73:22-10.0.0.100:65379.service: Succeeded.\n', 'Jan 07 19:18:50 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:53785).\n', 'Jan 07 19:18:50 br-automation1 dropbear[4217]: Child connection from ::ffff:10.0.0.100:53785\n', 'Jan 07 19:18:50 br-automation1 dropbear[4217]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:18:50 br-automation1 dropbear[4217]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:53785\n", 'Jan 07 19:18:54 br-automation1 dropbear[4217]: Exit (root) from <::ffff:10.0.0.100:53785>: Exited normally\n', 'Jan 07 19:18:54 br-automation1 systemd[1]: dropbear@2724-10.0.0.73:22-10.0.0.100:53785.service: Succeeded.\n', 'Jan 07 19:18:59 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:53806).\n', 'Jan 07 19:18:59 br-automation1 dropbear[4293]: Child connection from ::ffff:10.0.0.100:53806\n', 'Jan 07 19:18:59 br-automation1 dropbear[4293]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:18:59 br-automation1 dropbear[4293]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:53806\n", 'Jan 07 19:19:02 br-automation1 dropbear[4293]: Exit (root) from <::ffff:10.0.0.100:53806>: Exited normally\n', 'Jan 07 19:19:02 br-automation1 systemd[1]: dropbear@2725-10.0.0.73:22-10.0.0.100:53806.service: Succeeded.\n', 'Jan 07 19:19:07 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:53853).\n', 'Jan 07 19:19:07 br-automation1 dropbear[4360]: Child connection from ::ffff:10.0.0.100:53853\n', 'Jan 07 19:19:08 br-automation1 dropbear[4360]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:19:08 br-automation1 dropbear[4360]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:53853\n", 'Jan 07 19:24:34 br-automation1 dropbear[4360]: Exit (root) from <::ffff:10.0.0.100:53853>: Exited normally\n', 'Jan 07 19:24:34 br-automation1 systemd[1]: dropbear@2726-10.0.0.73:22-10.0.0.100:53853.service: Succeeded.\n', 'Jan 07 19:25:42 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:55111).\n', 'Jan 07 19:25:42 br-automation1 dropbear[7533]: Child connection from ::ffff:10.0.0.100:55111\n', 'Jan 07 19:25:42 br-automation1 dropbear[7533]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:25:42 br-automation1 dropbear[7533]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:55111\n", 'Jan 07 19:25:46 br-automation1 dropbear[7533]: Exit (root) from <::ffff:10.0.0.100:55111>: Exited normally\n', 'Jan 07 19:25:46 br-automation1 systemd[1]: dropbear@2727-10.0.0.73:22-10.0.0.100:55111.service: Succeeded.\n', 'Jan 07 19:25:47 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:55142).\n', 'Jan 07 19:25:47 br-automation1 dropbear[7573]: Child connection from ::ffff:10.0.0.100:55142\n', 'Jan 07 19:25:48 br-automation1 dropbear[7573]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:25:48 br-automation1 dropbear[7573]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:55142\n", 'Jan 07 19:25:50 br-automation1 dropbear[7573]: Exit (root) from <::ffff:10.0.0.100:55142>: Exited normally\n', 'Jan 07 19:25:50 br-automation1 systemd[1]: dropbear@2728-10.0.0.73:22-10.0.0.100:55142.service: Succeeded.\n', 'Jan 07 19:25:51 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:55150).\n', 'Jan 07 19:25:51 br-automation1 dropbear[7601]: Child connection from ::ffff:10.0.0.100:55150\n', 'Jan 07 19:25:51 br-automation1 dropbear[7601]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:25:51 br-automation1 dropbear[7601]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:55150\n", 'Jan 07 19:26:26 br-automation1 dropbear[7601]: Exit (root) from <::ffff:10.0.0.100:55150>: Exited normally\n', 'Jan 07 19:26:26 br-automation1 systemd[1]: dropbear@2729-10.0.0.73:22-10.0.0.100:55150.service: Succeeded.\n', 'Jan 07 19:31:24 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:56219).\n', 'Jan 07 19:31:24 br-automation1 dropbear[10283]: Child connection from ::ffff:10.0.0.100:56219\n', 'Jan 07 19:31:25 br-automation1 dropbear[10283]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:31:25 br-automation1 dropbear[10283]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:56219\n", 'Jan 07 19:31:28 br-automation1 dropbear[10283]: Exit (root) from <::ffff:10.0.0.100:56219>: Error reading: Connection reset by peer\n', 'Jan 07 19:31:28 br-automation1 systemd[1]: dropbear@2730-10.0.0.73:22-10.0.0.100:56219.service: Succeeded.\n', 'Jan 07 19:32:49 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:56486).\n', 'Jan 07 19:32:49 br-automation1 dropbear[10969]: Child connection from ::ffff:10.0.0.100:56486\n', 'Jan 07 19:32:49 br-automation1 dropbear[10969]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:32:49 br-automation1 dropbear[10969]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:56486\n", 'Jan 07 19:32:52 br-automation1 dropbear[10969]: Exit (root) from <::ffff:10.0.0.100:56486>: Error reading: Connection reset by peer\n', 'Jan 07 19:32:52 br-automation1 systemd[1]: dropbear@2731-10.0.0.73:22-10.0.0.100:56486.service: Succeeded.\n', 'Jan 07 19:35:07 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:56905).\n', 'Jan 07 19:35:07 br-automation1 dropbear[12077]: Child connection from ::ffff:10.0.0.100:56905\n', 'Jan 07 19:35:07 br-automation1 dropbear[12077]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:35:07 br-automation1 dropbear[12077]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:56905\n", 'Jan 07 19:35:09 br-automation1 dropbear[12077]: Exit (root) from <::ffff:10.0.0.100:56905>: Error reading: Connection reset by peer\n', 'Jan 07 19:35:09 br-automation1 systemd[1]: dropbear@2732-10.0.0.73:22-10.0.0.100:56905.service: Succeeded.\n', 'Jan 07 19:36:01 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:57082).\n', 'Jan 07 19:36:01 br-automation1 dropbear[12520]: Child connection from ::ffff:10.0.0.100:57082\n', 'Jan 07 19:36:02 br-automation1 dropbear[12520]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:36:02 br-automation1 dropbear[12520]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:57082\n", 'Jan 07 19:36:04 br-automation1 dropbear[12520]: Exit (root) from <::ffff:10.0.0.100:57082>: Error reading: Connection reset by peer\n', 'Jan 07 19:36:04 br-automation1 systemd[1]: dropbear@2733-10.0.0.73:22-10.0.0.100:57082.service: Succeeded.\n', 'Jan 07 19:37:58 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:57463).\n', 'Jan 07 19:37:58 br-automation1 dropbear[13456]: Child connection from ::ffff:10.0.0.100:57463\n', 'Jan 07 19:37:58 br-automation1 dropbear[13456]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:37:58 br-automation1 dropbear[13456]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:57463\n", 'Jan 07 19:39:40 br-automation1 dropbear[13456]: Exit (root) from <::ffff:10.0.0.100:57463>: Exited normally\n', 'Jan 07 19:39:40 br-automation1 systemd[1]: dropbear@2734-10.0.0.73:22-10.0.0.100:57463.service: Succeeded.\n', 'Jan 07 19:39:50 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:57802).\n', 'Jan 07 19:39:50 br-automation1 dropbear[14355]: Child connection from ::ffff:10.0.0.100:57802\n', 'Jan 07 19:39:50 br-automation1 dropbear[14355]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:39:50 br-automation1 dropbear[14355]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:57802\n", 'Jan 07 19:39:55 br-automation1 dropbear[14355]: Exit (root) from <::ffff:10.0.0.100:57802>: Exited normally\n', 'Jan 07 19:39:55 br-automation1 systemd[1]: dropbear@2735-10.0.0.73:22-10.0.0.100:57802.service: Succeeded.\n', 'Jan 07 19:42:37 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:58343).\n', 'Jan 07 19:42:37 br-automation1 dropbear[15699]: Child connection from ::ffff:10.0.0.100:58343\n', 'Jan 07 19:42:37 br-automation1 dropbear[15699]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:42:37 br-automation1 dropbear[15699]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:58343\n", 'Jan 07 19:42:40 br-automation1 dropbear[15699]: Exit (root) from <::ffff:10.0.0.100:58343>: Error reading: Connection reset by peer\n', 'Jan 07 19:42:40 br-automation1 systemd[1]: dropbear@2736-10.0.0.73:22-10.0.0.100:58343.service: Succeeded.\n', 'Jan 07 19:43:12 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:58456).\n', 'Jan 07 19:43:12 br-automation1 dropbear[15987]: Child connection from ::ffff:10.0.0.100:58456\n', 'Jan 07 19:43:12 br-automation1 dropbear[15987]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:43:12 br-automation1 dropbear[15987]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:58456\n", 'Jan 07 19:43:14 br-automation1 dropbear[15987]: Exit (root) from <::ffff:10.0.0.100:58456>: Error reading: Connection reset by peer\n', 'Jan 07 19:43:14 br-automation1 systemd[1]: dropbear@2737-10.0.0.73:22-10.0.0.100:58456.service: Succeeded.\n', 'Jan 07 19:44:21 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:58674).\n', 'Jan 07 19:44:21 br-automation1 dropbear[16547]: Child connection from ::ffff:10.0.0.100:58674\n', 'Jan 07 19:44:22 br-automation1 dropbear[16547]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:44:22 br-automation1 dropbear[16547]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:58674\n", 'Jan 07 19:44:24 br-automation1 dropbear[16547]: Exit (root) from <::ffff:10.0.0.100:58674>: Error reading: Connection reset by peer\n', 'Jan 07 19:44:24 br-automation1 systemd[1]: dropbear@2738-10.0.0.73:22-10.0.0.100:58674.service: Succeeded.\n', 'Jan 07 19:46:26 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:59086).\n', 'Jan 07 19:46:26 br-automation1 dropbear[17546]: Child connection from ::ffff:10.0.0.100:59086\n', 'Jan 07 19:46:26 br-automation1 dropbear[17546]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:46:26 br-automation1 dropbear[17546]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:59086\n", 'Jan 07 19:46:28 br-automation1 dropbear[17546]: Exit (root) from <::ffff:10.0.0.100:59086>: Error reading: Connection reset by peer\n', 'Jan 07 19:46:28 br-automation1 systemd[1]: dropbear@2739-10.0.0.73:22-10.0.0.100:59086.service: Succeeded.\n', 'Jan 07 19:49:16 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:59617).\n', 'Jan 07 19:49:16 br-automation1 dropbear[18917]: Child connection from ::ffff:10.0.0.100:59617\n', 'Jan 07 19:49:16 br-automation1 dropbear[18917]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:49:16 br-automation1 dropbear[18917]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:59617\n", 'Jan 07 19:49:18 br-automation1 dropbear[18917]: Exit (root) from <::ffff:10.0.0.100:59617>: Error reading: Connection reset by peer\n', 'Jan 07 19:49:18 br-automation1 systemd[1]: dropbear@2740-10.0.0.73:22-10.0.0.100:59617.service: Succeeded.\n', 'Jan 07 19:51:28 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:60018).\n', 'Jan 07 19:51:28 br-automation1 dropbear[19975]: Child connection from ::ffff:10.0.0.100:60018\n', 'Jan 07 19:51:28 br-automation1 dropbear[19975]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:51:28 br-automation1 dropbear[19975]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:60018\n", 'Jan 07 19:51:33 br-automation1 dropbear[19975]: Exit (root) from <::ffff:10.0.0.100:60018>: Error reading: Connection reset by peer\n', 'Jan 07 19:51:33 br-automation1 systemd[1]: dropbear@2741-10.0.0.73:22-10.0.0.100:60018.service: Succeeded.\n', 'Jan 07 19:51:52 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:60095).\n', 'Jan 07 19:51:52 br-automation1 dropbear[20177]: Child connection from ::ffff:10.0.0.100:60095\n', 'Jan 07 19:51:53 br-automation1 dropbear[20177]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:51:53 br-automation1 dropbear[20177]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:60095\n", 'Jan 07 19:51:55 br-automation1 dropbear[20177]: Exit (root) from <::ffff:10.0.0.100:60095>: Error reading: Connection reset by peer\n', 'Jan 07 19:51:55 br-automation1 systemd[1]: dropbear@2742-10.0.0.73:22-10.0.0.100:60095.service: Succeeded.\n', 'Jan 07 19:52:42 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:60248).\n', 'Jan 07 19:52:42 br-automation1 dropbear[20572]: Child connection from ::ffff:10.0.0.100:60248\n', 'Jan 07 19:52:42 br-automation1 dropbear[20572]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:52:42 br-automation1 dropbear[20572]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:60248\n", 'Jan 07 19:52:44 br-automation1 dropbear[20572]: Exit (root) from <::ffff:10.0.0.100:60248>: Error reading: Connection reset by peer\n', 'Jan 07 19:52:44 br-automation1 systemd[1]: dropbear@2743-10.0.0.73:22-10.0.0.100:60248.service: Succeeded.\n', 'Jan 07 19:53:09 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:60344).\n', 'Jan 07 19:53:09 br-automation1 dropbear[20796]: Child connection from ::ffff:10.0.0.100:60344\n', 'Jan 07 19:53:09 br-automation1 dropbear[20796]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:53:09 br-automation1 dropbear[20796]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:60344\n", 'Jan 07 19:53:14 br-automation1 dropbear[20796]: Exit (root) from <::ffff:10.0.0.100:60344>: Exited normally\n', 'Jan 07 19:53:14 br-automation1 systemd[1]: dropbear@2744-10.0.0.73:22-10.0.0.100:60344.service: Succeeded.\n', 'Jan 07 19:53:42 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:60449).\n', 'Jan 07 19:53:42 br-automation1 dropbear[21068]: Child connection from ::ffff:10.0.0.100:60449\n', 'Jan 07 19:53:42 br-automation1 dropbear[21068]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:53:42 br-automation1 dropbear[21068]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:60449\n", 'Jan 07 19:53:47 br-automation1 dropbear[21068]: Exit (root) from <::ffff:10.0.0.100:60449>: Exited normally\n', 'Jan 07 19:53:47 br-automation1 systemd[1]: dropbear@2745-10.0.0.73:22-10.0.0.100:60449.service: Succeeded.\n', 'Jan 07 19:54:19 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:60561).\n', 'Jan 07 19:54:19 br-automation1 dropbear[21359]: Child connection from ::ffff:10.0.0.100:60561\n', 'Jan 07 19:54:19 br-automation1 dropbear[21359]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:54:19 br-automation1 dropbear[21359]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:60561\n", 'Jan 07 19:54:24 br-automation1 dropbear[21359]: Exit (root) from <::ffff:10.0.0.100:60561>: Exited normally\n', 'Jan 07 19:54:24 br-automation1 systemd[1]: dropbear@2746-10.0.0.73:22-10.0.0.100:60561.service: Succeeded.\n', 'Jan 07 19:54:55 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:60676).\n', 'Jan 07 19:54:55 br-automation1 dropbear[21652]: Child connection from ::ffff:10.0.0.100:60676\n', 'Jan 07 19:54:55 br-automation1 dropbear[21652]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 19:54:55 br-automation1 dropbear[21652]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:60676\n", 'Jan 07 19:58:56 br-automation1 dropbear[21652]: Exit (root) from <::ffff:10.0.0.100:60676>: Exited normally\n', 'Jan 07 19:58:56 br-automation1 systemd[1]: dropbear@2747-10.0.0.73:22-10.0.0.100:60676.service: Succeeded.\n', 'Jan 07 20:00:34 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:61731).\n', 'Jan 07 20:00:34 br-automation1 dropbear[24386]: Child connection from ::ffff:10.0.0.100:61731\n', 'Jan 07 20:00:34 br-automation1 dropbear[24386]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 20:00:34 br-automation1 dropbear[24386]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:61731\n", 'Jan 07 20:05:28 br-automation1 dropbear[24386]: Exit (root) from <::ffff:10.0.0.100:61731>: Exited normally\n', 'Jan 07 20:05:28 br-automation1 systemd[1]: dropbear@2748-10.0.0.73:22-10.0.0.100:61731.service: Succeeded.\n', 'Jan 07 20:05:36 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:62689).\n', 'Jan 07 20:05:36 br-automation1 dropbear[26810]: Child connection from ::ffff:10.0.0.100:62689\n', 'Jan 07 20:05:36 br-automation1 dropbear[26810]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 20:05:36 br-automation1 dropbear[26810]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:62689\n", 'Jan 07 20:05:59 br-automation1 dropbear[26810]: Exit (root) from <::ffff:10.0.0.100:62689>: Exited normally\n', 'Jan 07 20:05:59 br-automation1 systemd[1]: dropbear@2749-10.0.0.73:22-10.0.0.100:62689.service: Succeeded.\n', 'Jan 07 20:06:07 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:62794).\n', 'Jan 07 20:06:07 br-automation1 dropbear[27065]: Child connection from ::ffff:10.0.0.100:62794\n', 'Jan 07 20:06:07 br-automation1 dropbear[27065]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 20:06:07 br-automation1 dropbear[27065]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:62794\n", 'Jan 07 20:06:11 br-automation1 dropbear[27065]: Exit (root) from <::ffff:10.0.0.100:62794>: Exited normally\n', 'Jan 07 20:06:11 br-automation1 systemd[1]: dropbear@2750-10.0.0.73:22-10.0.0.100:62794.service: Succeeded.\n', 'Jan 07 20:06:59 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:62936).\n', 'Jan 07 20:06:59 br-automation1 dropbear[27484]: Child connection from ::ffff:10.0.0.100:62936\n', 'Jan 07 20:06:59 br-automation1 dropbear[27484]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 20:06:59 br-automation1 dropbear[27484]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:62936\n", 'Jan 07 20:12:14 br-automation1 dropbear[27484]: Exit (root) from <::ffff:10.0.0.100:62936>: Exited normally\n', 'Jan 07 20:12:14 br-automation1 systemd[1]: dropbear@2751-10.0.0.73:22-10.0.0.100:62936.service: Succeeded.\n', 'Jan 07 20:12:22 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:63978).\n', 'Jan 07 20:12:22 br-automation1 dropbear[30079]: Child connection from ::ffff:10.0.0.100:63978\n', 'Jan 07 20:12:22 br-automation1 dropbear[30079]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 20:12:22 br-automation1 dropbear[30079]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:63978\n", 'Jan 07 20:12:24 br-automation1 dropbear[30079]: Exit (root) from <::ffff:10.0.0.100:63978>: Error reading: Connection reset by peer\n', 'Jan 07 20:12:24 br-automation1 systemd[1]: dropbear@2752-10.0.0.73:22-10.0.0.100:63978.service: Succeeded.\n', 'Jan 07 20:14:18 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:64362).\n', 'Jan 07 20:14:18 br-automation1 dropbear[31016]: Child connection from ::ffff:10.0.0.100:64362\n', 'Jan 07 20:14:18 br-automation1 dropbear[31016]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 20:14:18 br-automation1 dropbear[31016]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:64362\n", 'Jan 07 20:14:20 br-automation1 dropbear[31016]: Exit (root) from <::ffff:10.0.0.100:64362>: Error reading: Connection reset by peer\n', 'Jan 07 20:14:20 br-automation1 systemd[1]: dropbear@2753-10.0.0.73:22-10.0.0.100:64362.service: Succeeded.\n', 'Jan 07 20:15:02 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:64494).\n', 'Jan 07 20:15:02 br-automation1 dropbear[31371]: Child connection from ::ffff:10.0.0.100:64494\n', 'Jan 07 20:15:02 br-automation1 dropbear[31371]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 20:15:02 br-automation1 dropbear[31371]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:64494\n", 'Jan 07 20:15:54 br-automation1 dropbear[31371]: Exit (root) from <::ffff:10.0.0.100:64494>: Exited normally\n', 'Jan 07 20:15:54 br-automation1 systemd[1]: dropbear@2754-10.0.0.73:22-10.0.0.100:64494.service: Succeeded.\n', 'Jan 07 20:15:58 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:64667).\n', 'Jan 07 20:15:58 br-automation1 dropbear[31826]: Child connection from ::ffff:10.0.0.100:64667\n', 'Jan 07 20:15:58 br-automation1 dropbear[31826]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 20:15:58 br-automation1 dropbear[31826]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:64667\n", 'Jan 07 20:17:15 br-automation1 dropbear[31826]: Exit (root) from <::ffff:10.0.0.100:64667>: Exited normally\n', 'Jan 07 20:17:15 br-automation1 systemd[1]: dropbear@2755-10.0.0.73:22-10.0.0.100:64667.service: Succeeded.\n', 'Jan 07 20:17:38 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:65001).\n', 'Jan 07 20:17:38 br-automation1 dropbear[32633]: Child connection from ::ffff:10.0.0.100:65001\n', 'Jan 07 20:17:38 br-automation1 dropbear[32633]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 20:17:38 br-automation1 dropbear[32633]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:65001\n", 'Jan 07 20:21:31 br-automation1 dropbear[32633]: Exit (root) from <::ffff:10.0.0.100:65001>: Exited normally\n', 'Jan 07 20:21:31 br-automation1 systemd[1]: dropbear@2756-10.0.0.73:22-10.0.0.100:65001.service: Succeeded.\n', 'Jan 07 20:21:49 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:49407).\n', 'Jan 07 20:21:49 br-automation1 dropbear[2202]: Child connection from ::ffff:10.0.0.100:49407\n', 'Jan 07 20:21:50 br-automation1 dropbear[2202]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 20:21:50 br-automation1 dropbear[2202]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:49407\n", 'Jan 07 20:22:12 br-automation1 dropbear[2202]: Exit (root) from <::ffff:10.0.0.100:49407>: Exited normally\n', 'Jan 07 20:22:12 br-automation1 systemd[1]: dropbear@2757-10.0.0.73:22-10.0.0.100:49407.service: Succeeded.\n', 'Jan 07 20:23:16 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:49991).\n', 'Jan 07 20:23:16 br-automation1 dropbear[2907]: Child connection from ::ffff:10.0.0.100:49991\n', 'Jan 07 20:23:17 br-automation1 dropbear[2907]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 20:23:17 br-automation1 dropbear[2907]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:49991\n", 'Jan 07 20:35:25 br-automation1 dropbear[2907]: Exit (root) from <::ffff:10.0.0.100:49991>: Exited normally\n', 'Jan 07 20:35:25 br-automation1 systemd[1]: dropbear@2758-10.0.0.73:22-10.0.0.100:49991.service: Succeeded.\n', 'Jan 07 20:40:40 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:53290).\n', 'Jan 07 20:40:40 br-automation1 dropbear[11295]: Child connection from ::ffff:10.0.0.100:53290\n', 'Jan 07 20:40:41 br-automation1 dropbear[11295]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 20:40:41 br-automation1 dropbear[11295]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:53290\n", 'Jan 07 20:40:42 br-automation1 dropbear[11295]: Exit (root) from <::ffff:10.0.0.100:53290>: Error reading: Connection reset by peer\n', 'Jan 07 20:40:42 br-automation1 systemd[1]: dropbear@2759-10.0.0.73:22-10.0.0.100:53290.service: Succeeded.\n', 'Jan 07 20:41:35 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:53481).\n', 'Jan 07 20:41:35 br-automation1 dropbear[11730]: Child connection from ::ffff:10.0.0.100:53481\n', 'Jan 07 20:41:35 br-automation1 dropbear[11730]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 20:41:35 br-automation1 dropbear[11730]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:53481\n", 'Jan 07 20:41:38 br-automation1 dropbear[11730]: Exit (root) from <::ffff:10.0.0.100:53481>: Error reading: Connection reset by peer\n', 'Jan 07 20:41:38 br-automation1 systemd[1]: dropbear@2760-10.0.0.73:22-10.0.0.100:53481.service: Succeeded.\n', 'Jan 07 20:42:32 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:53651).\n', 'Jan 07 20:42:32 br-automation1 dropbear[12193]: Child connection from ::ffff:10.0.0.100:53651\n', 'Jan 07 20:42:32 br-automation1 dropbear[12193]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 20:42:32 br-automation1 dropbear[12193]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:53651\n", 'Jan 07 20:42:34 br-automation1 dropbear[12193]: Exit (root) from <::ffff:10.0.0.100:53651>: Error reading: Connection reset by peer\n', 'Jan 07 20:42:34 br-automation1 systemd[1]: dropbear@2761-10.0.0.73:22-10.0.0.100:53651.service: Succeeded.\n', 'Jan 07 20:43:14 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:53793).\n', 'Jan 07 20:43:14 br-automation1 dropbear[12537]: Child connection from ::ffff:10.0.0.100:53793\n', 'Jan 07 20:43:14 br-automation1 dropbear[12537]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 20:43:14 br-automation1 dropbear[12537]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:53793\n", 'Jan 07 20:45:36 br-automation1 dropbear[12537]: Exit (root) from <::ffff:10.0.0.100:53793>: Exited normally\n', 'Jan 07 20:45:36 br-automation1 systemd[1]: dropbear@2762-10.0.0.73:22-10.0.0.100:53793.service: Succeeded.\n', 'Jan 07 20:45:46 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:54262).\n', 'Jan 07 20:45:46 br-automation1 dropbear[13764]: Child connection from ::ffff:10.0.0.100:54262\n', 'Jan 07 20:45:47 br-automation1 dropbear[13764]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 20:45:47 br-automation1 dropbear[13764]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:54262\n", 'Jan 07 20:46:57 br-automation1 dropbear[13764]: Exit (root) from <::ffff:10.0.0.100:54262>: Exited normally\n', 'Jan 07 20:46:57 br-automation1 systemd[1]: dropbear@2763-10.0.0.73:22-10.0.0.100:54262.service: Succeeded.\n', 'Jan 07 20:47:39 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:54648).\n', 'Jan 07 20:47:39 br-automation1 dropbear[14672]: Child connection from ::ffff:10.0.0.100:54648\n', 'Jan 07 20:47:40 br-automation1 dropbear[14672]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 20:47:40 br-automation1 dropbear[14672]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:54648\n", 'Jan 07 20:51:58 br-automation1 dropbear[14672]: Exit (root) from <::ffff:10.0.0.100:54648>: Exited normally\n', 'Jan 07 20:51:58 br-automation1 systemd[1]: dropbear@2764-10.0.0.73:22-10.0.0.100:54648.service: Succeeded.\n', 'Jan 07 20:52:06 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:55472).\n', 'Jan 07 20:52:06 br-automation1 dropbear[16823]: Child connection from ::ffff:10.0.0.100:55472\n', 'Jan 07 20:52:07 br-automation1 dropbear[16823]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 20:52:07 br-automation1 dropbear[16823]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:55472\n", 'Jan 07 20:54:02 br-automation1 dropbear[16823]: Exit (root) from <::ffff:10.0.0.100:55472>: Exited normally\n', 'Jan 07 20:54:02 br-automation1 systemd[1]: dropbear@2765-10.0.0.73:22-10.0.0.100:55472.service: Succeeded.\n', 'Jan 07 20:54:07 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:55855).\n', 'Jan 07 20:54:07 br-automation1 dropbear[17799]: Child connection from ::ffff:10.0.0.100:55855\n', 'Jan 07 20:54:08 br-automation1 dropbear[17799]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 20:54:08 br-automation1 dropbear[17799]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:55855\n", 'Jan 07 21:13:39 br-automation1 dropbear[17799]: Exit (root) from <::ffff:10.0.0.100:55855>: Exited normally\n', 'Jan 07 21:13:39 br-automation1 systemd[1]: dropbear@2766-10.0.0.73:22-10.0.0.100:55855.service: Succeeded.\n', 'Jan 07 21:21:35 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:61193).\n', 'Jan 07 21:21:35 br-automation1 dropbear[31035]: Child connection from ::ffff:10.0.0.100:61193\n', 'Jan 07 21:21:36 br-automation1 dropbear[31035]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 21:21:36 br-automation1 dropbear[31035]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:61193\n", 'Jan 07 21:21:53 br-automation1 dropbear[31035]: Exit (root) from <::ffff:10.0.0.100:61193>: Exited normally\n', 'Jan 07 21:21:53 br-automation1 systemd[1]: dropbear@2767-10.0.0.73:22-10.0.0.100:61193.service: Succeeded.\n', 'Jan 07 22:39:14 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:59911).\n', 'Jan 07 22:39:14 br-automation1 dropbear[3546]: Child connection from ::ffff:10.0.0.100:59911\n', 'Jan 07 22:39:15 br-automation1 dropbear[3546]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 22:39:15 br-automation1 dropbear[3546]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:59911\n", 'Jan 07 22:44:59 br-automation1 dropbear[3546]: Exit (root) from <::ffff:10.0.0.100:59911>: Exited normally\n', 'Jan 07 22:44:59 br-automation1 systemd[1]: dropbear@2768-10.0.0.73:22-10.0.0.100:59911.service: Succeeded.\n', 'Jan 07 22:45:16 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:61040).\n', 'Jan 07 22:45:16 br-automation1 dropbear[6448]: Child connection from ::ffff:10.0.0.100:61040\n', 'Jan 07 22:45:16 br-automation1 dropbear[6448]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 22:45:16 br-automation1 dropbear[6448]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:61040\n", 'Jan 07 22:53:09 br-automation1 dropbear[6448]: Exit (root) from <::ffff:10.0.0.100:61040>: Exited normally\n', 'Jan 07 22:53:09 br-automation1 systemd[1]: dropbear@2769-10.0.0.73:22-10.0.0.100:61040.service: Succeeded.\n', 'Jan 07 23:08:26 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:65434).\n', 'Jan 07 23:08:26 br-automation1 dropbear[17709]: Child connection from ::ffff:10.0.0.100:65434\n', 'Jan 07 23:08:26 br-automation1 dropbear[17709]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 23:08:26 br-automation1 dropbear[17709]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:65434\n", 'Jan 07 23:28:14 br-automation1 dropbear[17709]: Exit (root) from <::ffff:10.0.0.100:65434>: Exited normally\n', 'Jan 07 23:28:14 br-automation1 systemd[1]: dropbear@2770-10.0.0.73:22-10.0.0.100:65434.service: Succeeded.\n', 'Jan 07 23:30:13 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:53519).\n', 'Jan 07 23:30:13 br-automation1 dropbear[28556]: Child connection from ::ffff:10.0.0.100:53519\n', 'Jan 07 23:30:14 br-automation1 dropbear[28556]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 23:30:14 br-automation1 dropbear[28556]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:53519\n", 'Jan 07 23:30:15 br-automation1 dropbear[28556]: Exit (root) from <::ffff:10.0.0.100:53519>: Error reading: Connection reset by peer\n', 'Jan 07 23:30:15 br-automation1 systemd[1]: dropbear@2771-10.0.0.73:22-10.0.0.100:53519.service: Succeeded.\n', 'Jan 07 23:31:08 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:53706).\n', 'Jan 07 23:31:08 br-automation1 dropbear[28999]: Child connection from ::ffff:10.0.0.100:53706\n', 'Jan 07 23:31:08 br-automation1 dropbear[28999]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 23:31:08 br-automation1 dropbear[28999]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:53706\n", 'Jan 07 23:31:09 br-automation1 dropbear[28999]: Exit (root) from <::ffff:10.0.0.100:53706>: Error reading: Connection reset by peer\n', 'Jan 07 23:31:09 br-automation1 systemd[1]: dropbear@2772-10.0.0.73:22-10.0.0.100:53706.service: Succeeded.\n', 'Jan 07 23:31:55 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:53854).\n', 'Jan 07 23:31:55 br-automation1 dropbear[29378]: Child connection from ::ffff:10.0.0.100:53854\n', 'Jan 07 23:31:56 br-automation1 dropbear[29378]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 23:31:56 br-automation1 dropbear[29378]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:53854\n", 'Jan 07 23:32:04 br-automation1 dropbear[29378]: Exit (root) from <::ffff:10.0.0.100:53854>: Error reading: Connection reset by peer\n', 'Jan 07 23:32:04 br-automation1 systemd[1]: dropbear@2773-10.0.0.73:22-10.0.0.100:53854.service: Succeeded.\n', 'Jan 07 23:32:37 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:53990).\n', 'Jan 07 23:32:37 br-automation1 dropbear[29711]: Child connection from ::ffff:10.0.0.100:53990\n', 'Jan 07 23:32:37 br-automation1 dropbear[29711]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 23:32:37 br-automation1 dropbear[29711]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:53990\n", 'Jan 07 23:33:23 br-automation1 dropbear[29711]: Exit (root) from <::ffff:10.0.0.100:53990>: Exited normally\n', 'Jan 07 23:33:23 br-automation1 systemd[1]: dropbear@2774-10.0.0.73:22-10.0.0.100:53990.service: Succeeded.\n', 'Jan 07 23:33:38 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:54196).\n', 'Jan 07 23:33:38 br-automation1 dropbear[30209]: Child connection from ::ffff:10.0.0.100:54196\n', 'Jan 07 23:33:38 br-automation1 dropbear[30209]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 23:33:38 br-automation1 dropbear[30209]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:54196\n", 'Jan 07 23:34:35 br-automation1 dropbear[30209]: Exit (root) from <::ffff:10.0.0.100:54196>: Exited normally\n', 'Jan 07 23:34:35 br-automation1 systemd[1]: dropbear@2775-10.0.0.73:22-10.0.0.100:54196.service: Succeeded.\n', 'Jan 07 23:34:49 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:54421).\n', 'Jan 07 23:34:49 br-automation1 dropbear[30783]: Child connection from ::ffff:10.0.0.100:54421\n', 'Jan 07 23:34:49 br-automation1 dropbear[30783]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 07 23:34:49 br-automation1 dropbear[30783]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:54421\n", 'Jan 08 00:02:59 br-automation1 dropbear[30783]: Exit (root) from <::ffff:10.0.0.100:54421>: Exited normally\n', 'Jan 08 00:02:59 br-automation1 systemd[1]: dropbear@2776-10.0.0.73:22-10.0.0.100:54421.service: Succeeded.\n', 'Jan 08 00:03:08 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:59840).\n', 'Jan 08 00:03:08 br-automation1 dropbear[11983]: Child connection from ::ffff:10.0.0.100:59840\n', 'Jan 08 00:03:08 br-automation1 dropbear[11983]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 08 00:03:08 br-automation1 dropbear[11983]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:59840\n", 'Jan 08 00:03:14 br-automation1 dropbear[11983]: Exit (root) from <::ffff:10.0.0.100:59840>: Exited normally\n', 'Jan 08 00:03:14 br-automation1 systemd[1]: dropbear@2777-10.0.0.73:22-10.0.0.100:59840.service: Succeeded.\n', 'Jan 08 00:03:38 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:59930).\n', 'Jan 08 00:03:38 br-automation1 dropbear[12224]: Child connection from ::ffff:10.0.0.100:59930\n', 'Jan 08 00:03:38 br-automation1 dropbear[12224]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 08 00:03:38 br-automation1 dropbear[12224]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:59930\n", 'Jan 08 00:03:41 br-automation1 dropbear[12224]: Exit (root) from <::ffff:10.0.0.100:59930>: Exited normally\n', 'Jan 08 00:03:41 br-automation1 systemd[1]: dropbear@2778-10.0.0.73:22-10.0.0.100:59930.service: Succeeded.\n', 'Jan 08 00:04:26 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:60087).\n', 'Jan 08 00:04:27 br-automation1 dropbear[12619]: Child connection from ::ffff:10.0.0.100:60087\n', 'Jan 08 00:04:27 br-automation1 dropbear[12619]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 08 00:04:27 br-automation1 dropbear[12619]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:60087\n", 'Jan 08 00:05:21 br-automation1 dropbear[12619]: Exit (root) from <::ffff:10.0.0.100:60087>: Exited normally\n', 'Jan 08 00:05:21 br-automation1 systemd[1]: dropbear@2779-10.0.0.73:22-10.0.0.100:60087.service: Succeeded.\n', 'Jan 08 00:05:29 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:60270).\n', 'Jan 08 00:05:29 br-automation1 dropbear[13123]: Child connection from ::ffff:10.0.0.100:60270\n', 'Jan 08 00:05:30 br-automation1 dropbear[13123]: Login attempt for nonexistent user\n', 'Jan 08 00:05:30 br-automation1 dropbear[13123]: pam_unix(dropbear:auth): check pass; user unknown\n', 'Jan 08 00:05:30 br-automation1 dropbear[13123]: pam_unix(dropbear:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=::ffff:10.0.0.100\n', 'Jan 08 00:05:32 br-automation1 dropbear[13123]: pam_authenticate() failed, rc=7, Authentication failure\n', "Jan 08 00:05:32 br-automation1 dropbear[13123]: Bad PAM password attempt for '<invalid username>' from ::ffff:10.0.0.100:60270\n", 'Jan 08 00:10:29 br-automation1 dropbear[13123]: Exit before auth from <::ffff:10.0.0.100:60270>: Timeout before auth\n', 'Jan 08 00:10:29 br-automation1 systemd[1]: dropbear@2780-10.0.0.73:22-10.0.0.100:60270.service: Succeeded.\n', 'Jan 08 00:24:13 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:63827).\n', 'Jan 08 00:24:13 br-automation1 dropbear[22147]: Child connection from ::ffff:10.0.0.100:63827\n', 'Jan 08 00:24:14 br-automation1 dropbear[22147]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 08 00:24:14 br-automation1 dropbear[22147]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:63827\n", 'Jan 08 00:24:16 br-automation1 dropbear[22147]: Exit (root) from <::ffff:10.0.0.100:63827>: Exited normally\n', 'Jan 08 00:24:16 br-automation1 systemd[1]: dropbear@2781-10.0.0.73:22-10.0.0.100:63827.service: Succeeded.\n', 'Jan 08 00:27:10 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:64411).\n', 'Jan 08 00:27:10 br-automation1 dropbear[23571]: Child connection from ::ffff:10.0.0.100:64411\n', 'Jan 08 00:27:10 br-automation1 dropbear[23571]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 08 00:27:10 br-automation1 dropbear[23571]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:64411\n", 'Jan 08 00:27:14 br-automation1 dropbear[23571]: Exit (root) from <::ffff:10.0.0.100:64411>: Exited normally\n', 'Jan 08 00:27:14 br-automation1 systemd[1]: dropbear@2782-10.0.0.73:22-10.0.0.100:64411.service: Succeeded.\n', 'Jan 08 00:28:06 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:64588).\n', 'Jan 08 00:28:06 br-automation1 dropbear[24022]: Child connection from ::ffff:10.0.0.100:64588\n', 'Jan 08 00:28:06 br-automation1 dropbear[24022]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 08 00:28:06 br-automation1 dropbear[24022]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:64588\n", 'Jan 08 00:28:09 br-automation1 dropbear[24022]: Exit (root) from <::ffff:10.0.0.100:64588>: Exited normally\n', 'Jan 08 00:28:09 br-automation1 systemd[1]: dropbear@2783-10.0.0.73:22-10.0.0.100:64588.service: Succeeded.\n', 'Jan 08 00:29:05 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:64776).\n', 'Jan 08 00:29:05 br-automation1 dropbear[24495]: Child connection from ::ffff:10.0.0.100:64776\n', 'Jan 08 00:29:05 br-automation1 dropbear[24495]: Login attempt for nonexistent user\n', 'Jan 08 00:29:05 br-automation1 dropbear[24495]: pam_unix(dropbear:auth): check pass; user unknown\n', 'Jan 08 00:29:05 br-automation1 dropbear[24495]: pam_unix(dropbear:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=::ffff:10.0.0.100\n', 'Jan 08 00:29:07 br-automation1 dropbear[24495]: pam_authenticate() failed, rc=7, Authentication failure\n', "Jan 08 00:29:07 br-automation1 dropbear[24495]: Bad PAM password attempt for '<invalid username>' from ::ffff:10.0.0.100:64776\n", 'Jan 08 00:31:08 br-automation1 dropbear[24495]: Exit before auth from <::ffff:10.0.0.100:64776>: Exited normally\n', 'Jan 08 00:31:08 br-automation1 systemd[1]: dropbear@2784-10.0.0.73:22-10.0.0.100:64776.service: Succeeded.\n', 'Jan 08 00:31:17 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:65179).\n', 'Jan 08 00:31:17 br-automation1 dropbear[25557]: Child connection from ::ffff:10.0.0.100:65179\n', 'Jan 08 00:31:17 br-automation1 dropbear[25557]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 08 00:31:17 br-automation1 dropbear[25557]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:65179\n", 'Jan 08 00:31:19 br-automation1 dropbear[25557]: Exit (root) from <::ffff:10.0.0.100:65179>: Exited normally\n', 'Jan 08 00:31:19 br-automation1 systemd[1]: dropbear@2785-10.0.0.73:22-10.0.0.100:65179.service: Succeeded.\n', 'Jan 08 00:40:15 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:50791).\n', 'Jan 08 00:40:15 br-automation1 dropbear[29885]: Child connection from ::ffff:10.0.0.100:50791\n', 'Jan 08 00:40:15 br-automation1 dropbear[29885]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 08 00:40:15 br-automation1 dropbear[29885]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:50791\n", 'Jan 08 00:40:36 br-automation1 dropbear[29885]: Exit (root) from <::ffff:10.0.0.100:50791>: Exited normally\n', 'Jan 08 00:40:36 br-automation1 systemd[1]: dropbear@2786-10.0.0.73:22-10.0.0.100:50791.service: Succeeded.\n', 'Jan 08 00:49:45 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:52582).\n', 'Jan 08 00:49:45 br-automation1 dropbear[2008]: Child connection from ::ffff:10.0.0.100:52582\n', 'Jan 08 00:49:45 br-automation1 dropbear[2008]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 08 00:49:45 br-automation1 dropbear[2008]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:52582\n", 'Jan 08 00:49:52 br-automation1 dropbear[2008]: Exit (root) from <::ffff:10.0.0.100:52582>: Exited normally\n', 'Jan 08 00:49:52 br-automation1 systemd[1]: dropbear@2787-10.0.0.73:22-10.0.0.100:52582.service: Succeeded.\n', 'Jan 08 00:52:17 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:53069).\n', 'Jan 08 00:52:17 br-automation1 dropbear[3234]: Child connection from ::ffff:10.0.0.100:53069\n', 'Jan 08 00:52:17 br-automation1 dropbear[3234]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 08 00:52:17 br-automation1 dropbear[3234]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:53069\n", 'Jan 08 00:52:33 br-automation1 dropbear[3234]: Exit (root) from <::ffff:10.0.0.100:53069>: Exited normally\n', 'Jan 08 00:52:33 br-automation1 systemd[1]: dropbear@2788-10.0.0.73:22-10.0.0.100:53069.service: Succeeded.\n', 'Jan 08 00:54:39 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:53516).\n', 'Jan 08 00:54:39 br-automation1 dropbear[4382]: Child connection from ::ffff:10.0.0.100:53516\n', 'Jan 08 00:54:40 br-automation1 dropbear[4382]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 08 00:54:40 br-automation1 dropbear[4382]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:53516\n", 'Jan 08 00:54:45 br-automation1 dropbear[4382]: Exit (root) from <::ffff:10.0.0.100:53516>: Exited normally\n', 'Jan 08 00:54:45 br-automation1 systemd[1]: dropbear@2789-10.0.0.73:22-10.0.0.100:53516.service: Succeeded.\n', 'Jan 08 00:57:01 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:53975).\n', 'Jan 08 00:57:01 br-automation1 dropbear[5519]: Child connection from ::ffff:10.0.0.100:53975\n', 'Jan 08 00:57:01 br-automation1 dropbear[5519]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 08 00:57:01 br-automation1 dropbear[5519]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:53975\n", 'Jan 08 00:57:24 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:54076).\n', 'Jan 08 00:57:24 br-automation1 dropbear[5709]: Child connection from ::ffff:10.0.0.100:54076\n', 'Jan 08 00:57:28 br-automation1 dropbear[5709]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 08 00:57:28 br-automation1 dropbear[5709]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:54076\n", 'Jan 08 01:00:17 br-automation1 dropbear[5709]: Exit (root) from <::ffff:10.0.0.100:54076>: Exited normally\n', 'Jan 08 01:00:17 br-automation1 systemd[1]: dropbear@2791-10.0.0.73:22-10.0.0.100:54076.service: Succeeded.\n', 'Jan 08 01:00:29 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:54659).\n', 'Jan 08 01:00:29 br-automation1 dropbear[7209]: Child connection from ::ffff:10.0.0.100:54659\n', 'Jan 08 01:00:32 br-automation1 dropbear[7209]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 08 01:00:32 br-automation1 dropbear[7209]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:54659\n", 'Jan 08 01:29:34 br-automation1 systemd[1]: Starting Cleanup of Temporary Directories...\n', 'Jan 08 01:29:34 br-automation1 systemd-tmpfiles[21309]: /etc/tmpfiles.d/connman_resolvconf.conf:1: Line references path below legacy directory /var/run/, updating /var/run/connman → /run/connman; please update the tmpfiles.d/ drop-in file accordingly.\n', 'Jan 08 01:29:34 br-automation1 systemd[1]: systemd-tmpfiles-clean.service: Succeeded.\n', 'Jan 08 01:29:34 br-automation1 systemd[1]: Finished Cleanup of Temporary Directories.\n', 'Jan 08 01:30:37 br-automation1 kernel: FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', 'Jan 08 01:30:39 br-automation1 systemd[1]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:30:39 br-automation1 systemd[311]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:32:07 br-automation1 kernel: FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', 'Jan 08 01:32:10 br-automation1 systemd[1]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:32:10 br-automation1 systemd[311]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:32:19 br-automation1 kernel: FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', 'Jan 08 01:32:22 br-automation1 systemd[311]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:32:22 br-automation1 systemd[1]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:32:31 br-automation1 kernel: FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', 'Jan 08 01:32:34 br-automation1 systemd[311]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:32:34 br-automation1 systemd[1]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:32:47 br-automation1 kernel: FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', 'Jan 08 01:32:50 br-automation1 systemd[1]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:32:50 br-automation1 systemd[311]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:33:43 br-automation1 kernel: FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', 'Jan 08 01:33:46 br-automation1 systemd[311]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:33:46 br-automation1 systemd[1]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:33:55 br-automation1 kernel: FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', 'Jan 08 01:33:58 br-automation1 systemd[1]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:33:58 br-automation1 systemd[311]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:34:06 br-automation1 kernel: FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', 'Jan 08 01:34:09 br-automation1 systemd[311]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:34:09 br-automation1 systemd[1]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:35:08 br-automation1 kernel: FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', 'Jan 08 01:35:11 br-automation1 systemd[311]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:35:11 br-automation1 systemd[1]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:35:25 br-automation1 kernel: FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', 'Jan 08 01:35:28 br-automation1 systemd[311]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:35:28 br-automation1 systemd[1]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:35:56 br-automation1 kernel: FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', 'Jan 08 01:35:59 br-automation1 systemd[311]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:35:59 br-automation1 systemd[1]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:36:09 br-automation1 kernel: FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', 'Jan 08 01:36:12 br-automation1 systemd[311]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:36:12 br-automation1 systemd[1]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:36:16 br-automation1 kernel: FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', 'Jan 08 01:36:19 br-automation1 systemd[1]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:36:19 br-automation1 systemd[311]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:36:32 br-automation1 kernel: FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', 'Jan 08 01:36:34 br-automation1 systemd[1]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:36:34 br-automation1 systemd[311]: var-autofs-usb1.mount: Succeeded.\n', 'Jan 08 01:58:10 br-automation1 dropbear[5519]: Exit (root) from <::ffff:10.0.0.100:53975>: Exited normally\n', 'Jan 08 01:58:10 br-automation1 systemd[1]: dropbear@2790-10.0.0.73:22-10.0.0.100:53975.service: Succeeded.\n', 'Jan 08 02:01:49 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:50139).\n', 'Jan 08 02:01:49 br-automation1 dropbear[4553]: Child connection from ::ffff:10.0.0.100:50139\n', 'Jan 08 02:01:49 br-automation1 dropbear[4553]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 08 02:01:49 br-automation1 dropbear[4553]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:50139\n", 'Jan 08 02:01:58 br-automation1 dropbear[4553]: Exit (root) from <::ffff:10.0.0.100:50139>: Exited normally\n', 'Jan 08 02:01:58 br-automation1 systemd[1]: dropbear@2793-10.0.0.73:22-10.0.0.100:50139.service: Succeeded.\n', 'Jan 08 02:02:42 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:50324).\n', 'Jan 08 02:02:42 br-automation1 dropbear[4984]: Child connection from ::ffff:10.0.0.100:50324\n', 'Jan 08 02:02:42 br-automation1 dropbear[4984]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 08 02:02:42 br-automation1 dropbear[4984]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:50324\n", 'Jan 08 02:06:40 br-automation1 dropbear[4984]: Exit (root) from <::ffff:10.0.0.100:50324>: Exited normally\n', 'Jan 08 02:06:40 br-automation1 systemd[1]: dropbear@2794-10.0.0.73:22-10.0.0.100:50324.service: Succeeded.\n', 'Jan 08 02:06:49 br-automation1 systemd[1]: Started SSH Per-Connection Server (10.0.0.100:51117).\n', 'Jan 08 02:06:49 br-automation1 dropbear[6964]: Child connection from ::ffff:10.0.0.100:51117\n', 'Jan 08 02:06:49 br-automation1 dropbear[6964]: pam_unix(dropbear:account): account root has password changed in future\n', "Jan 08 02:06:49 br-automation1 dropbear[6964]: PAM password auth succeeded for 'root' from ::ffff:10.0.0.100:51117\n"]

        list = self._linuxSSHConnector.getCmdByLines(CMD_GET_JOURNAL)

        self._addRowsToTable(list, self.tableJournalList)

    # ----------------------
    # TAB DMESG LOG OVERVIEW
    # ----------------------
    def getAndAddDmesgToTable(self):
        # list = ['[    0.000000] Booting Linux on physical CPU 0x0\n', '[    0.000000] Linux version 5.15.23 (oe-user@oe-host) (arm-poky-linux-gnueabi-gcc (GCC) 10.3.0, GNU ld (GNU Binutils) 2.36.1.20210703) #1 SMP PREEMPT Fri Feb 11 08:10:27 UTC 2022\n', '[    0.000000] CPU: ARMv7 Processor [412fc09a] revision 10 (ARMv7), cr=10c5387d\n', '[    0.000000] CPU: PIPT / VIPT nonaliasing data cache, VIPT aliasing instruction cache\n', '[    0.000000] OF: fdt: Machine model: PPC50\n', '[    0.000000] Memory policy: Data cache writealloc\n', '[    0.000000] cma: Reserved 256 MiB at 0x3f400000\n', '[    0.000000] Zone ranges:\n', '[    0.000000]   Normal   [mem 0x0000000010000000-0x000000004fffffff]\n', '[    0.000000]   HighMem  empty\n', '[    0.000000] Movable zone start for each node\n', '[    0.000000] Early memory node ranges\n', '[    0.000000]   node   0: [mem 0x0000000010000000-0x000000004fffffff]\n', '[    0.000000] Initmem setup node 0 [mem 0x0000000010000000-0x000000004fffffff]\n', '[    0.000000] percpu: Embedded 12 pages/cpu s17100 r8192 d23860 u49152\n', '[    0.000000] pcpu-alloc: s17100 r8192 d23860 u49152 alloc=12*4096\n', '[    0.000000] pcpu-alloc: [0] 0 [0] 1 \n', '[    0.000000] Built 1 zonelists, mobility grouping on.  Total pages: 259840\n', '[    0.000000] Kernel command line: b_mode=4 console=ttymxc2,115200n8 consoleblank=0 quiet root=/dev/mmcblk0p2 rootfstype=ext4 rootwait panic=2\n', '[    0.000000] Unknown kernel command line parameters "b_mode=4", will be passed to user space.\n', '[    0.000000] Dentry cache hash table entries: 131072 (order: 7, 524288 bytes, linear)\n', '[    0.000000] Inode-cache hash table entries: 65536 (order: 6, 262144 bytes, linear)\n', '[    0.000000] mem auto-init: stack:off, heap alloc:off, heap free:off\n', '[    0.000000] Memory: 761904K/1048576K available (8192K kernel code, 1049K rwdata, 2552K rodata, 1024K init, 381K bss, 24528K reserved, 262144K cma-reserved, 0K highmem)\n', '[    0.000000] SLUB: HWalign=64, Order=0-3, MinObjects=0, CPUs=2, Nodes=1\n', '[    0.000000] rcu: Preemptible hierarchical RCU implementation.\n', '[    0.000000] rcu: \tRCU event tracing is enabled.\n', '[    0.000000] rcu: \tRCU restricting CPUs from NR_CPUS=4 to nr_cpu_ids=2.\n', '[    0.000000] \tTrampoline variant of Tasks RCU enabled.\n', '[    0.000000] rcu: RCU calculated value of scheduler-enlistment delay is 10 jiffies.\n', '[    0.000000] rcu: Adjusting geometry for rcu_fanout_leaf=16, nr_cpu_ids=2\n', '[    0.000000] NR_IRQS: 16, nr_irqs: 16, preallocated irqs: 16\n', '[    0.000000] L2C-310 erratum 769419 enabled\n', '[    0.000000] L2C-310 enabling early BRESP for Cortex-A9\n', '[    0.000000] L2C-310 full line of zeros enabled for Cortex-A9\n', '[    0.000000] L2C-310 ID prefetch enabled, offset 16 lines\n', '[    0.000000] L2C-310 dynamic clock gating enabled, standby mode enabled\n', '[    0.000000] L2C-310 cache controller enabled, 16 ways, 512 kB\n', '[    0.000000] L2C-310: CACHE_ID 0x410000c8, AUX_CTRL 0x76450001\n', '[    0.000000] random: get_random_bytes called from start_kernel+0x4b4/0x66c with crng_init=0\n', '[    0.000000] Switching to timer-based delay loop, resolution 333ns\n', '[    0.000001] sched_clock: 32 bits at 3000kHz, resolution 333ns, wraps every 715827882841ns\n', '[    0.000021] clocksource: mxc_timer1: mask: 0xffffffff max_cycles: 0xffffffff, max_idle_ns: 637086815595 ns\n', '[    0.001090] Console: colour dummy device 80x30\n', '[    0.001130] Calibrating delay loop (skipped), value calculated using timer frequency.. 6.00 BogoMIPS (lpj=30000)\n', '[    0.001148] pid_max: default: 32768 minimum: 301\n', '[    0.001327] Mount-cache hash table entries: 2048 (order: 1, 8192 bytes, linear)\n', '[    0.001353] Mountpoint-cache hash table entries: 2048 (order: 1, 8192 bytes, linear)\n', '[    0.002169] CPU: Testing write buffer coherency: ok\n', '[    0.002225] CPU0: Spectre v2: using BPIALL workaround\n', '[    0.002458] CPU0: thread -1, cpu 0, socket 0, mpidr 80000000\n', '[    0.003298] Setting up static identity map for 0x10100000 - 0x10100060\n', '[    0.003471] rcu: Hierarchical SRCU implementation.\n', '[    0.003896] smp: Bringing up secondary CPUs ...\n', '[    0.004678] CPU1: thread -1, cpu 1, socket 0, mpidr 80000001\n', '[    0.004696] CPU1: Spectre v2: using BPIALL workaround\n', '[    0.004847] smp: Brought up 1 node, 2 CPUs\n', '[    0.004863] SMP: Total of 2 processors activated (12.00 BogoMIPS).\n', '[    0.004875] CPU: All CPU(s) started in SVC mode.\n', '[    0.005559] devtmpfs: initialized\n', '[    0.012607] VFP support v0.3: implementor 41 architecture 3 part 30 variant 9 rev 4\n', '[    0.012840] clocksource: jiffies: mask: 0xffffffff max_cycles: 0xffffffff, max_idle_ns: 19112604462750000 ns\n', '[    0.012864] futex hash table entries: 512 (order: 3, 32768 bytes, linear)\n', '[    0.026069] pinctrl core: initialized pinctrl subsystem\n', '[    0.027087] NET: Registered PF_NETLINK/PF_ROUTE protocol family\n', '[    0.029902] DMA: preallocated 256 KiB pool for atomic coherent allocations\n', "[    0.030955] thermal_sys: Registered thermal governor 'step_wise'\n", '[    0.031164] cpuidle: using governor ladder\n', '[    0.031205] cpuidle: using governor menu\n', '[    0.031271] CPU identified as i.MX6DL, silicon rev 1.3\n', '[    0.043617] vdd1p1: supplied by regulator-dummy\n', '[    0.044173] vdd3p0: supplied by regulator-dummy\n', '[    0.044753] vdd2p5: supplied by regulator-dummy\n', '[    0.045336] vddarm: supplied by regulator-dummy\n', '[    0.046104] vddpu: supplied by regulator-dummy\n', '[    0.046507] vddsoc: supplied by regulator-dummy\n', '[    0.054429] platform 2400000.ipu: Fixing up cyclic dependency with ldb\n', '[    0.054520] platform 2400000.ipu: Fixing up cyclic dependency with 20e0000.iomuxc-gpr:ipu1_csi1_mux\n', '[    0.054602] platform 2400000.ipu: Fixing up cyclic dependency with 20e0000.iomuxc-gpr:ipu1_csi0_mux\n', '[    0.056568] platform panel-lvds: Fixing up cyclic dependency with ldb\n', '[    0.059178] hw-breakpoint: found 5 (+1 reserved) breakpoint and 1 watchpoint registers.\n', '[    0.059197] hw-breakpoint: maximum watchpoint size is 4 bytes.\n', '[    0.060153] imx6dl-pinctrl 20e0000.pinctrl: Invalid fsl,pins or pins property in node /soc/bus@2000000/pinctrl@20e0000/imx6-brppc50/usdhc4grp\n', '[    0.060203] imx6dl-pinctrl 20e0000.pinctrl: initialized IMX pinctrl driver\n', '[    0.083789] mxs-dma 110000.dma-apbh: initialized\n', '[    0.086251] SCSI subsystem initialized\n', '[    0.086492] usbcore: registered new interface driver usbfs\n', '[    0.086550] usbcore: registered new interface driver hub\n', '[    0.086598] usbcore: registered new device driver usb\n', '[    0.086737] usb_phy_generic usbphynop1: supply vcc not found, using dummy regulator\n', '[    0.087052] usb_phy_generic usbphynop2: supply vcc not found, using dummy regulator\n', "[    0.087819] imx-i2c 21a0000.i2c: can't get pinctrl, bus recovery not supported\n", '[    0.088155] i2c i2c-0: IMX I2C adapter registered\n', "[    0.088673] imx-i2c 21a8000.i2c: can't get pinctrl, bus recovery not supported\n", '[    0.088815] i2c i2c-2: IMX I2C adapter registered\n', '[    0.088952] mc: Linux media interface: v0.10\n', '[    0.088993] videodev: Linux video capture interface: v2.00\n', '[    0.089045] pps_core: LinuxPPS API ver. 1 registered\n', '[    0.089054] pps_core: Software ver. 5.3.6 - Copyright 2005-2007 Rodolfo Giometti <giometti@linux.it>\n', '[    0.089076] PTP clock support registered\n', '[    0.090213] clocksource: Switched to clocksource mxc_timer1\n', '[    0.099543] NET: Registered PF_INET protocol family\n', '[    0.099898] IP idents hash table entries: 16384 (order: 5, 131072 bytes, linear)\n', '[    0.101086] tcp_listen_portaddr_hash hash table entries: 512 (order: 0, 6144 bytes, linear)\n', '[    0.101131] TCP established hash table entries: 8192 (order: 3, 32768 bytes, linear)\n', '[    0.101273] TCP bind hash table entries: 8192 (order: 4, 65536 bytes, linear)\n', '[    0.101415] TCP: Hash tables configured (established 8192 bind 8192)\n', '[    0.101608] UDP hash table entries: 512 (order: 2, 16384 bytes, linear)\n', '[    0.101653] UDP-Lite hash table entries: 512 (order: 2, 16384 bytes, linear)\n', '[    0.101839] NET: Registered PF_UNIX/PF_LOCAL protocol family\n', '[    0.102524] RPC: Registered named UNIX socket transport module.\n', '[    0.102539] RPC: Registered udp transport module.\n', '[    0.102546] RPC: Registered tcp transport module.\n', '[    0.102552] RPC: Registered tcp NFSv4.1 backchannel transport module.\n', '[    0.102822] armv7-pmu pmu: hw perfevents: no interrupt-affinity property, guessing.\n', '[    0.103058] hw perfevents: enabled with armv7_cortex_a9 PMU driver, 7 counters available\n', '[    0.106674] workingset: timestamp_bits=14 max_order=18 bucket_order=4\n', '[    0.112714] NFS: Registering the id_resolver key type\n', '[    0.112749] Key type id_resolver registered\n', '[    0.112758] Key type id_legacy registered\n', '[    0.112991] fuse: init (API version 7.34)\n', '[    0.113370] NET: Registered PF_ALG protocol family\n', '[    0.113444] io scheduler mq-deadline registered\n', '[    0.113455] io scheduler kyber registered\n', '[    0.120426] 2020000.serial: ttymxc0 at MMIO 0x2020000 (irq = 31, base_baud = 5000000) is a IMX\n', '[    0.121213] 21ec000.serial: ttymxc2 at MMIO 0x21ec000 (irq = 71, base_baud = 5000000) is a IMX\n', '[    0.134132] printk: console [ttymxc2] enabled\n', '[    0.139867] panel-simple panel-lcd: Specify missing connector_type\n', '[    0.145301] etnaviv etnaviv: bound 130000.gpu (ops gpu_ops)\n', '[    0.145595] etnaviv etnaviv: bound 134000.gpu (ops gpu_ops)\n', '[    0.145620] etnaviv-gpu 130000.gpu: model: GC880, revision: 5106\n', '[    0.145983] etnaviv-gpu 134000.gpu: model: GC320, revision: 5007\n', '[    0.146600] [drm] Initialized etnaviv 1.3.0 20151214 for etnaviv on minor 0\n', '[    0.148055] imx-ipuv3 2400000.ipu: IPUv3H probed\n', '[    0.158690] brd: module loaded\n', '[    0.166671] loop: module loaded\n', '[    0.169435] pps pps0: new PPS source ptp0\n', '[    0.173090] fec 2188000.ethernet eth0: registered PHC device 0\n', "[    0.173355] ehci_hcd: USB 2.0 'Enhanced' Host Controller (EHCI) Driver\n", '[    0.173424] usbcore: registered new interface driver usb-storage\n', '[    0.176296] pwm-beeper pwm-beep: supply amp not found, using dummy regulator\n', '[    0.176645] input: pwm-beeper as /devices/platform/pwm-beep/input/input0\n', '[    0.178339] snvs_rtc 20cc000.snvs:snvs-rtc-lp: registered as rtc0\n', '[    0.178379] snvs_rtc 20cc000.snvs:snvs-rtc-lp: setting system clock to 1970-01-01T00:00:00 UTC (0)\n', '[    0.178400] snvs_rtc 20cc000.snvs:snvs-rtc-lp: have a u-boot bootcounter (value: 1)\n', '[    0.178577] i2c_dev: i2c /dev entries driver\n', '[    0.182370] sdhci: Secure Digital Host Controller Interface driver\n', '[    0.182383] sdhci: Copyright(c) Pierre Ossman\n', '[    0.182389] sdhci-pltfm: SDHCI platform and OF driver helper\n', '[    0.183952] caam 2100000.crypto: Entropy delay = 3200\n', '[    0.212876] mmc0: SDHCI controller on 219c000.mmc [219c000.mmc] using ADMA\n', '[    0.244864] caam 2100000.crypto: Instantiated RNG4 SH0\n', '[    0.294005] mmc0: new DDR MMC card at address 0001\n', '[    0.294845] mmcblk0: mmc0:0001 004GA0 1.84 GiB \n', '[    0.297387]  mmcblk0: p1 p2 p3 p4\n', '[    0.298636] mmcblk0boot0: mmc0:0001 004GA0 2.00 MiB \n', '[    0.300809] mmcblk0boot1: mmc0:0001 004GA0 2.00 MiB \n', '[    0.302585] mmcblk0rpmb: mmc0:0001 004GA0 512 KiB, chardev (248:0)\n', '[    0.305628] caam 2100000.crypto: Instantiated RNG4 SH1\n', '[    0.305648] caam 2100000.crypto: device ID = 0x0a16010000000100 (Era 4)\n', '[    0.305661] caam 2100000.crypto: job rings = 2, qi = 0\n', '[    0.314520] caam algorithms registered in /proc/crypto\n', '[    0.316153] caam 2100000.crypto: registering rng-caam\n', '[    0.367654] usbcore: registered new interface driver usbhid\n', '[    0.367669] usbhid: USB HID core driver\n', '[    0.367842] i2c_hid_of 0-002c: supply vdd not found, using dummy regulator\n', '[    0.368057] i2c_hid_of 0-002c: supply vddl not found, using dummy regulator\n', '[    0.370629] NET: Registered PF_INET6 protocol family\n', '[    0.372029] Segment Routing with IPv6\n', '[    0.372062] In-situ OAM (IOAM) with IPv6\n', '[    0.372161] sit: IPv6, IPv4 and MPLS over IPv4 tunneling driver\n', '[    0.372817] NET: Registered PF_PACKET protocol family\n', '[    0.373070] 8021q: 802.1Q VLAN Support v1.8\n', '[    0.373124] Key type dns_resolver registered\n', '[    0.374869] Registering SWP/SWPB emulation handler\n', '[    0.401660] imx-drm display-subsystem: bound imx-ipuv3-crtc.2 (ops ipu_crtc_ops)\n', '[    0.401823] imx-drm display-subsystem: bound imx-ipuv3-crtc.3 (ops ipu_crtc_ops)\n', '[    0.401913] imx-drm display-subsystem: bound ldb (ops imx_ldb_ops)\n', '[    0.402394] [drm] Initialized imx-drm 1.0.0 20120507 for display-subsystem on minor 1\n', '[    0.406462] ci_hdrc ci_hdrc.0: EHCI Host Controller\n', '[    0.406503] ci_hdrc ci_hdrc.0: new USB bus registered, assigned bus number 1\n', '[    0.440272] ci_hdrc ci_hdrc.0: USB 2.0 started, EHCI 1.00\n', '[    0.441408] hub 1-0:1.0: USB hub found\n', '[    0.441489] hub 1-0:1.0: 1 port detected\n', '[    0.446628] ci_hdrc ci_hdrc.1: EHCI Host Controller\n', '[    0.446663] ci_hdrc ci_hdrc.1: new USB bus registered, assigned bus number 2\n', '[    0.470999] ci_hdrc ci_hdrc.1: USB 2.0 started, EHCI 1.00\n', '[    0.472610] hub 2-0:1.0: USB hub found\n', '[    0.472702] hub 2-0:1.0: 1 port detected\n', '[    0.478461] coda 2040000.vpu: Direct firmware load for vpu_fw_imx6d.bin failed with error -2\n', '[    0.478573] coda 2040000.vpu: Direct firmware load for vpu/vpu_fw_imx6d.bin failed with error -2\n', '[    0.478646] coda 2040000.vpu: Direct firmware load for v4l-coda960-imx6dl.bin failed with error -2\n', '[    0.478662] coda 2040000.vpu: firmware request failed\n', '[    0.481018] imx_thermal 20c8000.anatop:tempmon: Industrial CPU temperature grade - max:105C critical:100C passive:95C\n', '[    0.609560] random: fast init done\n', '[    0.731208] random: crng init done\n', '[    0.780255] usb 2-1: new high-speed USB device number 2 using ci_hdrc\n', '[    0.884600] input: hid-over-i2c FFFF:002B as /devices/platform/soc/2100000.bus/21a0000.i2c/i2c-0/0-002c/0018:FFFF:002B.0001/input/input1\n', '[    0.884818] hid-multitouch 0018:FFFF:002B.0001: input: I2C HID v1.00 Device [hid-over-i2c FFFF:002B] on 0-002c\n', '[    0.891228] EXT4-fs (mmcblk0p2): mounted filesystem with ordered data mode. Opts: (null). Quota mode: disabled.\n', '[    0.891306] VFS: Mounted root (ext4 filesystem) readonly on device 179:2.\n', '[    0.891847] devtmpfs: mounted\n', '[    0.893589] Freeing unused kernel image (initmem) memory: 1024K\n', '[    0.940903] Run /sbin/init as init process\n', '[    0.940931]   with arguments:\n', '[    0.940941]     /sbin/init\n', '[    0.940951]   with environment:\n', '[    0.940961]     HOME=/\n', '[    0.940972]     TERM=linux\n', '[    0.940981]     b_mode=4\n', '[    1.106300] systemd[1]: System time before build time, advancing clock.\n', '[    1.132072] systemd[1]: systemd 247.6+ running in system mode. (+PAM -AUDIT -SELINUX +IMA -APPARMOR -SMACK +SYSVINIT +UTMP -LIBCRYPTSETUP -GCRYPT -GNUTLS -ACL +XZ -LZ4 -ZSTD -SECCOMP +BLKID -ELFUTILS +KMOD -IDN2 -IDN -PCRE2 default-hierarchy=hybrid)\n', '[    1.133319] systemd[1]: Detected architecture arm.\n', '[    1.137309] systemd[1]: No hostname configured.\n', '[    1.137385] systemd[1]: Set hostname to <localhost>.\n', '[    1.144457] systemd[1]: Initializing machine ID from random generator.\n', '[    1.144874] systemd[1]: Installed transient /etc/machine-id file.\n', "[    1.169173] systemd[1]: Using hardware watchdog 'imx2+ watchdog', version 0, device /dev/watchdog\n", '[    1.169224] systemd[1]: Set hardware watchdog to 10s.\n', '[    1.393727] usb-storage 2-1:1.0: USB Mass Storage device detected\n', '[    1.394925] scsi host0: usb-storage 2-1:1.0\n', '[    1.850853] systemd[1]: Queued start job for default target Multi-User System.\n', '[    1.884284] systemd[1]: Created slice system-getty.slice.\n', '[    1.886162] systemd[1]: Created slice system-modprobe.slice.\n', '[    1.887795] systemd[1]: Created slice system-serial\\x2dgetty.slice.\n', '[    1.889506] systemd[1]: Created slice system-systemd\\x2dfsck.slice.\n', '[    1.891059] systemd[1]: Created slice User and Session Slice.\n', '[    1.891602] systemd[1]: Started Dispatch Password Requests to Console Directory Watch.\n', '[    1.892023] systemd[1]: Started Forward Password Requests to Wall Directory Watch.\n', '[    1.892859] systemd[1]: Reached target Host and Network Name Lookups.\n', '[    1.893007] systemd[1]: Reached target Paths.\n', '[    1.893192] systemd[1]: Reached target Remote File Systems.\n', '[    1.893350] systemd[1]: Reached target Slices.\n', '[    1.893666] systemd[1]: Reached target Swap.\n', '[    1.894376] systemd[1]: Listening on initctl Compatibility Named Pipe.\n', '[    1.906593] systemd[1]: Condition check resulted in Journal Audit Socket being skipped.\n', '[    1.907598] systemd[1]: Listening on Journal Socket (/dev/log).\n', '[    1.908547] systemd[1]: Listening on Journal Socket.\n', '[    1.910110] systemd[1]: Listening on udev Control Socket.\n', '[    1.911236] systemd[1]: Listening on udev Kernel Socket.\n', '[    1.912089] systemd[1]: Listening on User Database Manager Socket.\n', '[    1.912969] systemd[1]: Condition check resulted in Huge Pages File System being skipped.\n', '[    1.913545] systemd[1]: Condition check resulted in POSIX Message Queue File System being skipped.\n', '[    1.918557] systemd[1]: Mounting Kernel Debug File System...\n', '[    1.919734] systemd[1]: Condition check resulted in Kernel Trace File System being skipped.\n', '[    1.925916] systemd[1]: Mounting Temporary Directory (/tmp)...\n', '[    1.927278] systemd[1]: Condition check resulted in Create list of static device nodes for the current kernel being skipped.\n', '[    1.935896] systemd[1]: Starting Load Kernel Module configfs...\n', '[    1.942358] systemd[1]: Starting Load Kernel Module drm...\n', '[    1.949226] systemd[1]: Starting Load Kernel Module fuse...\n', '[    1.952058] systemd[1]: systemd-journald.service: unit configures an IP firewall, but the local system does not support BPF/cgroup firewalling.\n', '[    1.952100] systemd[1]: (This warning is only shown for the first unit using IP firewalling.)\n', '[    1.961273] systemd[1]: Starting Journal Service...\n', '[    1.966660] systemd[1]: Condition check resulted in Load Kernel Modules being skipped.\n', '[    1.975849] systemd[1]: Starting Remount Root and Kernel File Systems...\n', '[    1.991731] systemd[1]: Starting Apply Kernel Variables...\n', '[    1.997442] systemd[1]: Starting Coldplug All udev Devices...\n', '[    2.009665] systemd[1]: Mounted Kernel Debug File System.\n', '[    2.021348] systemd[1]: Mounted Temporary Directory (/tmp).\n', '[    2.023590] systemd[1]: modprobe@configfs.service: Succeeded.\n', '[    2.049234] EXT4-fs (mmcblk0p2): re-mounted. Opts: (null). Quota mode: disabled.\n', '[    2.054259] systemd[1]: Finished Load Kernel Module configfs.\n', '[    2.061529] systemd[1]: modprobe@drm.service: Succeeded.\n', '[    2.065367] systemd[1]: Finished Load Kernel Module drm.\n', '[    2.067846] systemd[1]: modprobe@fuse.service: Succeeded.\n', '[    2.081084] systemd[1]: Finished Load Kernel Module fuse.\n', '[    2.086668] systemd[1]: Finished Remount Root and Kernel File Systems.\n', '[    2.099771] systemd[1]: Finished Apply Kernel Variables.\n', '[    2.110971] systemd[1]: Mounting FUSE Control File System...\n', '[    2.130937] systemd[1]: Mounting Kernel Configuration File System...\n', '[    2.133244] systemd[1]: Condition check resulted in Rebuild Hardware Database being skipped.\n', '[    2.133751] systemd[1]: Condition check resulted in Platform Persistent Storage Archival being skipped.\n', '[    2.134216] systemd[1]: Condition check resulted in Create System Users being skipped.\n', '[    2.152921] systemd[1]: Starting Create Static Device Nodes in /dev...\n', '[    2.159930] systemd[1]: Mounted FUSE Control File System.\n', '[    2.181009] systemd[1]: Mounted Kernel Configuration File System.\n', '[    2.202085] systemd[1]: Finished Create Static Device Nodes in /dev.\n', '[    2.202727] systemd[1]: Reached target Local File Systems (Pre).\n', '[    2.207531] systemd[1]: Mounting /etc/dropbear...\n', '[    2.233825] systemd[1]: Mounting /home/ppc50-user/.cache...\n', '[    2.239296] systemd[1]: Mounting /home/ppc50-user/.dbus...\n', '[    2.261897] systemd[1]: Mounting /home/ppc50-user/.local...\n', '[    2.275144] systemd[1]: Mounting /home/ppc50-user/.pki...\n', '[    2.292210] systemd[1]: Mounting /var/volatile...\n', '[    2.310126] systemd[1]: Starting Rule-based Manager for Device Events and Files...\n', '[    2.329785] systemd[1]: Started Journal Service.\n', '[    2.445274] systemd-journald[175]: Received client request to flush runtime journal.\n', '[    2.471698] scsi 0:0:0:0: Direct-Access     Swissbit unitedCONTRAST   2000 PQ: 0 ANSI: 0 CCS\n', '[    2.474553] sd 0:0:0:0: [sda] 7843328 512-byte logical blocks: (4.02 GB/3.74 GiB)\n', '[    2.475557] sd 0:0:0:0: [sda] Write Protect is off\n', '[    2.475581] sd 0:0:0:0: [sda] Mode Sense: 43 00 00 00\n', '[    2.476406] sd 0:0:0:0: [sda] No Caching mode page found\n', '[    2.481966] sd 0:0:0:0: [sda] Assuming drive cache: write through\n', '[    2.527431]  sda: sda1\n', '[    2.530996] sd 0:0:0:0: [sda] Attached SCSI removable disk\n', '[    3.651402] imx-sdma 20ec000.sdma: loaded firmware 3.5\n', '[    4.976083] EXT4-fs (mmcblk0p1): mounted filesystem with ordered data mode. Opts: (null). Quota mode: disabled.\n', '[    4.992034] EXT4-fs (mmcblk0p3): mounted filesystem with ordered data mode. Opts: (null). Quota mode: disabled.\n', '[    4.992098] ext4 filesystem being mounted at /mnt/config supports timestamps until 2038 (0x7fffffff)\n', '[    5.042138] EXT4-fs (mmcblk0p4): mounted filesystem with ordered data mode. Opts: (null). Quota mode: disabled.\n', '[    6.099533] TI DP83867 2188000.ethernet-1:00: attached PHY driver (mii_bus:phy_addr=2188000.ethernet-1:00, irq=POLL)\n', '[   10.240734] fec 2188000.ethernet eth0: Link is Up - 1Gbps/Full - flow control rx/tx\n', '[   10.240775] IPv6: ADDRCONF(NETDEV_CHANGE): eth0: link becomes ready\n', '[   21.009509] FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', '[260303.371632] FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', '[260392.981129] FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', '[260405.285753] FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', '[260417.459303] FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', '[260433.891626] FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', '[260489.954505] FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', '[260501.602505] FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', '[260512.648379] FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', '[260574.756879] FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', '[260592.074932] FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', '[260622.143379] FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', '[260636.063378] FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', '[260642.697753] FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n', '[260658.205632] FAT-fs (sda1): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.\n']

        list = self._linuxSSHConnector.getCmdByLines(CMD_GET_DMESG)

        self._addRowsToTable(list, self.tableDmesgList)

    # ----------------------
    # GENERAL GUI METHODS
    # ----------------------

    def _copyTableSelection(self):
        cb = QApplication.clipboard()
        cb.clear(mode=0)
        # cb.setText(self.tablewMemoryOverview.selectedItems(),mode=0)
        rowList = self.tablewMemoryOverview.selectionModel().selectedIndexes()  # selectedRows(column=)

        temp = ''
        for row in rowList:
            temp += self.tablewMemoryOverview.model().data(row) + ','

        cb.setText(temp, mode=0)

    def _exportToExcel(self):

        # create pandas dataframe from each table
        df1 = self._createDataFrame(self.tablewMemoryOverview)
        df2 = self._createDataFrame(self.tableDiskUsage)
        df3 = self._createDataFrame(self.tableProcessOverview)
        df4 = self._createDataFrame(self.tableDmesgList)
        df5 = self._createDataFrame(self.tableJournalList)
        df6 = self._createDataFrame(self.tableCommand)

        # generate file name - e.g. 15_03_17_14_22_ssh.xlsx
        fileName = datetime.now().strftime('%d_%m_%H_%M_%S') + "_ssh.xlsx"

        # write data frames to excel, each table has its own tab in excel
        try:
            with pd.ExcelWriter(fileName) as writer:
                df1.to_excel(writer, sheet_name=self.tablewMemoryOverview.objectName())
                df2.to_excel(writer, sheet_name=self.tableDiskUsage.objectName())
                df3.to_excel(writer, sheet_name=self.tableProcessOverview.objectName())
                df4.to_excel(writer, sheet_name=self.tableDmesgList.objectName())
                df5.to_excel(writer, sheet_name=self.tableJournalList.objectName())
                df6.to_excel(writer, sheet_name=self.tableCommand.objectName())
        except Exception as e:
            self._connStatus = f"Export to excel failed: {e}"

        # open directory where exported file is stored
        directory = os.getcwd()
        subprocess.Popen(fr'explorer /open,{directory}')

    def _createDataFrame(self, table):

        # get size of table - columns x rows
        columnCount = table.columnCount()
        rowCount = table.rowCount()

        # prepare empty list
        listRows = []
        listHeader = []

        # get header content and create list from it
        for colIdx in range(columnCount):
            theHeaderItem = table.horizontalHeaderItem(colIdx)

            if theHeaderItem != None:
                listHeader.append(theHeaderItem.text())

        # get table content a create list of it
        for rowIdx in range(rowCount):
            listRow = []
            for colIdx in range(columnCount):
                theItem = table.item(rowIdx, colIdx)

                if theItem != None:
                    listRow.append(theItem.text())
                else:
                    listRow.append('-')

            listRows.append(listRow)

        # create pandas dataframe and return it
        return pd.DataFrame(data=listRows, columns=listHeader)

    def _updateTableWidget(self, header, rows, table):

        # table is empty? -> add all columns with labels
        if table.columnCount() == 0:
            # clean list from spaces
            tmpHeader = header[0].split(' ')
            headerItems = [value for value in tmpHeader if value != '']

            # first column is hardcoded for time span
            table.setColumnCount(len(headerItems) + 1)
            table.setColumnWidth(0, 150)
            table.setHorizontalHeaderItem(0, QTableWidgetItem('time'))

            # other columns are dynamic from received header list
            columnIdx = 1
            for headerItem in headerItems:
                table.setColumnWidth(columnIdx, 150)
                table.setHorizontalHeaderItem(columnIdx, QTableWidgetItem(headerItem))

                columnIdx += 1

        # add all rows to table
        for row in rows:

            # add new empty row
            rowCount = table.rowCount()
            table.insertRow(rowCount)

            # add current time to first column
            columnIdx = 0
            currentTime = time.strftime('%X %x')
            rowItem = QTableWidgetItem(currentTime)
            rowItem.setTextAlignment(0x0080 | 0x0004)
            table.setItem(rowCount, columnIdx, rowItem)

            # fill rest of column from received list
            columnIdx += 1
            tmp = row.split(' ')
            rowsItems = [value for value in tmp if value != '']
            # print(rowsItems)

            for item in rowsItems:
                rowItem = QTableWidgetItem(item)
                rowItem.setTextAlignment(0x0080 | 0x0004)
                table.setItem(rowCount, columnIdx, rowItem)
                columnIdx += 1

                # in column index is higher then number of columns -> break it
                if (columnIdx == table.columnCount()):
                    break

    def _clearTableWidget(self, table):
        table.setRowCount(0)

    def _removeRowFromTable(self, table):

        # if row is selected remove selected row
        rowCount = table.currentRow()

        # if row is not selected, remove last row
        if (rowCount == -1):
            rowCount = table.rowCount() - 1

        # valid index of the row? -> remove row
        if rowCount > -1:
            table.removeRow(rowCount)

    def _addRowsToTable(self, dataList, table):

        rowCount = 0
        columnIdx = 0

        if table.rowCount() > 0:
            table.setRowCount(0)

        for item in dataList:
            rowItem = QTableWidgetItem(item)
            # print(item)
            rowItem.setTextAlignment(0x0080 | 0x0001)
            table.insertRow(rowCount)
            table.setItem(rowCount, columnIdx, rowItem)
            rowCount += 1

    def _updateStatusBar(self):
        self.statusbar.showMessage(self._linuxSSHConnector.getConnectionStatus())
        self._updateGUI()

    def _showGUIMessage(self, text, msgDetails):
        msg = QMessageBox()
        msg.setWindowTitle("BnR SSH client")
        msg.setWindowFlags(Qt.WindowSystemMenuHint)
        msg.setWindowIcon(PyQt5.QtGui.QIcon('GUI/pictures/activity.svg'))
        msg.setIcon(QMessageBox.Critical)
        msg.setDetailedText(msgDetails)
        msg.setText(text)
        msg.exec_()

    def _checkHostValue(self):

        # read value from IPAddress input field and validate it
        ipAddressIsValid = ''
        try:
            ipAddressIsValid = self.validate_ip_regex(str(self.edTargetHost.text()))
        except Exception as e:
            print(f"Exception: {e}")

        # red background if address is not valid
        if ipAddressIsValid == False:
            self.edTargetHost.setStyleSheet("background-color: rgb(255, 85, 0);")
        else:
            self.edTargetHost.setStyleSheet("background-color: rgb(255, 255, 255);")

    def validate_ip_regex(self, ip_address=''):

        # split IPaddress to bytes
        bytes = ip_address.split(".")

        # first check format using reqex
        if not re.search(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", ip_address):
            # print(f"The IP address {ip_address} is not valid")
            return False

        # second check range 1-255
        try:
            for ip_byte in bytes:
                if int(ip_byte) < 0 or int(ip_byte) > 255:
                    # print(f"The IP address {ip_address} is not valid")
                    return False
        except:
            return False

        # print(f"The IP address {ip_address} is valid")

        return True

    def _setGUI(self):

        # commands list
        cmd_list = ["select command", "restart target", "get memory usage", "get disk usage", "get process overview"]

        # making it editable
        self.cboxCommand.setEditable(True)

        # adding list of items to combo box
        self.cboxCommand.addItems(cmd_list)

        # getting the line edit of combo box
        line_edit = self.cboxCommand.lineEdit()

        # setting line edit alignment to the center
        line_edit.setAlignment(Qt.AlignCenter)
        line_edit.setFont(QFont("Roboto", 12))

        # setting line edit to read only
        line_edit.setReadOnly(True)

        # workaround to be sure that is shown
        self.tablewMemoryOverview.horizontalHeader().setVisible(True)
        self.tableProcessOverview.horizontalHeader().setVisible(True)

    def _updateGUI(self):
        self.statusbar.showMessage(self._linuxSSHConnector.getConnectionStatus())

        isConnected = self._linuxSSHConnector.isConnected()

        if self._timerMemoryLogging.isActive():
            self.btnStartMemoryLogging.setText('stop timer')
            self.btnStartMemoryLogging.setStyleSheet("background-color: rgb(85, 255, 127)")
        else:
            self.btnStartMemoryLogging.setText('start timer')
            self.btnStartMemoryLogging.setStyleSheet("background-color: rgb(188, 220, 244)")

        if isConnected:
            self.btnCheckConnection.setText('disconnect')
            self.btnCheckConnection.setStyleSheet("background-color: rgb(85, 255, 127)")
            self.btnAddRecordToProcessTable.setStyleSheet("background-color: rgb(188, 220, 244)")
            self.btnDelRecordFromProcessTable.setStyleSheet("background-color: rgb(188, 220, 244)")
            self.btnClearProcessTable.setStyleSheet("background-color: rgb(188, 220, 244)")
            self.btnAddDiskUsage.setStyleSheet("background-color: rgb(188, 220, 244)")
            self.btnRemoveDiskUsage.setStyleSheet("background-color: rgb(188, 220, 244)")
            self.btnClearDiskUsage.setStyleSheet("background-color: rgb(188, 220, 244)")
            self.btnCallCmd.setStyleSheet("background-color: rgb(188, 220, 244)")
            self.cboxCommand.setStyleSheet("background-color: rgb(188, 220, 244)")
            self.btnCommandClear.setStyleSheet("background-color: rgb(188, 220, 244)")
            self.btnTakeSnapshot.setStyleSheet("background-color: rgb(188, 220, 244)")
            self.btnAddRecordToMemoryTable.setStyleSheet("background-color: rgb(188, 220, 244)")
            self.btnDelRecordFromMemoryTable.setStyleSheet("background-color: rgb(188, 220, 244)")
            self.btnClearMemoryTable.setStyleSheet("background-color: rgb(188, 220, 244)")
            self.btnLoadDmesg.setStyleSheet("background-color: rgb(188, 220, 244)")
            self.btnLoadJournal.setStyleSheet("background-color: rgb(188, 220, 244)")
            self.btnShowMemoryChart.setStyleSheet("background-color: rgb(188, 220, 244)")
        else:
            self.btnCheckConnection.setText('connect')
            self.btnCheckConnection.setStyleSheet("background-color: rgb(188, 220, 244)")
            self.btnStartMemoryLogging.setStyleSheet("background-color: rgb(232,232,232)")
            self.btnAddRecordToProcessTable.setStyleSheet("background-color: rgb(232,232,232)")
            self.btnDelRecordFromProcessTable.setStyleSheet("background-color: rgb(232,232,232)")
            self.btnClearProcessTable.setStyleSheet("background-color: rgb(232,232,232)")
            self.btnAddDiskUsage.setStyleSheet("background-color: rgb(232,232,232)")
            self.btnRemoveDiskUsage.setStyleSheet("background-color: rgb(232,232,232)")
            self.btnClearDiskUsage.setStyleSheet("background-color: rgb(232,232,232)")
            self.btnCallCmd.setStyleSheet("background-color: rgb(232,232,232)")
            self.cboxCommand.setStyleSheet("background-color: rgb(232,232,232)")
            self.btnCommandClear.setStyleSheet("background-color: rgb(232,232,232)")
            self.btnTakeSnapshot.setStyleSheet("background-color: rgb(232,232,232)")
            self.btnAddRecordToMemoryTable.setStyleSheet("background-color: rgb(232,232,232)")
            self.btnDelRecordFromMemoryTable.setStyleSheet("background-color: rgb(232,232,232)")
            self.btnClearMemoryTable.setStyleSheet("background-color: rgb(232,232,232)")
            self.btnStartMemoryLogging.setStyleSheet("background-color: rgb(232,232,232)")
            self.btnLoadDmesg.setStyleSheet("background-color: rgb(232,232,232)")
            self.btnLoadJournal.setStyleSheet("background-color: rgb(232,232,232)")
            self.btnShowMemoryChart.setStyleSheet("background-color: rgb(232,232,232)")

        self.cboxCommand.setStyleSheet("text-align:right;align-content: center;align-items: center;align-self: center;")

        self.btnAddRecordToProcessTable.setEnabled(isConnected)
        self.btnDelRecordFromProcessTable.setEnabled(isConnected)
        self.btnClearProcessTable.setEnabled(isConnected)

        self.btnAddDiskUsage.setEnabled(isConnected)
        self.btnRemoveDiskUsage.setEnabled(isConnected)
        self.btnClearDiskUsage.setEnabled(isConnected)

        self.btnCallCmd.setEnabled(isConnected)
        self.cboxCommand.setEnabled(isConnected)
        self.btnCommandClear.setEnabled(isConnected)

        self.btnTakeSnapshot.setEnabled(isConnected)

        self.btnAddRecordToMemoryTable.setEnabled(isConnected)
        self.btnDelRecordFromMemoryTable.setEnabled(isConnected)
        self.btnClearMemoryTable.setEnabled(isConnected)
        self.btnStartMemoryLogging.setEnabled(isConnected)
        self.btnShowMemoryChart.setEnabled(isConnected)

        # loggers
        self.btnLoadDmesg.setEnabled(isConnected)
        self.btnLoadJournal.setEnabled(isConnected)

    # ----------------------
    # MENU/NAVIGATION METHODS
    # ----------------------
    def _exit(self):
        sys.exit()

    def _showAbout(self):
        self._dlgAbout.exec()

    def nav_to_tab0(self):
        self.stackedWidget.setCurrentIndex(0)

    def nav_to_tab1(self):
        self.stackedWidget.setCurrentIndex(1)

    def nav_to_tab2(self):
        self.stackedWidget.setCurrentIndex(2)

    def nav_to_tab3(self):
        self.stackedWidget.setCurrentIndex(3)

    def nav_to_tab4(self):
        self.stackedWidget.setCurrentIndex(4)

    def nav_to_tab5(self):
        self.stackedWidget.setCurrentIndex(5)

    def nav_to_tab6(self):
        self.stackedWidget.setCurrentIndex(6)

    # ----------------------
    # GENERAL LOGIC METHODS
    # ----------------------
    def _connectToTarget(self):
        if self._linuxSSHConnector.isConnected():
            self._linuxSSHConnector.closeConnection()
        else:
            if self.validate_ip_regex(self.edTargetHost.text()):
                self._linuxSSHConnector.getConnection(host=self.edTargetHost.text())

                if self._linuxSSHConnector.isConnected() == False:
                    self._showGUIMessage("Client could not connect to host target",
                                         self._linuxSSHConnector.getConnectionStatus())

            else:
                self._showGUIMessage("Format of IP address is invalid!",
                                     "Use numbers in range 1-255 separated by a dot. E.g. 192.168.0.1")

        self._updateStatusBar()

    def takeSystemSnapshot(self):
        self.getAndAddDmesgToTable()
        self.getAndAddJournalToTable()
        self.getAndAddMemorySnapshotToTable()
        self.getAndAddDiskUsageTable()
        self.getAndAddProcessUsageTable()

    def _cyclicLogicHandler(self):

        loggingTime = self.spinBoxLoggingTime.value()

        # print(loggingTime)
        if self._timerMemoryLogging.isActive():
            self._timerMemoryLogging.stop()
        elif self._linuxSSHConnector.isConnected():
            self._timerMemoryLogging.timeout.connect(self._cyclicLogicActions)
            self._timerMemoryLogging.start(loggingTime * 60 * 1000)
            self.takeSystemSnapshot()

        self._updateGUI()

    def _cyclicLogicActions(self):
        self.takeSystemSnapshot()
