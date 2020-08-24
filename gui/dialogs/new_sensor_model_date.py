from PyQt5 import QtWidgets

from constants import DATE_ROW, TIME_ROW
from gui.designer.new_sensor_model_date import Ui_Dialog
from gui.dialogs.new_sensor_model_id import SensorModelIdDialog
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
        if self.model[DATE_ROW] is not None and self.model[DATE_ROW] != -1:
            self.spinBox_row.setValue(self.model[DATE_ROW])

        if self.model[TIME_ROW] is not None and self.model[TIME_ROW] != -1:
            self.spinBox_column.setValue(self.model[TIME_ROW])

    def open_time_dialog(self):
        self.model[DATE_ROW] = self.spinBox_date_row.value()
        self.model[TIME_ROW] = self.spinBox_time_row.value()

        dialog = SensorModelIdDialog(self.settings, self.model, self.model_id, self.parent)
        self.close()
        dialog.exec()

    def open_previous_dialog(self):
        from gui.dialogs.new_sensor_model_name import SensorModelNameDialog

        dialog = SensorModelNameDialog(self.settings, self.model, self.model_id, self.parent)
        self.close()
        dialog.exec()
