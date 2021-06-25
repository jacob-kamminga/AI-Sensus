import datetime as dt

import pytz
from PyQt5 import QtWidgets
from PyQt5.QtCore import QDateTime

from database.models import LabelType, Label
from gui.designer.label_specs import Ui_LabelSpecs

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
QDATETIME_FORMAT = "yyyy-MM-dd HH:mm:ss.zzz"


class LabelSpecs(QtWidgets.QDialog, Ui_LabelSpecs):

    def __init__(self, sensor_data_file: int, sensor_timezone):
        super().__init__()
        self.setupUi(self)

        self.sensor_timezone = sensor_timezone
        self.label_types = LabelType.select()
        activities = []

        for label_type in LabelType.select():
            activities.append(label_type.activity)

        self.label = Label(sensor_data_file=sensor_data_file)
        self.is_accepted = False

        # Connect methods to listeners
        self.accepted.connect(self.add_label_to_db)
        self.comboBox_labels.currentTextChanged.connect(self.update_label_type)
        self.comboBox_labels.currentTextChanged.connect(self.toggle_confirm_annotation)

        # Add items to the labels combobox
        self.comboBox_labels.addItems(activities)

        self.toggle_confirm_annotation()

    def update_label_type(self, activity: str):
        label_type = LabelType.get(LabelType.activity == activity).id
        self.label.label_type = label_type

    def add_label_to_db(self):
        if self.label is not None:
            # Convert start and end times to UTC
            start_time_local = self.sensor_timezone.localize(self.dateTimeEdit_start.dateTime().toPyDateTime())
            self.label.start_time = start_time_local.astimezone(pytz.utc).replace(tzinfo=None)
            end_time_local = self.sensor_timezone.localize(self.dateTimeEdit_end.dateTime().toPyDateTime())
            self.label.end_time = end_time_local.astimezone(pytz.utc).replace(tzinfo=None)

            if self.label.label_type is not None:
                # Save the label to the database
                self.is_accepted = self.label.save()

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
            QDateTime.fromString(self.label.start_time.astimezone(self.sensor_timezone).strftime(DATETIME_FORMAT)[:-3],
                                 QDATETIME_FORMAT))
        self.dateTimeEdit_end.setDateTime(
            QDateTime.fromString(self.label.end_time.astimezone(self.sensor_timezone).strftime(DATETIME_FORMAT)[:-3],
                                 QDATETIME_FORMAT))
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
