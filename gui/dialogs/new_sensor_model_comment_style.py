from PyQt5.QtWidgets import QDialog, QErrorMessage

from constants import COMMENT_STYLE
from gui.designer.new_sensor_model_comment_style import Ui_Dialog
from gui.dialogs.new_sensor_model_final import SensorModelFinalDialog
from project_settings import ProjectSettingsDialog


class SensorModelCommentStyleDialog(QDialog, Ui_Dialog):

    def __init__(self, settings: ProjectSettingsDialog, model: {}, model_id=None, test_file=None, parent=None):
        super().__init__()
        self.setupUi(self)
        self.settings = settings
        self.model_id = model_id
        self.test_file = test_file
        self.parent = parent

        self.model = model
        self.fill_existing_data()

        self.pushButton_next.pressed.connect(self.open_next_dialog)
        self.pushButton_previous.pressed.connect(self.open_previous_dialog)
        self.checkBox_enabled.stateChanged.connect(self.toggle_line_edit_style)

    def fill_existing_data(self):
        if self.model[COMMENT_STYLE] is not None and self.model[COMMENT_STYLE] != '':
            self.lineEdit_style.setEnabled(True)
            self.lineEdit_style.setText(self.model[COMMENT_STYLE])
            self.checkBox_enabled.setChecked(True)

    def open_next_dialog(self):
        if self.checkBox_enabled.isChecked():
            comment_style = self.lineEdit_style.text()

            if comment_style != '':
                self.model[COMMENT_STYLE] = comment_style
                dialog = SensorModelFinalDialog(
                    self.settings,
                    self.model,
                    model_id=self.model_id,
                    test_file=self.test_file,
                    parent=self.parent
                )
                self.close()
                dialog.exec()
            else:
                error_dialog = QErrorMessage()
                error_dialog.setModal(True)
                error_dialog.showMessage('Comment style cannot be empty if it is enabled.')
                error_dialog.exec()
        else:
            self.model[COMMENT_STYLE] = ''
            dialog = SensorModelFinalDialog(
                self.settings,
                self.model,
                model_id=self.model_id,
                test_file=self.test_file,
                parent=self.parent
            )
            self.close()
            dialog.exec()

    def open_previous_dialog(self):
        from gui.dialogs.new_sensor_model_col_names import SensorModelColumnNamesDialog
        dialog = SensorModelColumnNamesDialog(
            self.settings,
            self.model,
            model_id=self.model_id,
            test_file=self.test_file,
            parent=self.parent
        )
        self.close()
        dialog.exec()

    def toggle_line_edit_style(self):
        self.lineEdit_style.setEnabled(self.checkBox_enabled.isChecked())
        if not self.checkBox_enabled.isChecked():
            self.lineEdit_style.clear()
