# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'camera_settings.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not on_accepted this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(472, 415)
        self.layoutWidget = QtWidgets.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 22, 447, 385))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.label_camera = QtWidgets.QLabel(self.layoutWidget)

        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)

        self.label_camera.setFont(font)
        self.label_camera.setTextFormat(QtCore.Qt.AutoText)
        self.label_camera.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter)
        self.label_camera.setObjectName("label_camera")
        self.verticalLayout_2.addWidget(self.label_camera)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        self.label_2.setMinimumSize(QtCore.QSize(100, 0))
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)

        self.lineEdit_change_camera_name = QtWidgets.QLineEdit(self.layoutWidget)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_change_camera_name.sizePolicy().hasHeightForWidth())

        self.lineEdit_change_camera_name.setSizePolicy(sizePolicy)
        self.lineEdit_change_camera_name.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lineEdit_change_camera_name.setObjectName("lineEdit_change_camera_name")
        self.horizontalLayout_2.addWidget(self.lineEdit_change_camera_name)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem1)

        self.label_timezone_explanation = QtWidgets.QLabel(self.layoutWidget)
        self.label_timezone_explanation.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_timezone_explanation.setWordWrap(True)
        self.label_timezone_explanation.setObjectName("label_timezone_explanation")
        self.verticalLayout_2.addWidget(self.label_timezone_explanation)

        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")

        self.label_timezone = QtWidgets.QLabel(self.layoutWidget)
        self.label_timezone.setMinimumSize(QtCore.QSize(100, 0))

        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)

        self.label_timezone.setFont(font)
        self.label_timezone.setAlignment(QtCore.Qt.AlignCenter)
        self.label_timezone.setObjectName("label_timezone")
        self.horizontalLayout_4.addWidget(self.label_timezone)

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        self.lineEdit_timezone = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit_timezone.setObjectName("lineEdit_timezone")
        self.verticalLayout.addWidget(self.lineEdit_timezone)

        self.listWidget_timezones = QtWidgets.QListWidget(self.layoutWidget)
        self.listWidget_timezones.setObjectName("listWidget_timezones")
        self.verticalLayout.addWidget(self.listWidget_timezones)

        self.horizontalLayout_4.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem2)

        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem3)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)

        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)

        self.doubleSpinBox_manual_offset = QtWidgets.QDoubleSpinBox(self.layoutWidget)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.doubleSpinBox_manual_offset.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_manual_offset.setSizePolicy(sizePolicy)
        self.doubleSpinBox_manual_offset.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
        self.doubleSpinBox_manual_offset.setProperty("showGroupSeparator", False)
        self.doubleSpinBox_manual_offset.setMinimum(-99999.0)
        self.doubleSpinBox_manual_offset.setMaximum(99999.0)
        self.doubleSpinBox_manual_offset.setSingleStep(0.5)
        self.doubleSpinBox_manual_offset.setObjectName("doubleSpinBox_manual_offset")
        self.horizontalLayout.addWidget(self.doubleSpinBox_manual_offset)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem5)

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        self.pushButton_save_camera_settings = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_save_camera_settings.setEnabled(True)
        self.pushButton_save_camera_settings.setDefault(False)
        self.pushButton_save_camera_settings.setFlat(False)
        self.pushButton_save_camera_settings.setObjectName("pushButton_save_camera_settings")
        self.horizontalLayout_3.addWidget(self.pushButton_save_camera_settings)

        self.pushButton_cancel_camera_settings = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_cancel_camera_settings.setObjectName("pushButton_cancel_camera_settings")
        self.horizontalLayout_3.addWidget(self.pushButton_cancel_camera_settings)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_camera.setText(_translate("Dialog", "Update Camera Settings"))
        self.label_2.setText(_translate("Dialog", "Change name: "))
        self.label_timezone_explanation.setText(_translate("Dialog", "Select the timezone setting that was used on this camera. This will affect the extracted video start and end times"))
        self.label_timezone.setText(_translate("Dialog", "Timezone"))
        self.label.setText(_translate("Dialog", "[optional] Manual offset in hours"))
        self.pushButton_save_camera_settings.setText(_translate("Dialog", "Save camera settings"))
        self.pushButton_cancel_camera_settings.setText(_translate("Dialog", "Cancel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
