from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox

from database.db_sensor import SensorManager
from gui.designer_sensor import Ui_Dialog
from gui.dialog_edit_sensor import EditSensorDialog

INDEX_SENSOR_ID = 0
INDEX_SENSOR_NAME = 1


class SensorDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, project_name: str):
        super().__init__()
        self.setupUi(self)

        self.project_name = project_name
        self.sensor_manager = SensorManager(project_name)

        self.all_sensors = self.sensor_manager.get_all_sensors()
        self.sensors_dict = dict((id_, name) for id_, name in self.all_sensors)

        self.create_table()

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
            row = indices[0].row()
            id_ = int(self.all_sensors[row][INDEX_SENSOR_ID])

            dialog = EditSensorDialog(self.sensor_manager,
                                      self.sensors_dict,
                                      id_)

            dialog.exec_()
            dialog.show()

            if dialog.sensor_edited:
                self.clear_table()
                self.create_table()

    def open_remove_sensor_msg(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText("Are you sure you want to remove the selected sensor?")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        action = msg.exec_()

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
