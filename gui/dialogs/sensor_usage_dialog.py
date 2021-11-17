from typing import Tuple, List

import pytz
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox

from controllers.project_controller import ProjectController
from controllers.sensor_controller import SensorController
from database.models import Subject, Sensor, SensorUsage
from gui.designer.subject_sensor_map import Ui_Dialog
from gui.dialogs.edit_sensor_usage_dialog import EditSensorUsageDialog
from gui.dialogs.new_sensor_usage_dialog import NewSensorUsageDialog


class SensorUsageDialog(QtWidgets.QDialog, Ui_Dialog):

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

        self.sensor_usages = []
        self.column_names = ["ID", "Subject", "Sensor", "Start date", "End date"]

        self.create_table()

        self.pushButton_add_map.clicked.connect(self.open_new_map_dialog)
        self.pushButton_edit_map.clicked.connect(self.open_edit_usage_dialog)
        self.pushButton_remove_map.clicked.connect(self.open_delete_sensor_usage_msg)

    def create_table(self):
        self.tableWidget.blockSignals(True)

        self.sensor_usages = list(SensorUsage.select())

        self.tableWidget.setColumnCount(len(self.column_names))
        self.tableWidget.setRowCount(len(self.sensor_usages))
        self.tableWidget.setHorizontalHeaderLabels(self.column_names)

        for i, usage in enumerate(self.sensor_usages):
            start_dt = pytz.utc.localize(usage.on_click_datetime).astimezone(self.project_timezone)\
                .strftime('%Y-%m-%d %H:%M:%S')
            end_dt = pytz.utc.localize(usage.end_datetime).astimezone(self.project_timezone) \
                .strftime('%Y-%m-%d %H:%M:%S')

            self.tableWidget.setItem(i, 0, QTableWidgetItem(usage.id))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(usage.subject.name))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(usage.sensor.name))
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
        dialog = NewSensorUsageDialog(self.sensor_controller, self.subjects_dict, self.sensors_dict, self.project_timezone)
        dialog.exec()
        dialog.show()

        if dialog.new_map_added:
            self.clear_table()
            self.create_table()

    def open_edit_usage_dialog(self):
        indices = self.tableWidget.selectionModel().selectedRows()

        if len(indices) > 0:
            row = indices[0].row()
            usage = self.sensor_usages[row]

            dialog = EditSensorUsageDialog(
                self.sensor_controller, self.subjects_dict, self.sensors_dict, usage, self.project_timezone
            )
            dialog.exec()
            dialog.show()

            if dialog.value_changed:
                self.clear_table()
                self.create_table()

    def open_delete_sensor_usage_msg(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText("Are you sure you want to remove the selected mappings?")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        action = msg.exec()

        if action == QMessageBox.Ok:
            self.delete_sensor_usage()

    def delete_sensor_usage(self):
        indices = self.tableWidget.selectionModel().selectedRows()

        for index in indices:
            row = index.row()
            sensor_usage = self.sensor_usages[row]
            deleted = self.sensor_controller.delete_sensor_usage(sensor_usage)

            if deleted:
                self.sensor_usages.pop(row)
                self.tableWidget.removeRow(row)
