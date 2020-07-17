# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\denni\Documents\LabelingApp\project_new\LabelingApp\gui\designer\welcome.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.layoutWidget = QtWidgets.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(60, 40, 281, 211))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pushButton_new_project = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_new_project.setObjectName("pushButton_new_project")
        self.gridLayout_2.addWidget(self.pushButton_new_project, 1, 0, 1, 1)
        self.pushButton_load_project = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_load_project.setObjectName("pushButton_load_project")
        self.gridLayout_2.addWidget(self.pushButton_load_project, 1, 1, 1, 1)
        self.label_title = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_title.setFont(font)
        self.label_title.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.label_title.setObjectName("label_title")
        self.gridLayout_2.addWidget(self.label_title, 0, 0, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButton_new_project.setText(_translate("Dialog", "Create \n"
"new project"))
        self.pushButton_load_project.setText(_translate("Dialog", "Load existing\n"
" project"))
        self.label_title.setText(_translate("Dialog", "Labeling App"))
