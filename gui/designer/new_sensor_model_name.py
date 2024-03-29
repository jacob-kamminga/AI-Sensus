# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '..\..\gui\designer\new_sensor_model_name.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not on_accepted this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(450, 350)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_title = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_title.sizePolicy().hasHeightForWidth())
        self.label_title.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_title.setFont(font)
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        self.label_title.setObjectName("label_title")
        self.verticalLayout.addWidget(self.label_title)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_model_name = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_model_name.sizePolicy().hasHeightForWidth())
        self.label_model_name.setSizePolicy(sizePolicy)
        self.label_model_name.setObjectName("label_model_name")
        self.horizontalLayout_2.addWidget(self.label_model_name)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.lineEdit_model_name = QtWidgets.QLineEdit(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_model_name.sizePolicy().hasHeightForWidth())
        self.lineEdit_model_name.setSizePolicy(sizePolicy)
        self.lineEdit_model_name.setObjectName("lineEdit_model_name")
        self.verticalLayout.addWidget(self.lineEdit_model_name)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_choose_file = QtWidgets.QLabel(Dialog)
        self.label_choose_file.setObjectName("label_choose_file")
        self.horizontalLayout_3.addWidget(self.label_choose_file)
        self.pushButton_choose_file = QtWidgets.QPushButton(Dialog)
        self.pushButton_choose_file.setObjectName("pushButton_choose_file")
        self.horizontalLayout_3.addWidget(self.pushButton_choose_file)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.label_selected_file = QtWidgets.QLabel(Dialog)
        self.label_selected_file.setText("")
        self.label_selected_file.setObjectName("label_selected_file")
        self.verticalLayout.addWidget(self.label_selected_file)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.pushButton_next = QtWidgets.QPushButton(Dialog)
        self.pushButton_next.setObjectName("pushButton_next")
        self.horizontalLayout.addWidget(self.pushButton_next)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.lineEdit_model_name, self.pushButton_choose_file)
        Dialog.setTabOrder(self.pushButton_choose_file, self.pushButton_next)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Add sensor model"))
        self.label_title.setText(_translate("Dialog", "Sensor model"))
        self.label_model_name.setText(_translate("Dialog", "Sensor model name:"))
        self.label_choose_file.setText(_translate("Dialog", "(Optional) Select a file to test the configuration:"))
        self.pushButton_choose_file.setText(_translate("Dialog", "Choose file"))
        self.pushButton_next.setText(_translate("Dialog", "Next"))
