from typing import Tuple, List

import pytz
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox

from controllers.project_controller import ProjectController
from controllers.sensor_controller import SensorController
from database.models import Subject, Sensor, SubjectMapping
from gui.designer.subject_sensor_map import Ui_Dialog
from gui.dialogs.edit_subject_mapping_dialog import EditSubjectMappingDialog
from gui.dialogs.new_subject_mapping_dialog import NewSubjectMappingDialog


class SubjectMappingDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, project_controller: ProjectController, sensor_controller: SensorController):
        super().__init__()
        self.setupUi(self)
        self.project_controller = project_controller
        self.sensor_controller = sensor_controller
        self.project_timezone = pytz.timezone(self.project_controller.get_setting('timezone'))

        self.subjects = Subject.select()
        self.subjects_dict = dict((subject.id, subject.name) for subject in self.subjects)

        self.sensors = Sensor.select()
        self.sensors_dict = dict((sensor.id, sensor.name) for sensor in self.sensors)

        self.subject_mappings = []
        self.column_names = ["ID", "Subject", "Sensor", "Start date", "End date"]

        self.create_table()

        self.pushButton_add_map.clicked.connect(self.open_new_map_dialog)
        self.pushButton_edit_map.clicked.connect(self.open_edit_mapping_dialog)
        self.pushButton_remove_map.clicked.connect(self.open_delete_subject_mapping_msg)

    def create_table(self):
        self.tableWidget.blockSignals(True)

        self.subject_mappings = list(SubjectMapping.select())

        self.tableWidget.setColumnCount(len(self.column_names))
        self.tableWidget.setRowCount(len(self.subject_mappings))
        self.tableWidget.setHorizontalHeaderLabels(self.column_names)

        for i, mapping in enumerate(self.subject_mappings):
            start_dt = pytz.utc.localize(mapping.start_datetime).astimezone(self.project_timezone)\
                .strftime('%Y-%m-%d %H:%M:%S')
            end_dt = pytz.utc.localize(mapping.end_datetime).astimezone(self.project_timezone) \
                .strftime('%Y-%m-%d %H:%M:%S')

            self.tableWidget.setItem(i, 0, QTableWidgetItem(mapping.id))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(mapping.subject.name))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(mapping.sensor.name))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(start_dt))
            self.tableWidget.setItem(i, 4, QTableWidgetItem(end_dt))

        # Hide the ID column
        self.tableWidget.hideColumn(0)

        self.tableWidget.blockSignals(False)

    def clear_table(self):
        self.tableWidget.blockSignals(True)
        self.tableWidget.clear()
        self.tableWidget.blockSignals(False)

    def open_new_map_dialog(self):
        dialog = NewSubjectMappingDialog(self.sensor_controller, self.subjects_dict, self.sensors_dict, self.project_timezone)
        dialog.exec()
        dialog.show()

        if dialog.new_map_added:
            self.clear_table()
            self.create_table()

    def open_edit_mapping_dialog(self):
        indices = self.tableWidget.selectionModel().selectedRows()

        if len(indices) > 0:
            row = indices[0].row()
            mapping = self.subject_mappings[row]

            dialog = EditSubjectMappingDialog(
                self.sensor_controller, self.subjects_dict, self.sensors_dict, mapping, self.project_timezone
            )
            dialog.exec()
            dialog.show()

            if dialog.value_changed:
                self.clear_table()
                self.create_table()

    def open_delete_subject_mapping_msg(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText("Are you sure you want to remove the selected mappings?")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        action = msg.exec()

        if action == QMessageBox.Ok:
            self.delete_subject_mapping()

    def delete_subject_mapping(self):
        indices = self.tableWidget.selectionModel().selectedRows()

        for index in indices:
            row = index.row()
            subject_mapping = self.subject_mappings[row]
            deleted = self.sensor_controller.delete_subject_mapping(subject_mapping)

            if deleted:
                self.subject_mappings.pop(row)
                self.tableWidget.removeRow(row)
