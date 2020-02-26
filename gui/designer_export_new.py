# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Dennis\Documents\Work\labeling_app\project\gui\designer_export_new.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(510, 298)
        self.listWidget = QtWidgets.QListWidget(Dialog)
        self.listWidget.setGeometry(QtCore.QRect(40, 60, 211, 171))
        self.listWidget.setObjectName("listWidget")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(40, 30, 171, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(270, 60, 41, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(270, 110, 31, 16))
        self.label_3.setObjectName("label_3")
        self.dateTimeEdit = QtWidgets.QDateTimeEdit(Dialog)
        self.dateTimeEdit.setGeometry(QtCore.QRect(350, 60, 141, 22))
        self.dateTimeEdit.setObjectName("dateTimeEdit")
        self.dateTimeEdit_2 = QtWidgets.QDateTimeEdit(Dialog)
        self.dateTimeEdit_2.setGeometry(QtCore.QRect(350, 110, 141, 22))
        self.dateTimeEdit_2.setObjectName("dateTimeEdit_2")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(370, 250, 93, 28))
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Select subjects to export:"))
        self.label_2.setText(_translate("Dialog", "Start:"))
        self.label_3.setText(_translate("Dialog", "End:"))
        self.pushButton.setText(_translate("Dialog", "Export"))
