# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer_subject_table.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Subject_table(object):
    def setupUi(self, Subject_table):
        Subject_table.setObjectName("Subject_table")
        Subject_table.resize(677, 408)
        self.tableWidget = QtWidgets.QTableWidget(Subject_table)
        self.tableWidget.setGeometry(QtCore.QRect(5, 10, 661, 351))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tableWidget.verticalHeader().setVisible(False)
        self.rowButton = QtWidgets.QPushButton(Subject_table)
        self.rowButton.setGeometry(QtCore.QRect(10, 370, 93, 28))
        self.rowButton.setObjectName("rowButton")
        self.colButton = QtWidgets.QPushButton(Subject_table)
        self.colButton.setGeometry(QtCore.QRect(110, 370, 93, 28))
        self.colButton.setObjectName("colButton")
        self.closeButton = QtWidgets.QPushButton(Subject_table)
        self.closeButton.setGeometry(QtCore.QRect(570, 370, 93, 28))
        self.closeButton.setObjectName("closeButton")
        self.delSubjectButton = QtWidgets.QPushButton(Subject_table)
        self.delSubjectButton.setGeometry(QtCore.QRect(250, 370, 121, 28))
        self.delSubjectButton.setObjectName("delSubjectButton")
        self.delColumnButton = QtWidgets.QPushButton(Subject_table)
        self.delColumnButton.setGeometry(QtCore.QRect(380, 370, 121, 28))
        self.delColumnButton.setObjectName("delColumnButton")

        self.retranslateUi(Subject_table)
        QtCore.QMetaObject.connectSlotsByName(Subject_table)

    def retranslateUi(self, Subject_table):
        _translate = QtCore.QCoreApplication.translate
        Subject_table.setWindowTitle(_translate("Subject_table", "Subject table"))
        self.rowButton.setText(_translate("Subject_table", "Add subject"))
        self.colButton.setText(_translate("Subject_table", "Add column"))
        self.closeButton.setText(_translate("Subject_table", "Close"))
        self.delSubjectButton.setText(_translate("Subject_table", "Remove a subject"))
        self.delColumnButton.setText(_translate("Subject_table", "Remove a column"))

