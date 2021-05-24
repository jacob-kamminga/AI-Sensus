import datetime as dt

import pytz
from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate, QTime

from database.models import Subject, Sensor, SensorUsage
from gui.designer.edit_subject_sensor_map import Ui_Dialog

INDEX_MAP_ID = 0
INDEX_MAP_SUBJECT = 1
INDEX_MAP_SENSOR = 2
INDEX_MAP_START = 3
INDEX_MAP_END = 4

DT_FORMAT = '%Y-%m-%d %H:%M:%S'


class EditSensorUsageDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, subjects_dict: dict, sensors_dict: dict, usage: SensorUsage, project_timezone):
        super().__init__()
        self.setupUi(self)

        self.subjects_dict = subjects_dict
        self.sensors_dict = sensors_dict
        self.project_timezone = project_timezone

        self.usage = usage
        self.usage_edited = False

        self.fill_subject_combobox()
        self.fill_sensor_combobox()
        self.init_date_time_widgets()
        self.set_current_usage()

        # Add the new subject when the 'Ok' button is pressed
        self.buttonBox.accepted.connect(self.edit)

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

    def set_current_usage(self):
        self.comboBox_subject.setCurrentText(self.usage.subject.name)
        self.comboBox_sensor.setCurrentText(self.usage.sensor.name)
        self.dateEdit_start.setDate(self.usage.start_datetime.date())
        self.dateEdit_end.setDate(self.usage.end_datetime.date())
        self.timeEdit_start.setTime(self.usage.start_datetime.time())
        self.timeEdit_end.setTime(self.usage.end_datetime.time())

    def edit(self):
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

        if (subject_name != self.usage.subject.name or sensor_name != self.usage.sensor.name or
                start_dt != self.usage.start_datetime or end_dt != self.usage.end_datetime) and start_dt < end_dt:
            subject_id = Subject.get(Subject.name == subject_name)
            sensor_id = Sensor.get(Sensor.name == sensor_name)

            # Update the SensorUsage row
            sensor_usage = SensorUsage.get_by_id(self.usage.id)
            sensor_usage.subject = subject_id
            sensor_usage.sensor = sensor_id
            sensor_usage.start_datetime = start_dt
            sensor_usage.end_datetime = end_dt
            sensor_usage.save()

            self.usage_edited = True
