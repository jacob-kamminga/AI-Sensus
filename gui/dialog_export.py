import csv

from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate, QTime
from PyQt5.QtWidgets import QFileDialog

from database.db_export import ExportManager
from database.db_subject import SubjectManager
from database.db_subject_sensor_map import SubjectSensorMapManager
from gui.designer_export_new import Ui_Dialog

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


class ExportDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, project_name: str):
        super().__init__()
        self.setupUi(self)

        self.export_manager = ExportManager(project_name)
        self.subject_manager = SubjectManager(project_name)
        self.map_manager = SubjectSensorMapManager(project_name)

        self.subject_dict = self.subject_manager.get_all_subjects_name_id()

        self.fill_subject_list_widget()
        self.init_date_time_widgets()

        self.pushButton_export.clicked.connect(self.export)

    def fill_subject_list_widget(self):
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
            label_data = self.export_manager.get_label_data_between_dates(sensor_id,
                                                                          selected_start_dt,
                                                                          selected_end_dt)

            all_labels.extend(label_data)

        # Format datetime objects
        all_labels = [(row[0].strftime(DATETIME_FORMAT), row[1].strftime(DATETIME_FORMAT), row[2], row[3])
                      for row in all_labels]

        return all_labels

    def prompt_save_location(self):
        # Get the user input from a dialog window
        file_path, _ = QFileDialog.getSaveFileName(self, "Save file")

        return file_path

    def save_to_csv(self, label_data, file_path):
        with open(file_path, 'w', newline='') as out:
            csv_out = csv.writer(out)
            csv_out.writerow(["Start", "End", "Activity", "Sensor ID"])
            csv_out.writerows(label_data)

    def export(self):
        labels = self.get_labels()
        file_path = self.prompt_save_location()

        self.save_to_csv(labels, file_path)
