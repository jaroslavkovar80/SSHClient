import sys
from PyQt5 import QtWidgets
from GUI.SSHClientGUI import MainWindow


if __name__ == "__main__":
    while True:

        app = QtWidgets.QApplication(sys.argv)
        mainWindow = QtWidgets.QMainWindow()
        ui = MainWindow(mainWindow)
        mainWindow.show()
        sys.exit(app.exec_())

