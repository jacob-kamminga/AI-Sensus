import csv
import datetime as dt
import os
from pathlib import Path

import pandas as pd
import pytz
from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate, QTime, QDir, Qt
from PyQt5.QtWidgets import QFileDialog, QDialog, QPushButton

from data_import.sensor_data import SensorData
from database.export_manager import ExportManager
from database.sensor_data_file_manager import SensorDataFileManager
from database.sensor_manager import SensorManager
from database.subject_manager import SubjectManager
from database.sensor_usage_manager import SensorUsageManager
from gui.designer.export_new import Ui_Dialog
from project_settings import ProjectSettingsDialog

COL_LABEL = 'Label'
COL_TIME = 'Time'
COL_TIMESTAMP = 'Timestamp'


class ExportDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, settings: ProjectSettingsDialog, datetime: dt.datetime = None):
        super().__init__()
        self.setupUi(self)

        self.settings = settings
        self.export_manager = ExportManager(settings)
        self.subject_manager = SubjectManager(settings)
        self.map_manager = SensorUsageManager(settings)
        self.sensor_data_file_manager = SensorDataFileManager(settings)
        self.sensor_manager = SensorManager(settings)
        self.settings_dict = settings.settings_dict

        self.subject_dict = self.subject_manager.get_all_subjects_name_id()

        self.init_subject_list_widget()
        self.init_date_time_widgets(datetime)

        self.pushButton_export.clicked.connect(self.export)

    def init_subject_list_widget(self):
        self.listWidget_subjects.addItems(self.subject_dict.keys())

    def init_date_time_widgets(self, datetime):
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

    def get_sensor_ids(self, subject_id: int, start_dt: dt.datetime, end_dt: dt.datetime) -> [int]:
        return self.map_manager.get_sensor_ids_by_dates(subject_id, start_dt, end_dt)

    def get_sensor_data_file_ids(self, sensor_id: int, start_dt: dt.datetime, end_dt: dt.datetime) -> [int]:
        return self.sensor_data_file_manager.get_ids_by_sensor_and_dates(sensor_id,
                                                                         start_dt,
                                                                         end_dt)

    def get_labels(self, sensor_data_file_id: int, start_dt: dt.datetime, end_dt: dt.datetime):
        labels = self.export_manager.get_labels_by_dates(sensor_data_file_id,
                                                         start_dt,
                                                         end_dt)
        return [{"start": label["start_time"],
                 "end": label["end_time"],
                 "activity": label["activity"]} for label in labels]

    def get_sensor_data(self, sensor_data_file_id: int) -> SensorData:
        file_path = self.get_file_path(sensor_data_file_id)
        model_id = self.sensor_data_file_manager.get_sensor_model_by_id(sensor_data_file_id)
        sensor_id = self.sensor_data_file_manager.get_sensor_by_id(sensor_data_file_id)

        if model_id >= 0 and sensor_id >= 0:
            sensor_timezone = pytz.timezone(self.sensor_manager.get_timezone_by_id(sensor_id))
            sensor_data = SensorData(Path(file_path), self.settings, model_id, sensor_timezone)
            # Parse the utc datetime of the sensor data
            sensor_data.metadata.parse_datetime()
        # Sensor model unknown
        else:
            sensor_data = None

        return sensor_data

    def get_file_path(self, sensor_data_file_id: int) -> str:
        """
        Check whether the file paths in the database are still valid and update if necessary.

        :param sensor_data_file_id: The list of file names
        """
        file_path = self.sensor_data_file_manager.get_file_path_by_id(sensor_data_file_id)

        # Check whether the file path is still valid
        if os.path.isfile(file_path):
            return file_path
        else:
            # Invalid:
            # Prompt the user for the correct file path
            file_name = self.sensor_data_file_manager.get_file_name_by_id(sensor_data_file_id)
            new_file_path = self.prompt_file_location(file_name, file_path)

            # Update path in database
            self.sensor_data_file_manager.update_file_path(file_name, new_file_path)

            return new_file_path

    def prompt_file_location(self, file_name: str, old_path: str) -> str:
        """
        Open a QFileDialog in which the user can select a new file path

        :param file_name: The file name
        :param old_path: The old (invalid) file path
        :return: The new (valid) file path
        """
        # Split path to obtain the base path
        base_path = old_path.rsplit('/', 1)[0]

        if not os.path.isdir(base_path):
            base_path = QDir.homePath()

        # Open QFileDialog
        dialog = QFileDialog()
        dialog.setNameFilter(file_name)
        new_path, _ = dialog.getOpenFileName(self.gui, "Open Sensor Data", base_path, filter="csv (*.csv)")

        return new_path

    def prompt_save_location(self):
        # Open QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(self, "Save file")

        return file_path

    def get_start_datetime(self) -> dt.datetime:
        start_dt = self.dateEdit_start.dateTime()
        start_dt.setTime(self.timeEdit_start.time())
        return start_dt.toPyDateTime()

    def get_end_datetime(self) -> dt.datetime:
        end_dt = self.dateEdit_end.dateTime()
        end_dt.setTime(self.timeEdit_end.time())
        return end_dt.toPyDateTime()

    def get_subject_ids(self) -> [int]:
        return [self.subject_dict.get(item.text()) for item in self.listWidget_subjects.selectedItems()]

    @staticmethod
    def save_to_csv(label_data, file_path):
        with open(file_path, 'w', newline='') as out:
            csv_out = csv.writer(out)
            csv_out.writerow(["Start", "End", "Activity", "Sensor ID"])
            csv_out.writerows(label_data)

    def export(self):
        subject_ids: [int] = self.get_subject_ids()
        start_dt: dt.datetime = self.get_start_datetime()
        end_dt: dt.datetime = self.get_end_datetime()

        for subject_id in subject_ids:
            df: pd.DataFrame = pd.DataFrame()
            sensor_ids = self.get_sensor_ids(subject_id, start_dt, end_dt)

            for sensor_id in sensor_ids:
                sensor_data_file_ids = self.get_sensor_data_file_ids(sensor_id, start_dt, end_dt)

                for file_id in sensor_data_file_ids:
                    labels = self.get_labels(file_id, start_dt, end_dt)
                    sensor_data = self.get_sensor_data(file_id)

                    if sensor_data is None:
                        raise Exception('Sensor data not found')

                    sensor_data.add_timestamp_column(COL_TIME)
                    start_dt = sensor_data.project_timezone.localize(start_dt)
                    end_dt = sensor_data.project_timezone.localize(end_dt)

                    sensor_data.filter_between_dates(start_dt, end_dt)
                    sensor_data.add_labels(labels)

                    df = df.append(sensor_data.get_data())

                file_path = self.prompt_save_location()

                if file_path:
                    df.to_csv(file_path)

        d = QDialog()
        b = QPushButton("OK", d)
        b.clicked.connect(d.close)
        d.setWindowTitle("Export successful")
        d.setWindowModality(Qt.ApplicationModal)
        d.exec()
