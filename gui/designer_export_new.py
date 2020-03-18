# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Dennis\stack\documents\work\LabelingApp\gui\designer_export_new.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(587, 317)
        self.listWidget_subjects = QtWidgets.QListWidget(Dialog)
        self.listWidget_subjects.setGeometry(QtCore.QRect(40, 60, 241, 221))
        self.listWidget_subjects.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.listWidget_subjects.setObjectName("listWidget_subjects")
        self.label_select_subjects = QtWidgets.QLabel(Dialog)
        self.label_select_subjects.setGeometry(QtCore.QRect(40, 30, 171, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_select_subjects.setFont(font)
        self.label_select_subjects.setObjectName("label_select_subjects")
        self.label_start = QtWidgets.QLabel(Dialog)
        self.label_start.setGeometry(QtCore.QRect(300, 70, 41, 16))
        self.label_start.setObjectName("label_start")
        self.label_end = QtWidgets.QLabel(Dialog)
        self.label_end.setGeometry(QtCore.QRect(300, 120, 31, 16))
        self.label_end.setObjectName("label_end")
        self.pushButton_export = QtWidgets.QPushButton(Dialog)
        self.pushButton_export.setGeometry(QtCore.QRect(460, 260, 93, 28))
        self.pushButton_export.setObjectName("pushButton_export")
        self.dateEdit_start = QtWidgets.QDateEdit(Dialog)
        self.dateEdit_start.setGeometry(QtCore.QRect(350, 70, 110, 22))
        self.dateEdit_start.setObjectName("dateEdit_start")
        self.timeEdit_start = QtWidgets.QTimeEdit(Dialog)
        self.timeEdit_start.setGeometry(QtCore.QRect(480, 70, 81, 22))
        self.timeEdit_start.setObjectName("timeEdit_start")
        self.dateEdit_end = QtWidgets.QDateEdit(Dialog)
        self.dateEdit_end.setGeometry(QtCore.QRect(350, 120, 110, 22))
        self.dateEdit_end.setObjectName("dateEdit_end")
        self.timeEdit_end = QtWidgets.QTimeEdit(Dialog)
        self.timeEdit_end.setGeometry(QtCore.QRect(480, 120, 81, 22))
        self.timeEdit_end.setObjectName("timeEdit_end")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_select_subjects.setText(_translate("Dialog", "Select subjects to export:"))
        self.label_start.setText(_translate("Dialog", "Start:"))
        self.label_end.setText(_translate("Dialog", "End:"))
        self.pushButton_export.setText(_translate("Dialog", "Export"))
