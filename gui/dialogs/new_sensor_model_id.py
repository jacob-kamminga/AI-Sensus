from PyQt5.QtWidgets import QDialog

from constants import SENSOR_ID_ROW, SENSOR_ID_COLUMN, SENSOR_ID_REGEX
from gui.designer.new_sensor_model_sensor_id import Ui_Dialog
from gui.dialogs.new_sensor_model_col_names import SensorModelColumnNamesDialog
from project_settings import ProjectSettingsDialog


class SensorModelIdDialog(QDialog, Ui_Dialog):

    def __init__(self, settings: ProjectSettingsDialog, model: {}, model_id=None, test_file=None, parent=None):
        super().__init__()
        self.setupUi(self)
        self.settings = settings
        self.model_id = model_id
        self.test_file = test_file
        self.parent = parent

        self.model = model
        self.fill_existing_data()

        self.pushButton_previous.pressed.connect(self.open_previous_dialog)
        self.pushButton_next.pressed.connect(self.open_col_names_dialog)

    def fill_existing_data(self):
        if self.model[SENSOR_ID_ROW] is not None and self.model[SENSOR_ID_ROW] != -1:
            self.spinBox_row.setValue(self.model[SENSOR_ID_ROW] + 1)

        if self.model[SENSOR_ID_COLUMN] is not None and self.model[SENSOR_ID_COLUMN] != -1:
            self.checkBox_column.setChecked(True)
            self.spinBox_column.setValue(self.model[SENSOR_ID_COLUMN] + 1)

        if self.model[SENSOR_ID_REGEX] is not None and self.model[SENSOR_ID_REGEX] != '':
            self.checkBox_regex.setChecked(True)
            self.lineEdit_regex.setText(self.model[SENSOR_ID_REGEX])

    def open_col_names_dialog(self):
        self.model[SENSOR_ID_ROW] = self.spinBox_row.value() - 1
        self.model[SENSOR_ID_COLUMN] = self.spinBox_column.value() - 1 if self.checkBox_column.isChecked() else -1
        self.model[SENSOR_ID_REGEX] = self.lineEdit_regex.text() if self.checkBox_regex.isChecked() else ''

        dialog = SensorModelColumnNamesDialog(
            self.settings,
            self.model,
            model_id=self.model_id,
            test_file=self.test_file,
            parent=self.parent)
        self.close()
        dialog.exec()

    def open_previous_dialog(self):
        from gui.dialogs.new_sensor_model_date import SensorModelDateDialog

        dialog = SensorModelDateDialog(
            self.settings,
            self.model,
            model_id=self.model_id,
            test_file=self.test_file,
            parent=self.parent
        )
        self.close()
        dialog.exec()
