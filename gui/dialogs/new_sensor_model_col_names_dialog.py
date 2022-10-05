from PyQt5.QtWidgets import QDialog

from constants import COL_NAMES_ROW
from controllers.sensor_controller import SensorController
from gui.designer.new_sensor_model_column_names import Ui_Dialog
from gui.dialogs.new_sensor_model_comment_style_dialog import SensorModelCommentStyleDialog


class SensorModelColumnNamesDialog(QDialog, Ui_Dialog):

    def __init__(self, sensor_controller: SensorController, model: {}, model_id=None, test_file=None, parent=None):
        super().__init__()
        self.setupUi(self)
        self.sensor_controller = sensor_controller
        self.model_id = model_id
        self.test_file = test_file
        self.parent = parent

        self.model = model
        self.fill_existing_data()

        self.pushButton_previous.pressed.connect(self.open_previous_dialog)
        self.pushButton_next.pressed.connect(self.open_next_dialog)

    def fill_existing_data(self):
        if self.model[COL_NAMES_ROW] is not None and self.model[COL_NAMES_ROW] != -1:
            self.spinBox_row.setValue(self.model[COL_NAMES_ROW] + 1)

    def open_next_dialog(self):
        self.model[COL_NAMES_ROW] = self.spinBox_row.value() - 1

        dialog = SensorModelCommentStyleDialog(
            self.sensor_controller,
            self.model,
            model_id=self.model_id,
            test_file=self.test_file,
            parent=self.parent
        )
        self.close()
        dialog.exec()

    def open_previous_dialog(self):
        from gui.dialogs.new_sensor_model_id_dialog import SensorModelIdDialog
        dialog = SensorModelIdDialog(
            self.sensor_controller,
            self.model,
            model_id=self.model_id,
            test_file=self.test_file,
            parent=self.parent
        )
        self.close()
        dialog.exec()
