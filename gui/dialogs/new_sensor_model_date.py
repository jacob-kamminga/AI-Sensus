from PyQt5 import QtWidgets

from constants import DATE_FORMAT, DATE_ROW, DATE_COLUMN, DATE_REGEX
from gui.designer.new_sensor_model_date import Ui_Dialog
from gui.dialogs.new_sensor_model_time import SensorModelTimeDialog
from project_settings import ProjectSettings


class SensorModelDateDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, settings: ProjectSettings, model: {}, model_id=None, parent=None):
        super().__init__()
        self.setupUi(self)
        self.settings = settings
        self.parent = parent
        self.model_id = model_id

        self.model = model
        self.fill_existing_data()

        self.pushButton_previous.pressed.connect(self.open_previous_dialog)
        self.pushButton_next.pressed.connect(self.open_time_dialog)

    def fill_existing_data(self):
        if self.model[DATE_FORMAT] is not None and self.model[DATE_FORMAT] != '':
            self.lineEdit_format.setText(self.model[DATE_FORMAT])

        if self.model[DATE_ROW] is not None and self.model[DATE_ROW] != -1:
            self.spinBox_row.setValue(self.model[DATE_ROW])

        if self.model[DATE_COLUMN] is not None and self.model[DATE_COLUMN] != -1:
            self.checkBox_column.setChecked(True)
            self.spinBox_column.setValue(self.model[DATE_COLUMN])

        if self.model[DATE_REGEX] is not None and self.model[DATE_REGEX] != '':
            self.checkBox_regex.setChecked(True)
            self.lineEdit_regex.setText(self.model[DATE_REGEX])

    def open_time_dialog(self):
        self.model[DATE_FORMAT] = self.lineEdit_format.text()
        self.model[DATE_ROW] = self.spinBox_row.value()
        self.model[DATE_COLUMN] = self.spinBox_column.value() if self.checkBox_column.isChecked() else None
        self.model[DATE_REGEX] = self.lineEdit_regex.text() if self.checkBox_regex.isChecked() else None

        if self.model[DATE_FORMAT]:
            dialog = SensorModelTimeDialog(self.settings, self.model, self.model_id, self.parent)
            self.close()
            dialog.exec()
        else:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.setModal(True)
            error_dialog.showMessage('Date format cannot be empty.')
            error_dialog.exec()

    def open_previous_dialog(self):
        from gui.dialogs.new_sensor_model_name import SensorModelNameDialog
        dialog = SensorModelNameDialog(self.settings, self.model, self.model_id, self.parent)
        self.close()
        dialog.exec()
