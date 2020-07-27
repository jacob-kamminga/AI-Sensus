from PyQt5.QtWidgets import QDialog

from constants import SENSOR_ID_ROW, SENSOR_ID_COLUMN, SENSOR_ID_REGEX
from gui.designer.new_sensor_model_sensor_id import Ui_Dialog
from gui.dialogs.new_sensor_model_headers import SensorModelHeadersDialog
from project_settings import ProjectSettings


class SensorModelIdDialog(QDialog, Ui_Dialog):

    def __init__(self, settings: ProjectSettings, model: {}, model_id=None, parent=None):
        super().__init__()
        self.setupUi(self)
        self.settings = settings
        self.parent = parent
        self.model_id = model_id

        self.model = model
        self.fill_existing_data()

        self.pushButton_previous.pressed.connect(self.open_previous_dialog)
        self.pushButton_next.pressed.connect(self.open_headers_dialog)

    def fill_existing_data(self):
        if self.model[SENSOR_ID_ROW] is not None and self.model[SENSOR_ID_ROW] != -1:
            self.spinBox_row.setValue(self.model[SENSOR_ID_ROW])

        if self.model[SENSOR_ID_COLUMN] is not None and self.model[SENSOR_ID_COLUMN] != -1:
            self.checkBox_column.setChecked(True)
            self.spinBox_column.setValue(self.model[SENSOR_ID_COLUMN])

        if self.model[SENSOR_ID_REGEX] is not None and self.model[SENSOR_ID_REGEX] != '':
            self.checkBox_regex.setChecked(True)
            self.lineEdit_regex.setText(self.model[SENSOR_ID_REGEX])

    def open_headers_dialog(self):
        self.model[SENSOR_ID_ROW] = self.spinBox_row.value()
        self.model[SENSOR_ID_COLUMN] = self.spinBox_column.value() if self.checkBox_column.isChecked() else None
        self.model[SENSOR_ID_REGEX] = self.lineEdit_regex.text() if self.checkBox_regex.isChecked() else None

        dialog = SensorModelHeadersDialog(self.settings, self.model, self.model_id, self.parent)
        self.close()
        dialog.exec()

    def open_previous_dialog(self):
        from gui.dialogs.new_sensor_model_time import SensorModelTimeDialog
        dialog = SensorModelTimeDialog(self.settings, self.model, self.model_id, self.parent)
        self.close()
        dialog.exec()