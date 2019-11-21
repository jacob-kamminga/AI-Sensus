# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Dennis\Documents\Work\labeling_app\project\gui\designer_camera_settings.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(428, 300)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(20, 260, 391, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.layoutWidget = QtWidgets.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 22, 401, 231))
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
        self.comboBox_cameras = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox_cameras.setObjectName("comboBox_cameras")
        self.verticalLayout_2.addWidget(self.comboBox_cameras)
        self.label_new_camera = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_new_camera.sizePolicy().hasHeightForWidth())
        self.label_new_camera.setSizePolicy(sizePolicy)
        self.label_new_camera.setObjectName("label_new_camera")
        self.verticalLayout_2.addWidget(self.label_new_camera)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lineEdit_new_camera = QtWidgets.QLineEdit(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_new_camera.sizePolicy().hasHeightForWidth())
        self.lineEdit_new_camera.setSizePolicy(sizePolicy)
        self.lineEdit_new_camera.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lineEdit_new_camera.setObjectName("lineEdit_new_camera")
        self.horizontalLayout_2.addWidget(self.lineEdit_new_camera)
        self.pushButton_add = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_add.sizePolicy().hasHeightForWidth())
        self.pushButton_add.setSizePolicy(sizePolicy)
        self.pushButton_add.setIconSize(QtCore.QSize(16, 16))
        self.pushButton_add.setShortcut("")
        self.pushButton_add.setObjectName("pushButton_add")
        self.horizontalLayout_2.addWidget(self.pushButton_add)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.label = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.comboBox = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox.setObjectName("comboBox")
        self.verticalLayout_2.addWidget(self.comboBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_camera.setText(_translate("Dialog", "Camera"))
        self.label_new_camera.setText(_translate("Dialog", "Add new camera:"))
        self.pushButton_add.setText(_translate("Dialog", "Add"))
        self.label.setText(_translate("Dialog", "Timezone"))
