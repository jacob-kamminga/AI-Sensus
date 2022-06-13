import csv
import datetime as dt
from pathlib import Path

import pytz
from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate, QTime
from PyQt5.QtWidgets import QMessageBox

from database.models import Subject
from date_utils import naive_to_utc
from gui.designer.export_new import Ui_Dialog
from gui.dialogs.export_progress_dialog import ExportProgressDialog

COL_LABEL = 'Label'
COL_TIME = 'Time'
COL_TIMESTAMP = 'Timestamp'

class ExportDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, gui):
        super().__init__()
        self.setupUi(self)
        self.gui = gui
        self.project_controller = gui.project_controller
        self.sensor_controller = gui.sensor_controller
        self.project_timezone = pytz.timezone(self.project_controller.get_setting('timezone'))

        self.subjects = Subject.select()
        self.subjects_dict = dict()

        for subject in self.subjects:
            self.subjects_dict[subject.name] = subject.id

            # Initialise subject list widget
            self.listWidget_subjects.addItem(subject.name)

        # Initialise datetime widgets
        datetime = gui.sensor_controller.utc_dt
        if datetime is not None:
            self.dateEdit_start.setDate(datetime.date())
            self.dateEdit_end.setDate(datetime.date())
            self.timeEdit_start.setTime(datetime.time())
            self.timeEdit_end.setTime((datetime + dt.timedelta(hours=1)).time())
        else:
            self.dateEdit_start.setDate(QDate.currentDate().addDays(-1))
            self.dateEdit_end.setDate(QDate.currentDate())
            self.timeEdit_start.setTime(QTime.currentTime())
            self.timeEdit_end.setTime(QTime.currentTime())

        self.pushButton_export.clicked.connect(self.export)

    def get_start_datetime(self) -> dt.datetime:
        """
        Retrieve the start datetime from the export dialog.

        :return: Start datetime either in local format.
        """
        start_dt = self.dateEdit_start.dateTime()
        start_dt.setTime(self.timeEdit_start.time())
        start_pydt = start_dt.toPyDateTime()
        return start_pydt

    def get_end_datetime(self) -> dt.datetime:
        """
        Retrieve the end datetime from the export dialog.

        :return: End datetime either in local format.
        """
        end_dt = self.dateEdit_end.dateTime()
        end_dt.setTime(self.timeEdit_end.time())
        end_pydt = end_dt.toPyDateTime()
        return end_pydt

    def dt_to_utc(self, dt_: dt.datetime):
        return self.project_timezone.localize(dt_).astimezone(pytz.utc).replace(second=0)

    def get_subject_ids(self) -> [int]:
        return [self.subjects_dict.get(item.text()) for item in self.listWidget_subjects.selectedItems()]

    @staticmethod
    # Obsolete?
    def save_to_csv(label_data, file_path: Path):
        with file_path.open(mode='w', newline='') as out:
            csv_out = csv.writer(out)
            csv_out.writerow(["Start", "End", "Activity", "Sensor ID"])
            csv_out.writerows(label_data)

    def export(self):

        # Loop through each subject that the user wants to export.
        # For each subject, create a separate file.
        # For each subject mapping within the specified interval, get the data within
        # that interval from the appropriate sensor data file(s).
        # For each of the found sensor data files, get the annotations (labels) in the interval, append the data
        # to the subject's export file.

        subject_ids = self.get_subject_ids()
        start_dt_local = self.get_start_datetime()
        start_dt = naive_to_utc(start_dt_local, self.project_timezone)
        end_dt_local = self.get_end_datetime()
        end_dt = naive_to_utc(end_dt_local, self.project_timezone)
        
        if len(subject_ids) == 0:
           QMessageBox.information(self, "Export", "Please select a subject")
           return
        try:
            export_progess_dialog = ExportProgressDialog(self.gui, subject_ids, start_dt, end_dt)
            export_progess_dialog.exec()
        except RuntimeError:
            # User cancelled (one of the) the file path prompt or there are no labels in the given timespan.
            pass
