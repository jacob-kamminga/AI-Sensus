# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\denni\Documents\LabelingApp\project_new\LabelingApp\gui\designer\sensor_model_list.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(439, 386)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(40, 320, 361, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setGeometry(QtCore.QRect(40, 20, 361, 271))
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.listWidget_models = QtWidgets.QListWidget(self.widget)
        self.listWidget_models.setObjectName("listWidget_models")
        self.gridLayout.addWidget(self.listWidget_models, 1, 0, 1, 2)
        self.pushButton_new = QtWidgets.QPushButton(self.widget)
        self.pushButton_new.setObjectName("pushButton_new")
        self.gridLayout.addWidget(self.pushButton_new, 2, 0, 1, 1)
        self.pushButton_settings = QtWidgets.QPushButton(self.widget)
        self.pushButton_settings.setObjectName("pushButton_settings")
        self.gridLayout.addWidget(self.pushButton_settings, 2, 1, 1, 1)
        self.label_title = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_title.setFont(font)
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        self.label_title.setObjectName("label_title")
        self.gridLayout.addWidget(self.label_title, 0, 0, 1, 2)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Sensor models"))
        self.pushButton_new.setText(_translate("Dialog", "Create new"))
        self.pushButton_settings.setText(_translate("Dialog", "View settings"))
        self.label_title.setText(_translate("Dialog", "Sensor models"))
