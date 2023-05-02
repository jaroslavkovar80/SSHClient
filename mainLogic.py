import sys
from PyQt5 import QtWidgets
from GUI.TCMonitorGUI import TCMonitorMainWindow


if __name__ == "__main__":
    while True:

            app = QtWidgets.QApplication(sys.argv)
            mainWindow = QtWidgets.QMainWindow()
            ui = TCMonitorMainWindow(mainWindow)
            mainWindow.show()
            sys.exit(app.exec_())

