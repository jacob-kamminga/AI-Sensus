# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\denni\Documents\LabelingApp\project_new\LabelingApp\gui\designer_export_new.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(510, 298)
        self.listWidget_subjects = QtWidgets.QListWidget(Dialog)
        self.listWidget_subjects.setGeometry(QtCore.QRect(40, 60, 211, 171))
        self.listWidget_subjects.setObjectName("listWidget_subjects")
        self.label_select_subjects = QtWidgets.QLabel(Dialog)
        self.label_select_subjects.setGeometry(QtCore.QRect(40, 30, 171, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_select_subjects.setFont(font)
        self.label_select_subjects.setObjectName("label_select_subjects")
        self.label_start = QtWidgets.QLabel(Dialog)
        self.label_start.setGeometry(QtCore.QRect(270, 60, 41, 16))
        self.label_start.setObjectName("label_start")
        self.label_end = QtWidgets.QLabel(Dialog)
        self.label_end.setGeometry(QtCore.QRect(270, 110, 31, 16))
        self.label_end.setObjectName("label_end")
        self.dateTimeEdit_start = QtWidgets.QDateTimeEdit(Dialog)
        self.dateTimeEdit_start.setGeometry(QtCore.QRect(350, 60, 141, 22))
        self.dateTimeEdit_start.setObjectName("dateTimeEdit_start")
        self.dateTimeEdit_end = QtWidgets.QDateTimeEdit(Dialog)
        self.dateTimeEdit_end.setGeometry(QtCore.QRect(350, 110, 141, 22))
        self.dateTimeEdit_end.setObjectName("dateTimeEdit_end")
        self.pushButton_export = QtWidgets.QPushButton(Dialog)
        self.pushButton_export.setGeometry(QtCore.QRect(370, 250, 93, 28))
        self.pushButton_export.setObjectName("pushButton_export")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_select_subjects.setText(_translate("Dialog", "Select subjects to export:"))
        self.label_start.setText(_translate("Dialog", "Start:"))
        self.label_end.setText(_translate("Dialog", "End:"))
        self.pushButton_export.setText(_translate("Dialog", "Export"))
