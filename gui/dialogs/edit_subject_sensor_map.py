import datetime as dt

from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate, QTime

from database.sensor_manager import SensorManager
from database.subject_manager import SubjectManager
from database.sensor_usage_manager import SensorUsageManager
from gui.designer.edit_subject_sensor_map import Ui_Dialog

INDEX_MAP_ID = 0
INDEX_MAP_SUBJECT = 1
INDEX_MAP_SENSOR = 2
INDEX_MAP_START = 3
INDEX_MAP_END = 4

DT_FORMAT = '%Y-%m-%d %H:%M:%S'


class EditSubjectSensorMapDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self,
                 map_manager: SensorUsageManager,
                 subject_manager: SubjectManager,
                 sensor_manager: SensorManager,
                 subjects_dict: dict,
                 sensors_dict: dict,
                 map_id: int):
        super().__init__()
        self.setupUi(self)

        self.map_manager = map_manager
        self.subject_manager = subject_manager
        self.sensor_manager = sensor_manager
        self.subjects_dict = subjects_dict
        self.sensors_dict = sensors_dict
        self.map_id = map_id

        self.map_edited = False
        self.old_subject = None
        self.old_sensor = None
        self.old_start_dt = None
        self.old_end_dt = None

        self.fill_subject_combobox()
        self.fill_sensor_combobox()
        self.init_date_time_widgets()
        self.set_current_map()

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

    def set_current_map(self):
        map_ = self.map_manager.get_usage_by_id(self.map_id)[0]
        subject_id = map_[INDEX_MAP_SUBJECT]
        sensor_id = map_[INDEX_MAP_SENSOR]

        self.old_subject = self.subjects_dict[subject_id]
        self.old_sensor = self.sensors_dict[sensor_id]
        self.old_start_dt: dt.datetime = dt.datetime.strptime(map_[INDEX_MAP_START], DT_FORMAT)
        self.old_end_dt: dt.datetime = dt.datetime.strptime(map_[INDEX_MAP_END], DT_FORMAT)

        self.comboBox_subject.setCurrentText(self.old_subject)
        self.comboBox_sensor.setCurrentText(self.old_sensor)
        self.dateEdit_start.setDate(self.old_start_dt.date())
        self.dateEdit_end.setDate(self.old_end_dt.date())
        self.timeEdit_start.setTime(self.old_start_dt.time())
        self.timeEdit_end.setTime(self.old_end_dt.time())

    def edit(self):
        subject = self.comboBox_subject.currentText()
        sensor = self.comboBox_sensor.currentText()

        start_dt = self.dateEdit_start.dateTime()
        start_dt.setTime(self.timeEdit_start.time())
        start_dt = start_dt.toPyDateTime()

        end_dt = self.dateEdit_end.dateTime()
        end_dt.setTime(self.timeEdit_end.time())
        end_dt = end_dt.toPyDateTime()

        if (subject != self.old_subject or
                sensor != self.old_sensor or
                start_dt != self.old_start_dt or
                end_dt != self.old_end_dt) and \
                start_dt < end_dt:
            subject_id = self.subject_manager.get_id_by_name(subject)
            sensor_id = self.sensor_manager.get_id_by_name(sensor)

            self.map_manager.update_usage(self.map_id, subject_id, sensor_id, start_dt, end_dt)
            self.map_edited = True
