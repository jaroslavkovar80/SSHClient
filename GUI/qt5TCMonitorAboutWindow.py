# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt5TCMonitorAboutWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.NonModal)
        Dialog.setEnabled(True)
        Dialog.resize(413, 391)
        Dialog.setStyleSheet("#Dialog{\n"
"    border-style:none;\n"
"}\n"
"#frame{\n"
"    background-color:#16191d;\n"
"    border-style:none;\n"
"}\n"
"")
        Dialog.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.btnClose = QtWidgets.QPushButton(self.frame)
        self.btnClose.setGeometry(QtCore.QRect(200, 160, 75, 23))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/test/pictures/activity.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnClose.setIcon(icon)
        self.btnClose.setIconSize(QtCore.QSize(24, 24))
        self.btnClose.setObjectName("btnClose")
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.btnClose.clicked.connect(Dialog.close)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "About"))
        self.btnClose.setText(_translate("Dialog", "PushButton"))
import GUI.test
