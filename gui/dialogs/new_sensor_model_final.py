from PyQt5.QtWidgets import QDialog, QMessageBox

from constants import *
from database.sensor_model_manager import SensorModelManager
from gui.designer.new_sensor_model_final import Ui_Dialog
from project_settings import ProjectSettingsDialog


class SensorModelFinalDialog(QDialog, Ui_Dialog):

    def __init__(self, settings: ProjectSettingsDialog, model: {} = None, model_id=None, test_file=None, parent=None):
        super().__init__()
        self.setupUi(self)
        self.settings = settings
        self.model_id = model_id
        self.test_file = test_file
        self.parent = parent
        self.sensor_model_manager = SensorModelManager(self.settings)

        if model is not None:
            self.model = model

            # Hide edit/remove button
            self.pushButton_edit.hide()
            self.pushButton_remove.hide()
        elif model_id is not None:
            self.model = self.get_model_from_db()

            # Hide previous/save buttons
            self.pushButton_previous.hide()
            self.pushButton_save.hide()

        self.init()

        self.pushButton_previous.pressed.connect(self.previous)
        self.pushButton_save.pressed.connect(self.save)
        self.pushButton_edit.pressed.connect(self.edit)
        self.pushButton_remove.pressed.connect(self.remove_warning)

    def init(self):
        self.label_name.setText(str(self.model[MODEL_NAME]))

        if self.model[DATE_ROW] != -1:
            self.label_date_row.setText(str(self.model[DATE_ROW] + 1))

        if self.model[TIME_ROW] != -1:
            self.label_time_row.setText(str(self.model[TIME_ROW] + 1))

        self.label_id_row.setText(str(self.model[SENSOR_ID_ROW] + 1))

        if self.model[SENSOR_ID_COLUMN] != -1:
            self.label_id_column.setText(str(self.model[SENSOR_ID_COLUMN] + 1))

        self.label_id_regex.setText(str(self.model[SENSOR_ID_REGEX]))
        self.label_col_names_row.setText(str(self.model[COL_NAMES_ROW] + 1))
        self.label_comment_style.setText(str(self.model[COMMENT_STYLE]))

    def get_model_from_db(self):
        from database.sensor_model_manager import SensorModelManager
        sensor_model_manager = SensorModelManager(self.settings)
        existing_model = sensor_model_manager.get_model_by_id(self.model_id)

        return {
            MODEL_NAME: existing_model.name,

            DATE_ROW: existing_model.date_row,
            TIME_ROW: existing_model.time_row,
            TIMESTAMP_COLUMN: existing_model.timestamp_column,
            RELATIVE_ABSOLUTE: existing_model.relative_absolute,
            TIMESTAMP_UNIT: existing_model.timestamp_unit,
            FORMAT_STRING: existing_model.format_string,

            SENSOR_ID_ROW: existing_model.sensor_id_row,
            SENSOR_ID_COLUMN: existing_model.sensor_id_col,
            SENSOR_ID_REGEX: existing_model.sensor_id_regex,

            COL_NAMES_ROW: existing_model.col_names_row,

            COMMENT_STYLE: existing_model.comment_style
        }

    def convert_none_type(self):
        # Convert None to other types
        self.model[SENSOR_ID_COLUMN] = self.model[SENSOR_ID_COLUMN] \
            if self.model[SENSOR_ID_COLUMN] is not None \
            else -1
        self.model[SENSOR_ID_REGEX] = self.model[SENSOR_ID_REGEX] \
            if self.model[SENSOR_ID_REGEX] is not None \
            else ""

    def save(self):
        self.convert_none_type()

        if self.model_id is not None:
            self.sensor_model_manager.update_sensor_model(
                self.model_id,
                self.model[MODEL_NAME],
                self.model[DATE_ROW],
                self.model[TIME_ROW],
                self.model[TIMESTAMP_COLUMN],
                self.model[RELATIVE_ABSOLUTE],
                self.model[TIMESTAMP_UNIT],
                self.model[FORMAT_STRING],
                self.model[SENSOR_ID_ROW],
                self.model[SENSOR_ID_COLUMN],
                self.model[SENSOR_ID_REGEX],
                self.model[COL_NAMES_ROW],
                self.model[COMMENT_STYLE]
            )
        else:
            self.sensor_model_manager.insert_sensor_model(
                self.model[MODEL_NAME],
                self.model[DATE_ROW],
                self.model[TIME_ROW],
                self.model[TIMESTAMP_COLUMN],
                self.model[RELATIVE_ABSOLUTE],
                self.model[TIMESTAMP_UNIT],
                self.model[FORMAT_STRING],
                self.model[SENSOR_ID_ROW],
                self.model[SENSOR_ID_COLUMN],
                self.model[SENSOR_ID_REGEX],
                self.model[COL_NAMES_ROW],
                self.model[COMMENT_STYLE]
            )

        self.close()

        if self.parent is not None:
            self.parent.init()

    def previous(self):
        from gui.dialogs.new_sensor_model_id import SensorModelIdDialog

        dialog = SensorModelIdDialog(
            self.settings,
            self.model,
            model_id=self.model_id,
            test_file=self.test_file,
            parent=self.parent
        )
        self.close()
        dialog.exec()

    def edit(self):
        from gui.dialogs.new_sensor_model_name import SensorModelNameDialog

        dialog = SensorModelNameDialog(self.settings, model=self.model, model_id=self.model_id, test_file=self.test_file, parent=self.parent)
        self.close()
        dialog.exec()

    def remove_warning(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Are you sure you want to delete this model?")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.buttonClicked.connect(self.remove)
        msg.exec()

    def remove(self):
        from database.sensor_model_manager import SensorModelManager

        sensor_model_manager = SensorModelManager(self.settings)
        sensor_model_manager.delete_sensor_model_by_id(self.model_id)

        self.close()

        if self.parent is not None:
            # Refresh list
            self.parent.init()
