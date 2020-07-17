# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Dennis\stack\documents\work\LabelingApp\gui\new_subject_sensor_map.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(398, 225)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(40, 180, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label_subject = QtWidgets.QLabel(Dialog)
        self.label_subject.setGeometry(QtCore.QRect(20, 50, 55, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_subject.setFont(font)
        self.label_subject.setObjectName("label_subject")
        self.label_sensor = QtWidgets.QLabel(Dialog)
        self.label_sensor.setGeometry(QtCore.QRect(20, 80, 55, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_sensor.setFont(font)
        self.label_sensor.setObjectName("label_sensor")
        self.label_start_dt = QtWidgets.QLabel(Dialog)
        self.label_start_dt.setGeometry(QtCore.QRect(20, 110, 71, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_start_dt.setFont(font)
        self.label_start_dt.setObjectName("label_start_dt")
        self.label_end_dt = QtWidgets.QLabel(Dialog)
        self.label_end_dt.setGeometry(QtCore.QRect(20, 140, 71, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_end_dt.setFont(font)
        self.label_end_dt.setObjectName("label_end_dt")
        self.label_new_map = QtWidgets.QLabel(Dialog)
        self.label_new_map.setGeometry(QtCore.QRect(130, 10, 161, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_new_map.setFont(font)
        self.label_new_map.setObjectName("label_new_map")
        self.comboBox_subject = QtWidgets.QComboBox(Dialog)
        self.comboBox_subject.setGeometry(QtCore.QRect(120, 50, 261, 22))
        self.comboBox_subject.setObjectName("comboBox_subject")
        self.comboBox_sensor = QtWidgets.QComboBox(Dialog)
        self.comboBox_sensor.setGeometry(QtCore.QRect(120, 80, 261, 22))
        self.comboBox_sensor.setObjectName("comboBox_sensor")
        self.dateEdit_start = QtWidgets.QDateEdit(Dialog)
        self.dateEdit_start.setGeometry(QtCore.QRect(120, 110, 101, 22))
        self.dateEdit_start.setObjectName("dateEdit_start")
        self.dateEdit_end = QtWidgets.QDateEdit(Dialog)
        self.dateEdit_end.setGeometry(QtCore.QRect(120, 140, 101, 22))
        self.dateEdit_end.setObjectName("dateEdit_end")
        self.timeEdit_start = QtWidgets.QTimeEdit(Dialog)
        self.timeEdit_start.setGeometry(QtCore.QRect(240, 110, 81, 22))
        self.timeEdit_start.setObjectName("timeEdit_start")
        self.timeEdit_end = QtWidgets.QTimeEdit(Dialog)
        self.timeEdit_end.setGeometry(QtCore.QRect(240, 140, 81, 22))
        self.timeEdit_end.setObjectName("timeEdit_end")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.comboBox_subject, self.comboBox_sensor)
        Dialog.setTabOrder(self.comboBox_sensor, self.dateEdit_start)
        Dialog.setTabOrder(self.dateEdit_start, self.timeEdit_start)
        Dialog.setTabOrder(self.timeEdit_start, self.dateEdit_end)
        Dialog.setTabOrder(self.dateEdit_end, self.timeEdit_end)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Labeling App"))
        self.label_subject.setText(_translate("Dialog", "Subject"))
        self.label_sensor.setText(_translate("Dialog", "Sensor"))
        self.label_start_dt.setText(_translate("Dialog", "Start"))
        self.label_end_dt.setText(_translate("Dialog", "End"))
        self.label_new_map.setText(_translate("Dialog", "Add a new map"))
