from PyQt5.QtWidgets import QDialog

from constants import HEADERS_ROW
from gui.designer.new_sensor_model_headers import Ui_Dialog
from gui.dialogs.new_sensor_model_comment_style import SensorModelCommentStyleDialog
from project_settings import ProjectSettings


class SensorModelHeadersDialog(QDialog, Ui_Dialog):

    def __init__(self, settings: ProjectSettings, model: {}, model_id=None, parent=None):
        super().__init__()
        self.setupUi(self)
        self.settings = settings
        self.parent = parent
        self.model_id = model_id

        self.model = model
        self.fill_existing_data()

        self.pushButton_next.pressed.connect(self.open_final_dialog)

    def fill_existing_data(self):
        if self.model[HEADERS_ROW] is not None and self.model[HEADERS_ROW] != -1:
            self.spinBox_row.setValue(self.model[HEADERS_ROW])

    def open_final_dialog(self):
        self.model[HEADERS_ROW] = self.spinBox_row.value()

        dialog = SensorModelCommentStyleDialog(self.settings, self.model, self.model_id, self.parent)
        self.close()
        dialog.exec()

    def open_previous_dialog(self):
        from gui.dialogs.new_sensor_model_id import SensorModelIdDialog
        dialog = SensorModelIdDialog(self.settings, self.model, self.model_id, self.parent)
        self.close()
        dialog.exec()
