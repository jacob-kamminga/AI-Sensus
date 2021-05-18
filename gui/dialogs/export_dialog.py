import csv
import datetime as dt
import os
from pathlib import Path

import pandas as pd
import pytz
from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate, QTime, QDir
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from peewee import JOIN

from data_import.sensor_data import SensorData
from database.models import SensorUsage, SensorDataFile, Subject, Label, LabelType, Sensor, SensorModel
from gui.designer.export_new import Ui_Dialog
from gui.dialogs.export_progress import ExportProgressDialog
from gui.dialogs.project_settings_dialog import ProjectSettingsDialog

from numpy import array_split

COL_LABEL = 'Label'
COL_TIME = 'Time'
COL_TIMESTAMP = 'Timestamp'


def get_labels(sensor_data_file_id: int, start_dt: dt.datetime, end_dt: dt.datetime):
    labels = (Label
              .select(Label.start_time, Label.end_time, LabelType.activity)
              .join(LabelType)
              .where(Label.sensor_data_file == sensor_data_file_id &
                     (Label.start_time.between(start_dt, end_dt) |
                      Label.end_time.between(start_dt, end_dt))))
    return [{'start': label.start_time,
             'end': label.end_time,
             'activity': label.label_type.activity} for label in labels]


class ExportDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, settings: ProjectSettingsDialog, datetime: dt.datetime = None):
        super().__init__()
        self.setupUi(self)

        self.settings = settings
        self.project_timezone = pytz.timezone(settings.get_setting('timezone'))
        self.settings_dict = settings.settings_dict

        self.subjects = Subject.select()
        self.subjects_dict = dict()
        for subject in self.subjects:
            self.subjects_dict[subject.name] = subject.id

        self.init_subject_list_widget()
        self.init_date_time_widgets(datetime)

        self.pushButton_export.clicked.connect(self.export)

    def init_subject_list_widget(self):
        for subject in self.subjects:
            self.listWidget_subjects.addItem(subject.name)

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

    def get_sensor_data(self, sensor_data_file_id: int) -> SensorData:
        file_path = self.get_file_path(sensor_data_file_id)
        model_id = (SensorDataFile
                    .select()
                    .join(Sensor, JOIN.LEFT_OUTER)
                    .join(SensorModel, JOIN.LEFT_OUTER)
                    .where(SensorDataFile.id == sensor_data_file_id)
                    .get()
                    ).sensor.model.id
        sensor_id = SensorDataFile.get_by_id(sensor_data_file_id).sensor.id

        if model_id >= 0 and sensor_id >= 0:
            sensor_timezone = pytz.timezone(Sensor.get_by_id(sensor_id).timezone)
            sensor_data = SensorData(Path(file_path), self.settings, model_id)
            sensor_data.metadata.sensor_timezone = sensor_timezone
            # Parse the utc datetime of the sensor data
            sensor_data.metadata.parse_datetime()
            sensor_data.parse()
        # Sensor model unknown
        else:
            sensor_data = None

        return sensor_data

    def get_file_path(self, sensor_data_file_id: int) -> str:
        """
        Check whether the file paths in the database are still valid and update if necessary.

        :param sensor_data_file_id: The list of file names
        """
        file_path = SensorDataFile.get_by_id(sensor_data_file_id).file_path

        # Check whether the file path is still valid
        if os.path.isfile(file_path):
            return file_path
        else:
            # Invalid:
            # Prompt the user for the correct file path
            file_name = SensorDataFile.get_by_id(sensor_data_file_id).file_name
            new_file_path = self.prompt_file_location(file_name, file_path)

            # Update path in database
            sdf = SensorDataFile.get(SensorDataFile.file_name == file_name)
            sdf.file_path = file_path
            sdf.save()

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

    def prompt_save_location(self, name_suggestion: str):
        # Open QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(self, "Save file",
                                                   self.settings.project_dir.as_posix() + "\\" + name_suggestion + ".csv")

        return file_path

    def get_start_datetime(self) -> dt.datetime:
        start_dt = self.dateEdit_start.dateTime()
        start_dt.setTime(self.timeEdit_start.time())
        return self.project_timezone.localize(start_dt.toPyDateTime()) \
            .astimezone(pytz.utc) \
            .replace(second=0, tzinfo=None)

    def get_end_datetime(self) -> dt.datetime:
        end_dt = self.dateEdit_end.dateTime()
        end_dt.setTime(self.timeEdit_end.time())
        return self.project_timezone.localize(end_dt.toPyDateTime()) \
            .astimezone(pytz.utc) \
            .replace(second=0, tzinfo=None)

    def get_subject_ids(self) -> [int]:
        return [self.subjects_dict.get(item.text()) for item in self.listWidget_subjects.selectedItems()]

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
            subject_name = Subject.get_by_id(subject_id).name
            sensor_query = (SensorUsage
                            .select()
                            .where((SensorUsage.subject == subject_id) &
                                   (
                                           SensorUsage.start_datetime.between(start_dt, end_dt) |
                                           SensorUsage.end_datetime.between(start_dt, end_dt) |
                                           (start_dt >= SensorUsage.start_datetime) & (
                                                       start_dt <= SensorUsage.end_datetime) |
                                           (end_dt >= SensorUsage.start_datetime) & (end_dt <= SensorUsage.end_datetime)
                                   )
                                   ))

            if len(sensor_query) == 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("No labels within timespan.")
                msg.setText(f"There are no labels found between {start_dt} and {end_dt}.")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                return

            for sensor_usage in sensor_query:
                sensor_id = sensor_usage.sensor

                sdf_query = (SensorDataFile
                             .select(SensorDataFile.id)
                             .where((SensorDataFile.sensor == sensor_id) &
                                    SensorDataFile.datetime.between(start_dt, end_dt)))

                for file in sdf_query:
                    file_id = file.id
                    labels = get_labels(file_id, start_dt, end_dt)
                    sensor_data = self.get_sensor_data(file_id)

                    if sensor_data is None:
                        raise Exception('Sensor data not found')

                    if not sensor_data.add_abs_dt_col(use_utc=True):
                        return

                    sensor_data.filter_between_dates(start_dt, end_dt)
                    sensor_data.add_labels(labels)

                    # TODO: Indefinite loading bar / loop over deze call plaatsen.
                    df = df.append(sensor_data.get_data())

                file_path = self.prompt_save_location(subject_name + "_" + str(sensor_id))
                export_dialog = ExportProgressDialog(df, file_path)
                export_dialog.exec()