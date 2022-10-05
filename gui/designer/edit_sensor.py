# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '..\..\gui\designer\edit_sensor.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not on_accepted this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(398, 208)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(10, 170, 381, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label_sensor_id = QtWidgets.QLabel(Dialog)
        self.label_sensor_id.setGeometry(QtCore.QRect(20, 70, 101, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_sensor_id.setFont(font)
        self.label_sensor_id.setObjectName("label_sensor_id")
        self.label_title = QtWidgets.QLabel(Dialog)
        self.label_title.setGeometry(QtCore.QRect(130, 10, 161, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_title.setFont(font)
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        self.label_title.setObjectName("label_title")
        self.label_sensor_id_val = QtWidgets.QLabel(Dialog)
        self.label_sensor_id_val.setGeometry(QtCore.QRect(130, 70, 251, 16))
        self.label_sensor_id_val.setText("")
        self.label_sensor_id_val.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.label_sensor_id_val.setObjectName("label_sensor_id_val")
        self.label_timezone = QtWidgets.QLabel(Dialog)
        self.label_timezone.setGeometry(QtCore.QRect(20, 110, 101, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_timezone.setFont(font)
        self.label_timezone.setObjectName("label_timezone")
        self.comboBox_timezone = QtWidgets.QComboBox(Dialog)
        self.comboBox_timezone.setGeometry(QtCore.QRect(132, 110, 251, 22))
        self.comboBox_timezone.setObjectName("comboBox_timezone")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Labeling App"))
        self.label_sensor_id.setText(_translate("Dialog", "Sensor ID"))
        self.label_title.setText(_translate("Dialog", "Edit sensor"))
        self.label_timezone.setText(_translate("Dialog", "Timezone"))
