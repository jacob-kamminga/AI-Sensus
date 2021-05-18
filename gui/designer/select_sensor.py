# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'select_sensor.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(364, 251)
        self.layoutWidget = QtWidgets.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 341, 221))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_sensor = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_sensor.setFont(font)
        self.label_sensor.setTextFormat(QtCore.Qt.AutoText)
        self.label_sensor.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter)
        self.label_sensor.setObjectName("label_sensor")
        self.verticalLayout_2.addWidget(self.label_sensor, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.comboBox_sensor = QtWidgets.QComboBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_sensor.sizePolicy().hasHeightForWidth())
        self.comboBox_sensor.setSizePolicy(sizePolicy)
        self.comboBox_sensor.setMinimumSize(QtCore.QSize(150, 0))
        self.comboBox_sensor.setEditable(False)
        self.comboBox_sensor.setObjectName("comboBox_sensor")
        self.horizontalLayout.addWidget(self.comboBox_sensor, 0, QtCore.Qt.AlignVCenter)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton_delete_sensor = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_delete_sensor.setObjectName("pushButton_delete_sensor")
        self.horizontalLayout.addWidget(self.pushButton_delete_sensor)
        self.pushButton_edit_sensor = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_edit_sensor.setObjectName("pushButton_edit_sensor")
        self.horizontalLayout.addWidget(self.pushButton_edit_sensor)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.label_new_camera = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_new_camera.sizePolicy().hasHeightForWidth())
        self.label_new_camera.setSizePolicy(sizePolicy)
        self.label_new_camera.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_new_camera.setObjectName("label_new_camera")
        self.verticalLayout_2.addWidget(self.label_new_camera)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lineEdit_new_sensor_name = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit_new_sensor_name.setInputMask("")
        self.lineEdit_new_sensor_name.setObjectName("lineEdit_new_sensor_name")
        self.horizontalLayout_2.addWidget(self.lineEdit_new_sensor_name)
        self.pushButton_new_sensor = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_new_sensor.sizePolicy().hasHeightForWidth())
        self.pushButton_new_sensor.setSizePolicy(sizePolicy)
        self.pushButton_new_sensor.setIconSize(QtCore.QSize(16, 16))
        self.pushButton_new_sensor.setShortcut("")
        self.pushButton_new_sensor.setObjectName("pushButton_new_sensor")
        self.horizontalLayout_2.addWidget(self.pushButton_new_sensor)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButton_use_sensor = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_use_sensor.setObjectName("pushButton_use_sensor")
        self.horizontalLayout_3.addWidget(self.pushButton_use_sensor)
        self.pushButton_cancel_select_sensor = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_cancel_select_sensor.setObjectName("pushButton_cancel_select_sensor")
        self.horizontalLayout_3.addWidget(self.pushButton_cancel_select_sensor)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Select Sensor ID"))
        self.label_sensor.setText(_translate("Dialog", "Select Sensor ID"))
        self.label.setText(_translate("Dialog", "Select a sensor that was used to record the selected sensordata"))
        self.pushButton_delete_sensor.setText(_translate("Dialog", "Delete"))
        self.pushButton_edit_sensor.setText(_translate("Dialog", "Edit"))
        self.label_new_camera.setText(_translate("Dialog", "Add new sensor when the sensor is not yet listed"))
        self.lineEdit_new_sensor_name.setPlaceholderText(_translate("Dialog", "New sensor name"))
        self.pushButton_new_sensor.setText(_translate("Dialog", "Add"))
        self.pushButton_use_sensor.setText(_translate("Dialog", "Save changes"))
        self.pushButton_cancel_select_sensor.setText(_translate("Dialog", "Cancel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
