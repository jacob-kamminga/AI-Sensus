# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Dennis\Documents\Work\labeling_app\project\gui\designer_subject.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(526, 350)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(170, 310, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label_select_subject = QtWidgets.QLabel(Dialog)
        self.label_select_subject.setGeometry(QtCore.QRect(20, 20, 101, 16))
        self.label_select_subject.setObjectName("label_select_subject")
        self.comboBox = QtWidgets.QComboBox(Dialog)
        self.comboBox.setGeometry(QtCore.QRect(130, 20, 211, 22))
        self.comboBox.setObjectName("comboBox")
        self.label_name = QtWidgets.QLabel(Dialog)
        self.label_name.setGeometry(QtCore.QRect(20, 70, 55, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_name.setFont(font)
        self.label_name.setObjectName("label_name")
        self.label_color = QtWidgets.QLabel(Dialog)
        self.label_color.setGeometry(QtCore.QRect(20, 100, 55, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_color.setFont(font)
        self.label_color.setObjectName("label_color")
        self.label_size = QtWidgets.QLabel(Dialog)
        self.label_size.setGeometry(QtCore.QRect(20, 130, 55, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_size.setFont(font)
        self.label_size.setObjectName("label_size")
        self.label_extra_info = QtWidgets.QLabel(Dialog)
        self.label_extra_info.setGeometry(QtCore.QRect(20, 160, 71, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_extra_info.setFont(font)
        self.label_extra_info.setObjectName("label_extra_info")
        self.plainTextEdit_extra_info = QtWidgets.QPlainTextEdit(Dialog)
        self.plainTextEdit_extra_info.setGeometry(QtCore.QRect(100, 160, 411, 131))
        self.plainTextEdit_extra_info.setReadOnly(True)
        self.plainTextEdit_extra_info.setObjectName("plainTextEdit_extra_info")
        self.label_name_val = QtWidgets.QLabel(Dialog)
        self.label_name_val.setGeometry(QtCore.QRect(100, 70, 55, 16))
        self.label_name_val.setText("")
        self.label_name_val.setObjectName("label_name_val")
        self.label_color_val = QtWidgets.QLabel(Dialog)
        self.label_color_val.setGeometry(QtCore.QRect(100, 100, 55, 16))
        self.label_color_val.setText("")
        self.label_color_val.setObjectName("label_color_val")
        self.label_size_val = QtWidgets.QLabel(Dialog)
        self.label_size_val.setGeometry(QtCore.QRect(100, 130, 55, 16))
        self.label_size_val.setText("")
        self.label_size_val.setObjectName("label_size_val")
        self.pushButton_add_subject = QtWidgets.QPushButton(Dialog)
        self.pushButton_add_subject.setGeometry(QtCore.QRect(360, 20, 151, 28))
        self.pushButton_add_subject.setObjectName("pushButton_add_subject")
        self.pushButton_remove_subject = QtWidgets.QPushButton(Dialog)
        self.pushButton_remove_subject.setGeometry(QtCore.QRect(360, 50, 151, 28))
        self.pushButton_remove_subject.setObjectName("pushButton_remove_subject")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_select_subject.setText(_translate("Dialog", "Select a subject:"))
        self.label_name.setText(_translate("Dialog", "Name:"))
        self.label_color.setText(_translate("Dialog", "Color:"))
        self.label_size.setText(_translate("Dialog", "Size:"))
        self.label_extra_info.setText(_translate("Dialog", "Extra info:"))
        self.pushButton_add_subject.setText(_translate("Dialog", "Add new subject"))
        self.pushButton_remove_subject.setText(_translate("Dialog", "Remove current subject"))
