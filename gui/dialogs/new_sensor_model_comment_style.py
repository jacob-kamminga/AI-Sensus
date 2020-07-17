from PyQt5.QtWidgets import QDialog

from constants import COMMENT_STYLE
from gui.designer.new_sensor_model_comment_style import Ui_Dialog
from gui.dialogs.new_sensor_model_final import SensorModelFinalDialog
from project_settings import ProjectSettings


class SensorModelCommentStyleDialog(QDialog, Ui_Dialog):

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
        if self.model[COMMENT_STYLE] is not None and self.model[COMMENT_STYLE] != '':
            self.lineEdit_style.setValue(self.model[COMMENT_STYLE])

    def open_final_dialog(self):
        self.model[COMMENT_STYLE] = self.lineEdit_style.text()

        dialog = SensorModelFinalDialog(self.settings, self.model, self.model_id, self.parent)
        self.close()
        dialog.exec()

    def open_previous_dialog(self):
        from gui.dialogs.new_sensor_model_headers import SensorModelHeadersDialog
        dialog = SensorModelHeadersDialog(self.settings, self.model, self.model_id, self.parent)
        self.close()
        dialog.exec()
