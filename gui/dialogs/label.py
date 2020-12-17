import datetime as dt
from typing import Optional

import pytz
from PyQt5 import QtWidgets
from PyQt5.QtCore import QDateTime

from database.label_manager import LabelManager
from database.label_type_manager import LabelTypeManager
from gui.designer.label_specs import Ui_LabelSpecs

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
QDATETIME_FORMAT = "yyyy-MM-dd HH:mm:ss.zzz"


class LabelSpecs(QtWidgets.QDialog, Ui_LabelSpecs):

    def __init__(self, sensor_data_file: int, label_manager: LabelManager, label_type_manager: LabelTypeManager,
                 sensor_timezone):
        super().__init__()
        self.setupUi(self)

        self.sensor_data_file = sensor_data_file
        self.label_manager = label_manager
        self.label_type_manager = label_type_manager
        self.sensor_timezone = sensor_timezone

        self.label_type_dict = dict()

        for row in self.label_type_manager.get_all_label_types():
            self.label_type_dict[row["activity"]] = {"id": row["id"],
                                                     "color": row["color"],
                                                     "description": row["description"]}

        self.start_time = None  # Start time of label in UTC format
        self.end_time = None  # End time of label in UTC format
        self.selected_label = Label()
        self.is_accepted = False

        # Connect methods to listeners
        self.accepted.connect(self.add_label_to_db)
        self.comboBox_labels.currentTextChanged.connect(self.update_label_type)

        self.comboBox_labels.addItems(self.label_type_dict.keys())

    def update_label_type(self, activity: str):
        self.selected_label.type = self.label_type_dict[activity]["id"]

    def add_label_to_db(self):
        self.start_time = self.sensor_timezone.localize(
            self.dateTimeEdit_start.dateTime().toPyDateTime()
        ).astimezone(pytz.utc)
        self.end_time = self.sensor_timezone.localize(
            self.dateTimeEdit_end.dateTime().toPyDateTime()
        ).astimezone(pytz.utc)

        self.selected_label.start = self.start_time.replace(tzinfo=None)
        self.selected_label.end = self.end_time.replace(tzinfo=None)

        if self.selected_label.type is not None:
            self.label_manager.add_label(self.selected_label.start,
                                         self.selected_label.end,
                                         self.selected_label.type,
                                         self.sensor_data_file)
            self.is_accepted = True

    def show_dialog(self, shortcut_label):
        if self.start_time.tzinfo is None:
            self.start_time = pytz.utc.localize(self.start_time, is_dst=None)
        if self.end_time.tzinfo is None:
            self.end_time = pytz.utc.localize(self.end_time, is_dst=None)

        if self.end_time - self.start_time < dt.timedelta(seconds=0.5):
            self.end_time = self.end_time + dt.timedelta(seconds=0.5)

        self.dateTimeEdit_start.setDateTime(
            QDateTime.fromString(self.start_time.astimezone(
                self.sensor_timezone).strftime(DATETIME_FORMAT)[:-3], QDATETIME_FORMAT)
        )
        self.dateTimeEdit_end.setDateTime(
            QDateTime.fromString(self.end_time.astimezone(
                self.sensor_timezone).strftime(DATETIME_FORMAT)[:-3], QDATETIME_FORMAT)
        )
        if shortcut_label:
            self.selected_label.type = shortcut_label
            self.add_label_to_db()
        else:
            self.exec()


class Label:

    def __init__(self):
        self.type: Optional[int] = None
        self.start: Optional[dt.datetime] = None
        self.end: Optional[dt.datetime] = None
