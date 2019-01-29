import os
import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox


from gui.designer_new import Ui_NewProject
from datastorage import settings


def exit_project():
    sys.exit(0)


class NewProject(QtWidgets.QDialog, Ui_NewProject):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.accepted.connect(self.open_project)
        self.rejected.connect(exit_project)
        for folder in os.listdir("projects"):
            self.comboBox_existing.addItem(folder)
        self.lineEdit_new.textChanged.connect(self.text_changed)
        self.comboBox_existing.currentTextChanged.connect(self.name_changed)
        self.project_name = ""
        if os.listdir("projects"):
            self.project_name = os.listdir("projects")[0]
            self.spinBox_timerow.setEnabled(False)
            self.spinBox_timecol.setEnabled(False)
            self.spinBox_daterow.setEnabled(False)
            self.spinBox_datecol.setEnabled(False)
            self.spinBox_srrow.setEnabled(False)
            self.spinBox_srcol.setEnabled(False)
            self.spinBox_snrow.setEnabled(False)
            self.spinBox_sncol.setEnabled(False)
            self.spinBox_namesrow.setEnabled(False)
            self.lineEdit_comment.setEnabled(False)
        else:
            self.comboBox_existing.setEnabled(False)
        self.time_row = 3
        self.spinBox_timerow.valueChanged.connect(self.set_timerow)
        self.time_col = 3
        self.spinBox_timecol.valueChanged.connect(self.set_timecol)
        self.date_row = 3
        self.spinBox_daterow.valueChanged.connect(self.set_daterow)
        self.date_col = 2
        self.spinBox_datecol.valueChanged.connect(self.set_datecol)
        self.sr_row = 5
        self.spinBox_srrow.valueChanged.connect(self.set_srrow)
        self.sr_col = 2
        self.spinBox_srcol.valueChanged.connect(self.set_srcol)
        self.sn_row = 2
        self.spinBox_snrow.valueChanged.connect(self.set_snrow)
        self.sn_col = 5
        self.spinBox_sncol.valueChanged.connect(self.set_sncol)
        self.names_row = 8
        self.spinBox_namesrow.valueChanged.connect(self.set_namesrow)
        self.comment = ";"
        self.lineEdit_comment.textChanged.connect(self.set_comment)
        self.spinBox_timerow.setValue(3)
        self.spinBox_timecol.setValue(3)
        self.spinBox_daterow.setValue(3)
        self.spinBox_datecol.setValue(2)
        self.spinBox_srrow.setValue(5)
        self.spinBox_srcol.setValue(2)
        self.spinBox_snrow.setValue(2)
        self.spinBox_sncol.setValue(5)
        self.spinBox_namesrow.setValue(8)
        self.lineEdit_comment.setText(";")

    def open_project(self):
        if self.lineEdit_new.text():
            settings.new_project(self.project_name)
            self.new_settings = settings.Settings(self.project_name)
            self.new_settings.set_setting("time_row", self.time_row)
            self.new_settings.set_setting("time_col", self.time_col)
            self.new_settings.set_setting("date_row", self.date_row)
            self.new_settings.set_setting("date_col", self.date_col)
            self.new_settings.set_setting("sr_row", self.sr_row)
            self.new_settings.set_setting("sr_col", self.sr_col)
            self.new_settings.set_setting("sn_row", self.sn_row)
            self.new_settings.set_setting("sn_col", self.sn_col)
            self.new_settings.set_setting("names_row", self.names_row)
            self.new_settings.set_setting("comment", self.comment)
        self.new_settings = settings.Settings(self.project_name)

    def text_changed(self, new):
        if self.lineEdit_new.text():
            self.project_name = new

            self.comboBox_existing.setEnabled(False)
            self.spinBox_timerow.setEnabled(True)
            self.spinBox_timecol.setEnabled(True)
            self.spinBox_daterow.setEnabled(True)
            self.spinBox_datecol.setEnabled(True)
            self.spinBox_srrow.setEnabled(True)
            self.spinBox_srcol.setEnabled(True)
            self.spinBox_snrow.setEnabled(True)
            self.spinBox_sncol.setEnabled(True)
            self.spinBox_namesrow.setEnabled(True)
            self.lineEdit_comment.setEnabled(True)

            self.spinBox_timerow.setValue(3)
            self.spinBox_timecol.setValue(3)
            self.spinBox_daterow.setValue(3)
            self.spinBox_datecol.setValue(2)
            self.spinBox_srrow.setValue(5)
            self.spinBox_srcol.setValue(2)
            self.spinBox_snrow.setValue(2)
            self.spinBox_sncol.setValue(5)
            self.spinBox_namesrow.setValue(8)
            self.lineEdit_comment.setText(";")
        else:
            if os.listdir("projects"):
                self.project_name = os.listdir("projects")[0]
                self.comboBox_existing.setEnabled(True)
                self.spinBox_timerow.setEnabled(False)
                self.spinBox_timecol.setEnabled(False)
                self.spinBox_daterow.setEnabled(False)
                self.spinBox_datecol.setEnabled(False)
                self.spinBox_srrow.setEnabled(False)
                self.spinBox_srcol.setEnabled(False)
                self.spinBox_snrow.setEnabled(False)
                self.spinBox_sncol.setEnabled(False)
                self.spinBox_namesrow.setEnabled(False)
                self.lineEdit_comment.setEnabled(False)
            else:
                self.project_name = ""

    def name_changed(self, name):
        self.project_name = name

    def set_timerow(self, new):
        self.time_row = new

    def set_timecol(self, new):
        self.time_col = new

    def set_daterow(self, new):
        self.date_row = new

    def set_datecol(self, new):
        self.date_col = new

    def set_srrow(self, new):
        self.sr_row = new

    def set_srcol(self, new):
        self.sr_col = new

    def set_snrow(self, new):
        self.sn_row = new

    def set_sncol(self, new):
        self.sn_col = new

    def set_namesrow(self, new):
        self.names_row = new

    def set_comment(self, new):
        self.comment = new

    def accept(self):
        if self.lineEdit_new.text() in [self.comboBox_existing.itemText(i) for i in range(
                self.comboBox_existing.count())]:
            QMessageBox.warning(self, 'Warning', "The name of your new project already exists",
                                QMessageBox.Cancel)
        elif not self.project_name:
            QMessageBox.warning(self, 'Warning', "Choose a name for your project",
                                QMessageBox.Cancel)
        else:
            super().accept()
