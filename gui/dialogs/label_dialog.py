import datetime as dt
from typing import List

import peewee
import pytz
from PyQt5 import QtWidgets
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QMessageBox
from peewee import DoesNotExist

from controllers.sensor_controller import SensorController
from database.models import LabelType, Label
from date_utils import naive_to_utc
from gui.designer.label_specs import Ui_LabelSpecs

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
QDATETIME_FORMAT = "yyyy-MM-dd HH:mm:ss.zzz"


class LabelDialog(QtWidgets.QDialog, Ui_LabelSpecs):

    def __init__(self, sensor_controller: SensorController):
        super().__init__()
        self.setupUi(self)

        self.sensor_timezone = sensor_controller.sensor_data.metadata.sensor_timezone
        self.label = Label(sensor_data_file=sensor_controller.sensor_data_file.id)
        self.sensor_data_file_id = sensor_controller.sensor_data_file.id
        self.is_accepted = False

        # Connect methods to listeners
        self.accepted.connect(self.add_label_to_db)
        self.comboBox_labels.currentTextChanged.connect(self.update_label_type)
        self.comboBox_labels.currentTextChanged.connect(self.toggle_confirm_annotation)

        # Add activities to the labels combobox
        self.comboBox_labels.addItems([label_type.activity for label_type in LabelType.select()])

        self.toggle_confirm_annotation()

    def update_label_type(self, activity: str):
        label_type = LabelType.get(LabelType.activity == activity).id
        self.label.label_type = label_type

    def trim_overlap(self, time, pos: str = 'begin') -> str:
        """
        If <code>time</code> overlaps with an existing label, snap it to the begin/end of that label.
        """
        try:
            overlapping_label = (
                Label.get(
                    (Label.sensor_data_file == self.sensor_data_file_id) &
                    (Label.start_time <= time) &
                    (Label.end_time >= time)
                )
            )

            if pos == 'begin':
                return overlapping_label.end_time
            elif pos == 'end':
                return overlapping_label.start_time
            else:
                raise ValueError("pos is not in ['begin', 'end']")
        except DoesNotExist:
            return time

    def set_times(self, datetime1, datetime2) -> None:
        # Set begin and end datetimes
        if datetime1 <= datetime2:
            begin = datetime1
            end = datetime2
        else:
            begin = datetime2
            end = datetime1

        self.label.start_time = self.trim_overlap(begin, 'begin')
        self.label.end_time = self.trim_overlap(end, 'end')

    def add_label_to_db(self):
        if self.label is not None:
            start_datetime = self.dateTimeEdit_start.dateTime().toPyDateTime()
            end_datetime = self.dateTimeEdit_end.dateTime().toPyDateTime()

            # Convert start and end times to UTC
            self.label.start_time = naive_to_utc(start_datetime, self.sensor_timezone)
            self.label.end_time = naive_to_utc(end_datetime, self.sensor_timezone)

            if self.label.label_type is not None:
                # Save the label to the database
                try:
                    self.is_accepted = self.label.save()
                except peewee.IntegrityError:
                    msg = QMessageBox()
                    msg.setWindowTitle('Error')
                    msg.setText('There already exists a label with the same start time.')
                    msg.exec()

    def show_dialog(self, shortcut_label):
        if self.label.start_time.tzinfo is None:
            self.label.start_time = pytz.utc.localize(self.label.start_time, is_dst=None)
        if self.label.end_time.tzinfo is None:
            self.label.end_time = pytz.utc.localize(self.label.end_time, is_dst=None)

        # Set the minimal difference between start and end to 0.5 seconds
        if self.label.end_time - self.label.start_time < dt.timedelta(seconds=0.5):
            self.label.end_time = self.label.end_time + dt.timedelta(seconds=0.5)

        # Localize start and end times
        self.dateTimeEdit_start.setDateTime(
            QDateTime(self.label.start_time.astimezone(self.sensor_timezone))
        )
        self.dateTimeEdit_end.setDateTime(
            QDateTime(self.label.end_time.astimezone(self.sensor_timezone))
        )
        if shortcut_label:
            self.label.label_type = shortcut_label
            self.add_label_to_db()
        else:
            self.exec()

    def toggle_confirm_annotation(self):
        OK_button = self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        if self.comboBox_labels.currentText() == '':
            OK_button.setEnabled(False)
        else:
            OK_button.setEnabled(True)
