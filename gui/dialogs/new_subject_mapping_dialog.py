import pytz
from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate, QTime

from controllers.sensor_controller import SensorController
from database.models import SubjectMapping, Subject, Sensor
from gui.designer.new_subject_sensor_map import Ui_Dialog


class NewSubjectMappingDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, sensor_controller: SensorController, subjects_dict: dict, sensors_dict: dict, project_timezone):
        super().__init__()
        self.setupUi(self)

        self.sensor_controller = sensor_controller
        self.subjects_dict = subjects_dict
        self.sensors_dict = sensors_dict
        self.project_timezone = project_timezone

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
        subject_name = self.comboBox_subject.currentText()
        sensor_name = self.comboBox_sensor.currentText()

        start_dt = self.dateEdit_start.dateTime()
        start_dt.setTime(self.timeEdit_start.time())
        start_dt = start_dt.toPyDateTime()
        # Convert to UTC
        start_dt = self.project_timezone.localize(start_dt).astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')

        end_dt = self.dateEdit_end.dateTime()
        end_dt.setTime(self.timeEdit_end.time())
        end_dt = end_dt.toPyDateTime()
        # Convert to UTC
        end_dt = self.project_timezone.localize(end_dt).astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')

        if subject_name is not None and \
                sensor_name is not None and \
                start_dt is not None and \
                end_dt is not None and \
                start_dt < end_dt:
            subject_id = Subject.get(Subject.name == subject_name)
            sensor_id = Sensor.get(Sensor.name == sensor_name)
            SubjectMapping.create(subject=subject_id, sensor_id=sensor_id, start_datetime=start_dt, end_datetime=end_dt)
            self.new_map_added = True
