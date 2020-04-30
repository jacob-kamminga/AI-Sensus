from typing import Tuple, List

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox

from database.db_sensor import SensorManager
from database.db_subject import SubjectManager
from database.db_subject_sensor_map import SubjectSensorMapManager
from gui.designer_subject_sensor_map import Ui_Dialog
from gui.dialog_new_subject_sensor_map import NewSubjectSensorMapDialog

INDEX_MAP_ID = 0
INDEX_MAP_SUBJECT = 1
INDEX_MAP_SENSOR = 2
INDEX_MAP_START = 3
INDEX_MAP_END = 4


class SubjectSensorMapDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, project_name: str):
        super().__init__()
        self.setupUi(self)

        self.project_name = project_name
        self.subject_manager = SubjectManager(project_name)
        self.sensor_manager = SensorManager(project_name)
        self.map_manager = SubjectSensorMapManager(project_name)

        self.all_subjects = self.subject_manager.get_all_subjects()
        self.subjects_dict = dict((id_, name) for id_, name, _, _, _ in self.all_subjects)

        self.all_sensors = self.sensor_manager.get_all_sensors()
        self.sensors_dict = dict((id_, name) for id_, name in self.all_sensors)

        self.maps: List[Tuple[str]] = []
        self.column_names = ["ID", "Subject", "Sensor", "Start date", "End date"]

        self.create_table()

        self.pushButton_add_map.clicked.connect(self.open_new_map_dialog)
        self.pushButton_remove_map.clicked.connect(self.open_remove_map_msg)

    def create_table(self):
        self.tableWidget.blockSignals(True)

        self.maps = self.map_manager.get_all_maps()

        self.tableWidget.setColumnCount(len(self.column_names))
        self.tableWidget.setRowCount(len(self.maps))
        self.tableWidget.setHorizontalHeaderLabels(self.column_names)

        for i, row in enumerate(self.maps):
            id_ = row[INDEX_MAP_ID]
            subject_id = row[INDEX_MAP_SUBJECT]
            sensor_id = row[INDEX_MAP_SENSOR]
            start_dt = row[INDEX_MAP_START]
            end_dt = row[INDEX_MAP_END]

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
        dialog.exec_()
        dialog.show()

        if dialog.new_map_added:
            self.clear_table()
            self.create_table()

    def open_remove_map_msg(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText("Are you sure you want to remove the selected mappings?")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.accepted.connect(self.remove_map)
        msg.exec_()

    def remove_map(self):
        indexes = self.tableWidget.selectionModel().selectedRows()

        for index in indexes:
            row = index.row()
            id_ = self.maps[row][INDEX_MAP_ID]
            self.map_manager.delete_map(int(id_))
            self.maps.pop(row)
            self.tableWidget.removeRow(row)
