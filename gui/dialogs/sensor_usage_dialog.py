from typing import Tuple, List

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox

from database.models import Subject, Sensor, SensorUsage
from gui.designer.subject_sensor_map import Ui_Dialog
from gui.dialogs.edit_sensor_usage_dialog import EditSensorUsageDialog
from gui.dialogs.new_sensor_usage_dialog import NewSensorUsageDialog


class SensorUsageDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.subjects = Subject.select()
        self.subjects_dict = dict((subject.id, subject.name) for subject in self.subjects)

        self.sensors = Sensor.select()
        self.sensors_dict = dict((sensor.id, sensor.name) for sensor in self.sensors)

        self.usages: List[Tuple[str]] = []
        self.column_names = ["ID", "Subject", "Sensor", "Start date", "End date"]

        self.create_table()

        self.pushButton_add_map.clicked.connect(self.open_new_map_dialog)
        self.pushButton_edit_map.clicked.connect(self.open_edit_map_dialog)
        self.pushButton_remove_map.clicked.connect(self.open_remove_map_msg)

    def create_table(self):
        self.tableWidget.blockSignals(True)

        self.usages = SensorUsage.select()

        self.tableWidget.setColumnCount(len(self.column_names))
        self.tableWidget.setRowCount(len(self.usages))
        self.tableWidget.setHorizontalHeaderLabels(self.column_names)

        for i, usage in enumerate(self.usages):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(usage.id))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(usage.subject.name))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(usage.sensor.name))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(str(usage.start_datetime)))
            self.tableWidget.setItem(i, 4, QTableWidgetItem(str(usage.end_datetime)))

        # Hide the ID column
        self.tableWidget.hideColumn(0)

        self.tableWidget.blockSignals(False)

    def clear_table(self):
        self.tableWidget.blockSignals(True)
        self.tableWidget.clear()
        self.tableWidget.blockSignals(False)

    def open_new_map_dialog(self):
        dialog = NewSensorUsageDialog(self.subjects_dict, self.sensors_dict)
        dialog.exec()
        dialog.show()

        if dialog.new_map_added:
            self.clear_table()
            self.create_table()

    def open_edit_map_dialog(self):
        indices = self.tableWidget.selectionModel().selectedRows()

        if len(indices) > 0:
            row = indices[0].row()
            id_ = int(self.usages[row][0])

            dialog = EditSensorUsageDialog(self.subjects_dict, self.sensors_dict, id_)
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
            id_ = int(self.usages[row][0])
            usage = SensorUsage.get_by_id(id_)
            usage.delete_by_instance()
            self.usages.pop(row)
            self.tableWidget.removeRow(row)
