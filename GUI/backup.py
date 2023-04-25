def smaz_createGraph(self, graphTitle, seriesTitle, xTitle, yTitle):
    # Create Line series to present data in line chart

    # self._lineserie1 = QLineSeries()
    self._lineserie1.setName(seriesTitle)
    self._lineserie1.append(QDateTime.currentDateTime().toSecsSinceEpoch(), 0)

    self._lineserie[0].setName('TEST')
    self._lineserie[0].append(QDateTime.currentDateTime().toSecsSinceEpoch(), 0)

    self._lineserie2 = QLineSeries()
    self._lineserie2.setName(seriesTitle)
    self._lineserie2.append(QDateTime.currentDateTime().toSecsSinceEpoch(), 0)

    # create and configure Chart and assign series to it
    self.chart = QChart()
    self.chart.addSeries(self._lineserie1)
    self.chart.addSeries(self._lineserie2)
    self.chart.addSeries(self._lineserie[0])
    self.chart.setTitle(graphTitle)
    self.chart.setAnimationOptions(QChart.AllAnimations)
    self.chart.setAnimationDuration(1000)
    # self.chart.setTheme(QChart.ChartThemeBlueCerulean)
    self.chart.legend().setVisible(True)
    self.chart.legend().setAlignment(Qt.AlignBottom)

    # create axis X - type QDateTimeAxis()
    self._axis_x = QDateTimeAxis()
    self.chart.addAxis(self._axis_x, Qt.AlignBottom)
    self._lineserie1.attachAxis(self._axis_x)
    self._lineserie2.attachAxis(self._axis_x)
    self._axis_x.setTitleText(xTitle)
    self._axis_x.setTitleVisible(True)
    self._axis_x.setTickCount(5)
    self._axis_x.setLabelsAngle(0)
    self._axis_x.setFormat("h:mm:ss")
    # self._axis_x.setMin(QDateTime.currentDateTime())
    # self._axis_x.setMax(QDateTime.currentDateTime().addSecs(120))

    dt = QDateTime.fromMSecsSinceEpoch(1682082585868)

    self._axis_x.setMin(dt)
    self._axis_x.setMax(dt.addSecs(1))

    # create axis Y - type QDateTimeAxis()
    self._axis_y = QValueAxis()
    self.chart.addAxis(self._axis_y, Qt.AlignLeft)
    self._lineserie1.attachAxis(self._axis_y)
    self._lineserie2.attachAxis(self._axis_y)

    self._axis_y.setRange(0, 120)
    self._axis_y.setTitleText(yTitle)
    self._axis_y.setTitleVisible(True)

    self._chart_view = QChartView(self.chart)
    self._chart_view.setRenderHint(QPainter.Antialiasing)

    self.setCentralWidget(self._chart_view)


def smaz_addPoint(self, x_time=0, y_value=0):
    # record current date and time
    dt = QDateTime.currentDateTime()

    print(x_time)
    # add time and its value to series
    self._lineserie1.append(x_time.toMSecsSinceEpoch(), y_value)
    self._lineserie2.append(x_time.toMSecsSinceEpoch(), 10)

    # recalculate max and min value for X/Y axes
    t_min, t_max = min(x_time, self._axis_x.min()), max(x_time, (self._axis_x.max()))
    y_min, y_max = min(y_value - 10, self._axis_y.min()), max(y_value + 10, self._axis_y.max())

    print(t_min)
    print(t_max)
    self._axis_x.setRange(t_min, t_max)
    self._axis_y.setRange(y_min, y_max)


def smaz_addPoint2(self, x_time=0, y_value=0):
    # record current date and time
    x_time = QDateTime.currentDateTime()

    print(x_time)
    # add time and its value to series
    self._lineserie[0].append(x_time.toMSecsSinceEpoch(), y_value + 10)
    print(len(self._lineserie))
    self._lineserie[1].append(x_time.toMSecsSinceEpoch(), y_value)
    # self._lineserie[1].append(x_time.toMSecsSinceEpoch(), 10)

    # recalculate max and min value for X/Y axes
    t_min, t_max = min(x_time, self._axis_x.min()), max(x_time, (self._axis_x.max()))
    y_min, y_max = min(y_value - 10, self._axis_y.min()), max(y_value + 10, self._axis_y.max())

    print(t_min)
    print(t_max)
    self._axis_x.setRange(t_min, t_max)
    self._axis_y.setRange(y_min, y_max)


class MyChartBackup(QMainWindow):

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

class MyChart(QMainWindow):

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
class TestChart(QMainWindow):
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