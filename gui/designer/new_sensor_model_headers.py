# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\denni\Documents\LabelingApp\project_new\LabelingApp\gui\designer\new_sensor_model_headers.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(450, 350)
        self.gridLayout_2 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pushButton_next = QtWidgets.QPushButton(Dialog)
        self.pushButton_next.setObjectName("pushButton_next")
        self.gridLayout_2.addWidget(self.pushButton_next, 2, 2, 1, 1)
        self.pushButton_previous = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_previous.sizePolicy().hasHeightForWidth())
        self.pushButton_previous.setSizePolicy(sizePolicy)
        self.pushButton_previous.setObjectName("pushButton_previous")
        self.gridLayout_2.addWidget(self.pushButton_previous, 2, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 2, 1, 1, 1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_row = QtWidgets.QLabel(Dialog)
        self.label_row.setObjectName("label_row")
        self.gridLayout.addWidget(self.label_row, 2, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 0, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 3, 1, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.gridLayout.addLayout(self.horizontalLayout_2, 4, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.spinBox_row = QtWidgets.QSpinBox(Dialog)
        self.spinBox_row.setObjectName("spinBox_row")
        self.horizontalLayout.addWidget(self.spinBox_row)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 1, 1, 1)
        self.gridLayout.setColumnMinimumWidth(0, 30)
        self.gridLayout_2.addLayout(self.gridLayout, 1, 0, 1, 3)
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
        self.gridLayout_2.addWidget(self.label_title, 0, 0, 1, 3)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Add sensor model"))
        self.pushButton_next.setText(_translate("Dialog", "Next"))
        self.pushButton_previous.setText(_translate("Dialog", "Previous"))
        self.label_row.setText(_translate("Dialog", "Row"))
        self.label_title.setText(_translate("Dialog", "Headers"))
