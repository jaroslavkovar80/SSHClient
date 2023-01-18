import sys
import time

import paramiko
from PyQt5 import QtWidgets
from GUI.TCMonitorGUI import TCMonitorMainWindow

host = "10.0.0.73"
port = 22
username = "root"
password = "root"

command = "free -h"

starttime = time.time()

def call_me():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username, password)

    stdin, stdout, stderr = ssh.exec_command(command)

    lines = stdout.readlines()
    print(lines)
    ssh.close()

while True:
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    ui = TCMonitorMainWindow(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())


    #print("tick:" + str(time.strftime('%X %x %Z')))
    #call_me()
    #time.sleep(60.0 - ((time.time() - starttime) % 60.0))
    #time.sleep(30)


