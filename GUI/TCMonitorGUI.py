from GUI.qt5TCMonitorMainWindow import Ui_MainWindow

class TCMonitorMainWindow(Ui_MainWindow):
    def __init__(self, window):

        self.setupUi(window)

        self.tabWidget.setStyleSheet("QTabWidget:title {background-color: red;}")

        self.btnTab1.clicked.connect(self.nav_to_tab0)
        self.btnTab2.clicked.connect(self.nav_to_tab1)
        self.btnTab3.clicked.connect(self.nav_to_tab2)
        self.btnTab4.clicked.connect(self.nav_to_tab3)



    def nav_to_tab0(self):
        self.tabWidget.setCurrentIndex(0)

    def nav_to_tab1(self):
        self.tabWidget.setCurrentIndex(1)

    def nav_to_tab2(self):
        self.tabWidget.setCurrentIndex(2)

    def nav_to_tab3(self):
        self.tabWidget.setCurrentIndex(3)