from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

from database.sensor_manager import SensorManager
from gui.designer.sensor import Ui_Dialog
from gui.dialogs.edit_sensor import EditSensorDialog
from project_settings import ProjectSettingsDialog

INDEX_SENSOR_ID = 0
INDEX_SENSOR_NAME = 1


class SensorDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, settings: ProjectSettingsDialog):
        super().__init__()
        self.setupUi(self)

        self.sensor_manager = SensorManager(settings)

        self.all_sensors = self.sensor_manager.get_all_sensors()
        self.sensors_dict = dict((id_, name) for id_, name in self.all_sensors)

        self.create_table()

        self.listWidget.itemDoubleClicked.connect(self.open_edit_sensor_dialog)
        self.pushButton_edit_sensor.clicked.connect(self.open_edit_sensor_dialog)
        self.pushButton_remove_sensor.clicked.connect(self.open_remove_sensor_msg)

    def create_table(self):
        self.listWidget.blockSignals(True)
        self.all_sensors = self.sensor_manager.get_all_sensors()
        self.sensors_dict = dict((id_, name) for id_, name in self.all_sensors)
        self.listWidget.addItems(self.sensors_dict.values())
        self.listWidget.blockSignals(False)

    def clear_table(self):
        self.listWidget.blockSignals(True)
        self.listWidget.clear()
        self.listWidget.blockSignals(False)

    def open_edit_sensor_dialog(self):
        indices = self.listWidget.selectionModel().selectedRows()

        if len(indices) > 0:
            # Get the sensor ID and name of the selected row
            row = indices[0].row()
            id_ = int(self.all_sensors[row][INDEX_SENSOR_ID])
            name = self.all_sensors[row][INDEX_SENSOR_NAME]

            dialog = EditSensorDialog(self.sensor_manager, id_, name)

            dialog.exec()

            if dialog.sensor_edited:
                self.clear_table()
                self.create_table()

    def open_remove_sensor_msg(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText("Are you sure you want to remove the selected sensor?")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        action = msg.exec()

        if action == QMessageBox.Ok:
            self.remove_sensor()

    def remove_sensor(self):
        indices = self.listWidget.selectionModel().selectedRows()

        if len(indices) > 0:
            row = indices[0].row()
            id_ = int(self.all_sensors[row][INDEX_SENSOR_ID])
            self.sensor_manager.delete_sensor_by_id(id_)
            self.all_sensors.pop(row)
            self.listWidget.takeItem(row)
