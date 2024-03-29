# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'new_sensor_model_comment_style.ui'
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
        self.gridLayout.addWidget(self.label_title, 0, 1, 1, 1)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFormAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.formLayout.setObjectName("formLayout")
        self.checkBox_enabled = QtWidgets.QCheckBox(Dialog)
        self.checkBox_enabled.setObjectName("checkBox_enabled")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.checkBox_enabled)
        self.lineEdit_style = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_style.setEnabled(False)
        self.lineEdit_style.setClearButtonEnabled(False)
        self.lineEdit_style.setObjectName("lineEdit_style")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit_style)
        self.gridLayout.addLayout(self.formLayout, 1, 0, 1, 3)
        self.pushButton_previous = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_previous.sizePolicy().hasHeightForWidth())
        self.pushButton_previous.setSizePolicy(sizePolicy)
        self.pushButton_previous.setObjectName("pushButton_previous")
        self.gridLayout.addWidget(self.pushButton_previous, 2, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(267, 17, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 1, 1, 1)
        self.pushButton_next = QtWidgets.QPushButton(Dialog)
        self.pushButton_next.setObjectName("pushButton_next")
        self.gridLayout.addWidget(self.pushButton_next, 2, 2, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.checkBox_enabled, self.lineEdit_style)
        Dialog.setTabOrder(self.lineEdit_style, self.pushButton_next)
        Dialog.setTabOrder(self.pushButton_next, self.pushButton_previous)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Add sensor model"))
        self.label_title.setText(_translate("Dialog", "Comment style"))
        self.checkBox_enabled.setText(_translate("Dialog", "Sensordata contains comment style"))
        self.pushButton_previous.setText(_translate("Dialog", "Previous"))
        self.pushButton_next.setText(_translate("Dialog", "Next"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
