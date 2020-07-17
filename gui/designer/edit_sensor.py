# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\denni\Documents\LabelingApp\project_new\LabelingApp\gui\edit_sensor.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(398, 160)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(10, 120, 381, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label_subject = QtWidgets.QLabel(Dialog)
        self.label_subject.setGeometry(QtCore.QRect(20, 50, 101, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_subject.setFont(font)
        self.label_subject.setObjectName("label_subject")
        self.label_sensor = QtWidgets.QLabel(Dialog)
        self.label_sensor.setGeometry(QtCore.QRect(20, 80, 101, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_sensor.setFont(font)
        self.label_sensor.setObjectName("label_sensor")
        self.label_new_map = QtWidgets.QLabel(Dialog)
        self.label_new_map.setGeometry(QtCore.QRect(130, 10, 161, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_new_map.setFont(font)
        self.label_new_map.setAlignment(QtCore.Qt.AlignCenter)
        self.label_new_map.setObjectName("label_new_map")
        self.lineEdit_new_id_val = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_new_id_val.setGeometry(QtCore.QRect(130, 80, 251, 20))
        self.lineEdit_new_id_val.setObjectName("lineEdit_new_id_val")
        self.label_old_id_val = QtWidgets.QLabel(Dialog)
        self.label_old_id_val.setGeometry(QtCore.QRect(130, 50, 251, 16))
        self.label_old_id_val.setText("")
        self.label_old_id_val.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.label_old_id_val.setObjectName("label_old_id_val")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Labeling App"))
        self.label_subject.setText(_translate("Dialog", "Old sensor ID"))
        self.label_sensor.setText(_translate("Dialog", "New sensor ID"))
        self.label_new_map.setText(_translate("Dialog", "Edit sensor"))
