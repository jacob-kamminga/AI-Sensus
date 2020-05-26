from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox

from database.db_sensor import SensorManager
from gui.designer_sensor import Ui_Dialog

INDEX_MAP_ID = 0
INDEX_MAP_SUBJECT = 1
INDEX_MAP_SENSOR = 2
INDEX_MAP_START = 3
INDEX_MAP_END = 4


class SensorDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, project_name: str):
        super().__init__()
        self.setupUi(self)

        self.project_name = project_name
        self.sensor_manager = SensorManager(project_name)

        self.all_sensors = self.sensor_manager.get_all_sensors()
        self.sensors_dict = dict((id_, name) for id_, name in self.all_sensors)

        self.create_table()

        # self.pushButton_add_sensor.clicked.connect(self.open_new_map_dialog)
        # self.pushButton_edit_sensor.clicked.connect(self.open_edit_map_dialog)
        # self.pushButton_remove_sensor.clicked.connect(self.open_remove_map_msg)

    def create_table(self):
        self.listWidget.blockSignals(True)
        self.listWidget.addItems(self.sensors_dict.values())
        self.listWidget.blockSignals(False)

    def clear_table(self):
        self.tableWidget.blockSignals(True)
        self.tableWidget.clear()
        self.tableWidget.blockSignals(False)

    # def open_new_map_dialog(self):
    #     dialog = NewSubjectSensorMapDialog(self.map_manager,
    #                                        self.subject_manager,
    #                                        self.sensor_manager,
    #                                        self.subjects_dict,
    #                                        self.sensors_dict)
    #     dialog.exec_()
    #     dialog.show()
    #
    #     if dialog.new_map_added:
    #         self.clear_table()
    #         self.create_table()

    # def open_edit_map_dialog(self):
    #     indices = self.tableWidget.selectionModel().selectedRows()
    #
    #     if len(indices) > 0:
    #         row = indices[0].row()
    #         id_ = int(self.maps[row][INDEX_MAP_ID])
    #
    #         dialog = EditSubjectSensorMapDialog(self.map_manager,
    #                                             self.subject_manager,
    #                                             self.sensor_manager,
    #                                             self.subjects_dict,
    #                                             self.sensors_dict,
    #                                             id_)
    #         dialog.exec_()
    #         dialog.show()
    #
    #         if dialog.map_edited:
    #             self.clear_table()
    #             self.create_table()
    #
    # def open_remove_map_msg(self):
    #     msg = QMessageBox()
    #     msg.setIcon(QMessageBox.Information)
    #
    #     msg.setText("Are you sure you want to remove the selected mappings?")
    #     msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    #     msg.accepted.connect(self.remove_map)
    #     msg.exec_()
    #
    # def remove_map(self):
    #     indices = self.tableWidget.selectionModel().selectedRows()
    #
    #     for index in indices:
    #         row = index.row()
    #         id_ = self.maps[row][INDEX_MAP_ID]
    #         self.map_manager.delete_map(int(id_))
    #         self.maps.pop(row)
    #         self.tableWidget.removeRow(row)
