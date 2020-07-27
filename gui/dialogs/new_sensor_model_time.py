from PyQt5 import QtWidgets

from constants import TIME_FORMAT, TIME_ROW, TIME_COLUMN, TIME_REGEX
from gui.designer.new_sensor_model_time import Ui_Dialog
from gui.dialogs.new_sensor_model_id import SensorModelIdDialog
from project_settings import ProjectSettings


class SensorModelTimeDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, settings: ProjectSettings, model: {}, model_id=None, parent=None):
        super().__init__()
        self.setupUi(self)
        self.settings = settings
        self.parent = parent
        self.model_id = model_id

        self.model = model
        self.fill_existing_data()

        self.pushButton_previous.pressed.connect(self.open_previous_dialog)
        self.pushButton_next.pressed.connect(self.open_sensor_id_dialog)

    def fill_existing_data(self):
        if self.model[TIME_FORMAT] is not None and self.model[TIME_FORMAT] != '':
            self.lineEdit_format.setText(self.model[TIME_FORMAT])

        if self.model[TIME_ROW] is not None and self.model[TIME_ROW] != -1:
            self.spinBox_row.setValue(self.model[TIME_ROW])

        if self.model[TIME_COLUMN] is not None and self.model[TIME_COLUMN] != -1:
            self.checkBox_column.setChecked(True)
            self.spinBox_column.setValue(self.model[TIME_COLUMN])

        if self.model[TIME_REGEX] is not None and self.model[TIME_REGEX] != '':
            self.checkBox_regex.setChecked(True)
            self.lineEdit_regex.setText(self.model[TIME_REGEX])

    def open_sensor_id_dialog(self):
        self.model[TIME_FORMAT] = self.lineEdit_format.text()
        self.model[TIME_ROW] = self.spinBox_row.value()
        self.model[TIME_COLUMN] = self.spinBox_column.value() if self.checkBox_column.isChecked() else None
        self.model[TIME_REGEX] = self.lineEdit_regex.text() if self.checkBox_regex.isChecked() else None

        if self.model[TIME_FORMAT]:
            dialog = SensorModelIdDialog(self.settings, self.model, self.model_id, self.parent)
            self.close()
            dialog.exec()
        else:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.setModal(True)
            error_dialog.showMessage('Time format cannot be empty.')
            error_dialog.exec()

    def open_previous_dialog(self):
        from gui.dialogs.new_sensor_model_date import SensorModelDateDialog
        dialog = SensorModelDateDialog(self.settings, self.model, self.model_id, self.parent)
        self.close()
        dialog.exec()
