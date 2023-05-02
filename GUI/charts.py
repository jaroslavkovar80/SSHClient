from PyQt5.QtWidgets import (QApplication, QTableWidget, QTableWidgetItem, QDialog, QMessageBox, QMainWindow)
from PyQt5.QtChart import (QBarCategoryAxis, QBarSeries, QBarSet, QChart, QChartView, QLineSeries, QValueAxis,
                           QDateTimeAxis)
from PyQt5.QtCore import  QDateTime
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QFont


class ChartWithTimeAxis(QMainWindow):

    """
    CLASS FOR window with CHART
     - X axis is represented by time
     - Y axis is represented by int value
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

class ChartWithValueAxis(QMainWindow):

    _x = 1
    _y = 15


    def __init__(self, xTitle, yTitle):
        super().__init__()

        self.lineserie = QLineSeries()
        self.lineserie.setName("trend")

        self.lineserie.append(QPoint(0, 4))

        self.chart = QChart()
        self.chart.addSeries(self.lineserie)
        self.chart.setTitle("Memory overview")

        self._axis_x = QValueAxis()
        self.chart.addAxis(self._axis_x, Qt.AlignBottom)
        self.lineserie.attachAxis(self._axis_x)
        self._axis_x.setRange(0, 10)
        self._axis_x.setTitleText(xTitle)
        self._axis_x.setTitleVisible(True)

        self._axis_y = QValueAxis()
        self.chart.addAxis(self._axis_y, Qt.AlignLeft)
        self.lineserie.attachAxis(self._axis_y)
        self._axis_y.setRange(0, 120)
        self._axis_y.setTitleText(yTitle)
        self._axis_y.setTitleVisible(True)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)

        self._chart_view = QChartView(self.chart)
        self._chart_view.setRenderHint(QPainter.Antialiasing)

        self.setCentralWidget(self._chart_view)

    def addPoint(self):

        self.lineserie.append(QPoint(self._x, self._y))
        self._x = self._x + 1
        self._y = self._y + self._x + 3

        if( self._axis_x.max() <= self._x):
            self._axis_x.setMax(self._x)

class ChartSample(QMainWindow):
    def __init__(self):
        super().__init__()

        self.set0 = QBarSet("Jane")
        self.set1 = QBarSet("John")
        self.set2 = QBarSet("Axel")
        self.set3 = QBarSet("Mary")
        self.set4 = QBarSet("Sam")

        self.set0.append([1, 2, 3, 4, 5, 6])
        self.set1.append([5, 0, 0, 4, 0, 7])
        self.set2.append([3, 5, 8, 13, 8, 5])
        self.set3.append([5, 6, 7, 3, 4, 5])
        self.set4.append([9, 7, 5, 3, 1, 2])

        self._bar_series = QBarSeries()
        self._bar_series.append(self.set0)
        self._bar_series.append(self.set1)
        self._bar_series.append(self.set2)
        self._bar_series.append(self.set3)
        self._bar_series.append(self.set4)

        self.lineserie = QLineSeries()
        self.lineserie.setName("trend")
        self.lineserie.append(QPoint(0, 4))
        self.lineserie.append(QPoint(1, 15))
        self.lineserie.append(QPoint(2, 20))
        self.lineserie.append(QPoint(3, 4))
        self.lineserie.append(QPoint(4, 12))
        self.lineserie.append(QPoint(5, 17))

        self.chart = QChart()
        self.chart.addSeries(self._bar_series)
        self.chart.addSeries(self.lineserie)
        self.chart.setTitle("Line and barchart example")

        self.categories = ["Jan", "Feb", "Mar", "Apr", "May", "Jun2"]
        self._axis_x = QBarCategoryAxis()
        self._axis_x.append(self.categories)
        self.chart.addAxis(self._axis_x, Qt.AlignBottom)
        self.lineserie.attachAxis(self._axis_x)
        self._bar_series.attachAxis(self._axis_x)
        self._axis_x.setRange("Jan", "Jun")
        self._axis_x.setTitleText("x axis")
        self._axis_x.setTitleVisible(True)

        self._axis_y = QValueAxis()
        self.chart.addAxis(self._axis_y, Qt.AlignLeft)
        self.lineserie.attachAxis(self._axis_y)
        self._bar_series.attachAxis(self._axis_y)
        self._axis_y.setRange(0, 20)
        self._axis_y.setTitleText("y axis")
        self._axis_y.setTitleVisible(True)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)

        self._chart_view = QChartView(self.chart)
        self._chart_view.setRenderHint(QPainter.Antialiasing)

        self.setCentralWidget(self._chart_view)