import datetime as dt

import pytz
from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate, QTime

from controllers.sensor_controller import SensorController
from database.models import Subject, Sensor, SubjectMapping
from gui.designer.edit_subject_sensor_map import Ui_Dialog

INDEX_MAP_ID = 0
INDEX_MAP_SUBJECT = 1
INDEX_MAP_SENSOR = 2
INDEX_MAP_START = 3
INDEX_MAP_END = 4

DT_FORMAT = '%Y-%m-%d %H:%M:%S'


class EditSubjectMappingDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(
            self,
            sensor_controller: SensorController,
            subjects_dict: dict,
            sensors_dict: dict,
            subject_mapping: SubjectMapping,
            project_timezone
    ):
        super().__init__()
        self.setupUi(self)

        self.sensor_controller = sensor_controller
        self.subjects_dict = subjects_dict
        self.sensors_dict = sensors_dict
        self.project_timezone = project_timezone
        self.sensor_usage = subject_mapping

        self.value_changed = False

        self.fill_subject_combobox()
        self.fill_sensor_combobox()
        self.init_date_time_widgets()
        self.init_sensor_mapping()

        # Add the new subject when the 'Ok' button is pressed
        self.comboBox_subject.currentIndexChanged.connect(self.on_value_changed)
        self.comboBox_sensor.currentIndexChanged.connect(self.on_value_changed)
        self.dateEdit_start.dateChanged.connect(self.on_value_changed)
        self.dateEdit_end.dateChanged.connect(self.on_value_changed)
        self.timeEdit_start.timeChanged.connect(self.on_value_changed)
        self.timeEdit_end.timeChanged.connect(self.on_value_changed)
        self.buttonBox.accepted.connect(self.on_accepted)

    def fill_subject_combobox(self):
        self.comboBox_subject.addItems(self.subjects_dict.values())

    def fill_sensor_combobox(self):
        self.comboBox_sensor.addItems(self.sensors_dict.values())

    def init_date_time_widgets(self):
        self.dateEdit_start.setDate(QDate.currentDate().addDays(-1))
        self.dateEdit_end.setDate(QDate.currentDate())
        current_time = QTime()
        current_time.setHMS(QTime.currentTime().hour(), QTime.currentTime().minute(), 0)
        self.timeEdit_start.setTime(current_time)
        self.timeEdit_end.setTime(current_time)

    def init_sensor_mapping(self):
        self.comboBox_subject.setCurrentText(self.sensor_usage.subject.name)
        self.comboBox_sensor.setCurrentText(self.sensor_usage.sensor.name)
        self.dateEdit_start.setDate(self.sensor_usage.start_datetime.date())
        self.dateEdit_end.setDate(self.sensor_usage.end_datetime.date())
        self.timeEdit_start.setTime(self.sensor_usage.start_datetime.time())
        self.timeEdit_end.setTime(self.sensor_usage.end_datetime.time())

    def on_value_changed(self) -> None:
        """ Sets value_changed to True when the user edits a value in the dialog. """
        self.value_changed = True

    def on_accepted(self):
        if self.value_changed:
            subject_name = self.comboBox_subject.currentText()
            sensor_name = self.comboBox_sensor.currentText()

            start_dt = self.dateEdit_start.dateTime()
            start_dt.setTime(self.timeEdit_start.time())
            start_dt = start_dt.toPyDateTime()
            start_dt = self.project_timezone.localize(start_dt).astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')

            end_dt = self.dateEdit_end.dateTime()
            end_dt.setTime(self.timeEdit_end.time())
            end_dt = end_dt.toPyDateTime()
            # Convert to UTC
            end_dt = self.project_timezone.localize(end_dt).astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')

            if start_dt < end_dt:
                subject = Subject.get(Subject.name == subject_name)
                sensor = Sensor.get(Sensor.name == sensor_name)
                self.sensor_controller.edit_subject_mapping(self.sensor_usage, subject, sensor, start_dt, end_dt)
