# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\denni\Documents\LabelingApp\project_new\LabelingApp\gui\designer\new_sensor_model_comment_style.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(450, 350)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_style = QtWidgets.QLabel(Dialog)
        self.label_style.setObjectName("label_style")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_style)
        self.lineEdit_style = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_style.setObjectName("lineEdit_style")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_style)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.formLayout.setItem(2, QtWidgets.QFormLayout.FieldRole, spacerItem)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.formLayout.setItem(0, QtWidgets.QFormLayout.FieldRole, spacerItem1)
        self.gridLayout.addLayout(self.formLayout, 2, 0, 1, 3)
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
        self.gridLayout.addWidget(self.label_title, 0, 0, 1, 3)
        spacerItem2 = QtWidgets.QSpacerItem(267, 17, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 3, 1, 1, 1)
        self.pushButton_previous = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_previous.sizePolicy().hasHeightForWidth())
        self.pushButton_previous.setSizePolicy(sizePolicy)
        self.pushButton_previous.setObjectName("pushButton_previous")
        self.gridLayout.addWidget(self.pushButton_previous, 3, 0, 1, 1)
        self.pushButton_next = QtWidgets.QPushButton(Dialog)
        self.pushButton_next.setObjectName("pushButton_next")
        self.gridLayout.addWidget(self.pushButton_next, 3, 2, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Add sensor model"))
        self.label_style.setText(_translate("Dialog", "Style"))
        self.label_title.setText(_translate("Dialog", "Comment style"))
        self.pushButton_previous.setText(_translate("Dialog", "Previous"))
        self.pushButton_next.setText(_translate("Dialog", "Next"))
