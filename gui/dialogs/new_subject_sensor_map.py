from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate, QTime

from database.sensor_manager import SensorManager
from database.subject_manager import SubjectManager
from database.sensor_usage_manager import SensorUsageManager
from gui.designer.new_subject_sensor_map import Ui_Dialog


class NewSubjectSensorMapDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self,
                 map_manager: SensorUsageManager,
                 subject_manager: SubjectManager,
                 sensor_manager: SensorManager,
                 subjects_dict: dict,
                 sensors_dict: dict):
        super().__init__()
        self.setupUi(self)

        self.map_manager = map_manager
        self.subject_manager = subject_manager
        self.sensor_manager = sensor_manager
        self.subjects_dict = subjects_dict
        self.sensors_dict = sensors_dict

        self.new_map_added = False

        self.fill_subject_combobox()
        self.fill_sensor_combobox()
        self.init_date_time_widgets()

        # Add the new subject when the 'Ok' button is pressed
        self.buttonBox.accepted.connect(self.add)

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

    def add(self):
        new_map_subject_name = self.comboBox_subject.currentText()
        new_map_sensor_name = self.comboBox_sensor.currentText()

        new_map_start_dt = self.dateEdit_start.dateTime()
        new_map_start_dt.setTime(self.timeEdit_start.time())
        new_map_start_dt = new_map_start_dt.toPyDateTime()

        new_map_end_dt = self.dateEdit_end.dateTime()
        new_map_end_dt.setTime(self.timeEdit_end.time())
        new_map_end_dt = new_map_end_dt.toPyDateTime()

        if new_map_subject_name is not None and \
                new_map_sensor_name is not None and \
                new_map_start_dt is not None and \
                new_map_end_dt is not None and \
                new_map_start_dt < new_map_end_dt:
            new_map_subject_id = self.subject_manager.get_id_by_name(new_map_subject_name)
            new_map_sensor_id = self.sensor_manager.get_id_by_name(new_map_sensor_name)

            self.map_manager.add_usage(new_map_subject_id, new_map_sensor_id, new_map_start_dt, new_map_end_dt)
            self.new_map_added = True
