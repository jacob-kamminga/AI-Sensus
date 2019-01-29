# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer_labelspecs.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_LabelSpecs(object):
    def setupUi(self, LabelSpecs):
        LabelSpecs.setObjectName("LabelSpecs")
        LabelSpecs.resize(400, 300)
        self.buttonBox = QtWidgets.QDialogButtonBox(LabelSpecs)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayoutWidget_3 = QtWidgets.QWidget(LabelSpecs)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(30, 90, 351, 111))
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.label_3.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_4.addWidget(self.label_3)
        self.comboBox_labels = QtWidgets.QComboBox(self.verticalLayoutWidget_3)
        self.comboBox_labels.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.comboBox_labels.setObjectName("comboBox_labels")
        self.verticalLayout_4.addWidget(self.comboBox_labels)
        self.verticalLayout_3.addLayout(self.verticalLayout_4)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.label.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.doubleSpinBox_start = QtWidgets.QDoubleSpinBox(self.verticalLayoutWidget_3)
        self.doubleSpinBox_start.setMaximum(99999.99)
        self.doubleSpinBox_start.setObjectName("doubleSpinBox_start")
        self.verticalLayout.addWidget(self.doubleSpinBox_start)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.label_2.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.doubleSpinBox_end = QtWidgets.QDoubleSpinBox(self.verticalLayoutWidget_3)
        self.doubleSpinBox_end.setMaximum(99999.99)
        self.doubleSpinBox_end.setObjectName("doubleSpinBox_end")
        self.verticalLayout_2.addWidget(self.doubleSpinBox_end)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.retranslateUi(LabelSpecs)
        self.buttonBox.accepted.connect(LabelSpecs.accept)
        self.buttonBox.rejected.connect(LabelSpecs.reject)
        QtCore.QMetaObject.connectSlotsByName(LabelSpecs)

    def retranslateUi(self, LabelSpecs):
        _translate = QtCore.QCoreApplication.translate
        LabelSpecs.setWindowTitle(_translate("LabelSpecs", "Dialog"))
        self.label_3.setText(_translate("LabelSpecs", "Label"))
        self.label.setText(_translate("LabelSpecs", "From (s)"))
        self.label_2.setText(_translate("LabelSpecs", "To (s)"))

