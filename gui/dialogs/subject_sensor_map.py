from typing import Tuple, List

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox

from database.sensor_manager import SensorManager
from database.subject_manager import SubjectManager
from database.sensor_usage_manager import SensorUsageManager
from gui.designer.subject_sensor_map import Ui_Dialog
from gui.dialogs.edit_subject_sensor_map import EditSubjectSensorMapDialog
from gui.dialogs.new_subject_sensor_map import NewSubjectSensorMapDialog
from project_settings import ProjectSettingsDialog

INDEX_MAP_ID = 0
INDEX_MAP_SUBJECT = 1
INDEX_MAP_SENSOR = 2
INDEX_MAP_START = 3
INDEX_MAP_END = 4


class SubjectSensorMapDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, settings: ProjectSettingsDialog):
        super().__init__()
        self.setupUi(self)

        self.subject_manager = SubjectManager(settings)
        self.sensor_manager = SensorManager(settings)
        self.map_manager = SensorUsageManager(settings)

        self.all_subjects = self.subject_manager.get_all_subjects()
        self.subjects_dict = dict((id_, name) for id_, name, _, _, _ in self.all_subjects)

        self.all_sensors = self.sensor_manager.get_all_sensors()
        self.sensors_dict = dict((id_, name) for id_, name in self.all_sensors)

        self.maps: List[Tuple[str]] = []
        self.column_names = ["ID", "Subject", "Sensor", "Start date", "End date"]

        self.create_table()

        self.pushButton_add_map.clicked.connect(self.open_new_map_dialog)
        self.pushButton_edit_map.clicked.connect(self.open_edit_map_dialog)
        self.pushButton_remove_map.clicked.connect(self.open_remove_map_msg)

    def create_table(self):
        self.tableWidget.blockSignals(True)

        self.maps = self.map_manager.get_all_usages()

        self.tableWidget.setColumnCount(len(self.column_names))
        self.tableWidget.setRowCount(len(self.maps))
        self.tableWidget.setHorizontalHeaderLabels(self.column_names)

        for i, map_ in enumerate(self.maps):
            id_ = map_[INDEX_MAP_ID]
            subject_id = map_[INDEX_MAP_SUBJECT]
            sensor_id = map_[INDEX_MAP_SENSOR]
            start_dt = map_[INDEX_MAP_START]
            end_dt = map_[INDEX_MAP_END]

            self.tableWidget.setItem(i, INDEX_MAP_ID, QTableWidgetItem(str(id_)))
            self.tableWidget.setItem(i, INDEX_MAP_SUBJECT, QTableWidgetItem(self.subjects_dict[subject_id]))
            self.tableWidget.setItem(i, INDEX_MAP_SENSOR, QTableWidgetItem(self.sensors_dict[sensor_id]))
            self.tableWidget.setItem(i, INDEX_MAP_START, QTableWidgetItem(str(start_dt)))
            self.tableWidget.setItem(i, INDEX_MAP_END, QTableWidgetItem(str(end_dt)))

        # Hide the ID column
        self.tableWidget.hideColumn(INDEX_MAP_ID)

        self.tableWidget.blockSignals(False)

    def clear_table(self):
        self.tableWidget.blockSignals(True)
        self.tableWidget.clear()
        self.tableWidget.blockSignals(False)

    def open_new_map_dialog(self):
        dialog = NewSubjectSensorMapDialog(self.map_manager,
                                           self.subject_manager,
                                           self.sensor_manager,
                                           self.subjects_dict,
                                           self.sensors_dict)
        dialog.exec()
        dialog.show()

        if dialog.new_map_added:
            self.clear_table()
            self.create_table()

    def open_edit_map_dialog(self):
        indices = self.tableWidget.selectionModel().selectedRows()

        if len(indices) > 0:
            row = indices[0].row()
            id_ = int(self.maps[row][INDEX_MAP_ID])

            dialog = EditSubjectSensorMapDialog(self.map_manager,
                                                self.subject_manager,
                                                self.sensor_manager,
                                                self.subjects_dict,
                                                self.sensors_dict,
                                                id_)
            dialog.exec()
            dialog.show()

            if dialog.map_edited:
                self.clear_table()
                self.create_table()

    def open_remove_map_msg(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText("Are you sure you want to remove the selected mappings?")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        action = msg.exec()

        if action == QMessageBox.Ok:
            self.remove_map()

    def remove_map(self):
        indices = self.tableWidget.selectionModel().selectedRows()

        for index in indices:
            row = index.row()
            id_ = self.maps[row][INDEX_MAP_ID]
            self.map_manager.delete_usage(int(id_))
            self.maps.pop(row)
            self.tableWidget.removeRow(row)
