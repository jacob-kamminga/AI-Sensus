# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '..\..\gui\designer_sensor.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(411, 300)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.listWidget = QtWidgets.QListWidget(Dialog)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_add_sensor = QtWidgets.QPushButton(Dialog)
        self.pushButton_add_sensor.setObjectName("pushButton_add_sensor")
        self.horizontalLayout.addWidget(self.pushButton_add_sensor)
        self.pushButton_edit_sensor = QtWidgets.QPushButton(Dialog)
        self.pushButton_edit_sensor.setObjectName("pushButton_edit_sensor")
        self.horizontalLayout.addWidget(self.pushButton_edit_sensor)
        self.pushButton_remove_sensor = QtWidgets.QPushButton(Dialog)
        self.pushButton_remove_sensor.setObjectName("pushButton_remove_sensor")
        self.horizontalLayout.addWidget(self.pushButton_remove_sensor)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButton_add_sensor.setText(_translate("Dialog", "Add"))
        self.pushButton_edit_sensor.setText(_translate("Dialog", "Edit"))
        self.pushButton_remove_sensor.setText(_translate("Dialog", "Remove"))
