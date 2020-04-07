import csv
import datetime as dt
import os

import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate, QTime, QDir
from PyQt5.QtWidgets import QFileDialog

from data_import.sensor_data import SensorData
from database.db_export import ExportManager
from database.db_sensor_data_file import SensorDataFileManager
from database.db_subject import SubjectManager
from database.db_subject_sensor_map import SubjectSensorMapManager
from gui.designer_export_new import Ui_Dialog

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


class ExportDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, project_name: str, settings_dict: dict):
        super().__init__()
        self.setupUi(self)

        self.export_manager = ExportManager(project_name)
        self.subject_manager = SubjectManager(project_name)
        self.map_manager = SubjectSensorMapManager(project_name)
        self.sensor_data_file_manager = SensorDataFileManager(project_name)
        self.settings_dict = settings_dict

        self.subject_dict = self.subject_manager.get_all_subjects_name_id()

        self.init_subject_list_widget()
        self.init_date_time_widgets()

        self.pushButton_export.clicked.connect(self.export)

    def init_subject_list_widget(self):
        self.listWidget_subjects.addItems(self.subject_dict.keys())

    def init_date_time_widgets(self):
        self.dateEdit_start.setDate(QDate.currentDate().addDays(-1))
        self.dateEdit_end.setDate(QDate.currentDate())
        self.timeEdit_start.setTime(QTime.currentTime())
        self.timeEdit_end.setTime(QTime.currentTime())

    def get_labels(self):
        selected_subject_ids = [self.subject_dict.get(item.text()) for item in self.listWidget_subjects.selectedItems()]
        selected_start_dt = self.dateEdit_start.dateTime()
        selected_start_dt.setTime(self.timeEdit_start.time())
        selected_start_dt = selected_start_dt.toPyDateTime()
        selected_end_dt = self.dateEdit_end.dateTime()
        selected_end_dt.setTime(self.timeEdit_end.time())
        selected_end_dt = selected_end_dt.toPyDateTime()

        all_sensor_ids = []
        all_labels = []

        for subject_id in selected_subject_ids:
            sensor_ids = self.map_manager.get_sensor_ids_between_dates(subject_id,
                                                                       selected_start_dt,
                                                                       selected_end_dt)
            all_sensor_ids.extend(sensor_ids)

        for sensor_id in all_sensor_ids:
            file_names = self.sensor_data_file_manager.get_file_names_between_dates(sensor_id,
                                                                                    selected_start_dt,
                                                                                    selected_end_dt)

            self.check_file_paths(file_names)

            label_data = self.export_manager.get_label_data_between_dates(sensor_id,
                                                                          selected_start_dt,
                                                                          selected_end_dt)

            all_labels.extend(label_data)

        # Format datetime objects
        all_labels = [(row[0].strftime(DATETIME_FORMAT), row[1].strftime(DATETIME_FORMAT), row[2], row[3])
                      for row in all_labels]

        return all_labels

    def get_sensor_data(self, sensor_ids: [str], start_dt: dt.datetime, end_dt: dt.datetime) -> [pd.DataFrame]:
        for sensor_id in sensor_ids:
            file_names = self.sensor_data_file_manager.get_file_names_between_dates(sensor_id,
                                                                                    start_dt,
                                                                                    end_dt)

            self.check_file_paths(file_names)

            file_paths = [self.sensor_data_file_manager.get_file_path_by_file_name(file_name) for file_name in file_names]

            for file_path in file_paths:
                sensor_data = SensorData(file_path, self.settings_dict)

                sensor_data.add_labels()

    def check_file_paths(self, file_names: [str]):
        """
        Check whether the file paths in the database are still valid and update if necessary.

        :param file_names: The list of file names
        """
        for file_name in file_names:
            # Check whether the file path is still valid
            file_path = self.sensor_data_file_manager.get_file_path_by_file_name(file_name)

            # File path invalid
            if file_path is not None and not os.path.isfile(file_path):
                # Prompt the user for the correct file path
                new_file_path = self.prompt_file_location(file_name, file_path)

                # Update path in database
                self.sensor_data_file_manager.update_file_path(file_name, new_file_path)

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

    @staticmethod
    def save_to_csv(label_data, file_path):
        with open(file_path, 'w', newline='') as out:
            csv_out = csv.writer(out)
            csv_out.writerow(["Start", "End", "Activity", "Sensor ID"])
            csv_out.writerows(label_data)

    def export(self):
        labels = self.get_labels()
        file_path = self.prompt_save_location()

        # Retrieve the SensorData object that parses the sensor data file
        data = SensorData(self.file_path, self.settings_dict)
        sensor_name = self.data.metadata['sn']
        sensor_id = self.sensor_manager.get_id_by_name(sensor_name)

        self.save_to_csv(labels, file_path)
