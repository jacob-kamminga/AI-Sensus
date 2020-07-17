from PyQt5.QtWidgets import QDialog

from constants import *
from database.sensor_model_manager import SensorModelManager
from gui.designer.new_sensor_model_final_new import Ui_Dialog
from project_settings import ProjectSettings


class SensorModelFinalDialog(QDialog, Ui_Dialog):

    def __init__(self, settings: ProjectSettings, model: {}, model_id=None, parent=None):
        super().__init__()
        self.setupUi(self)
        self.settings = settings
        self.parent = parent
        self.model_id = model_id
        self.sensor_model_manager = SensorModelManager(self.settings)

        self.model = model
        self.init()

        self.pushButton_previous.pressed.connect(self.open_previous_dialog)
        self.pushButton_save.pressed.connect(self.save_to_database)

    def init(self):
        self.label_name.setText(str(self.model[MODEL_NAME]))
        self.label_date_format.setText(str(self.model[DATE_FORMAT]))
        self.label_date_row.setText(str(self.model[DATE_ROW]))
        self.label_date_column.setText(str(self.model[DATE_COLUMN]))
        self.label_date_regex.setText(str(self.model[DATE_REGEX]))
        self.label_time_format.setText(str(self.model[TIME_FORMAT]))
        self.label_time_row.setText(str(self.model[TIME_ROW]))
        self.label_time_column.setText(str(self.model[TIME_COLUMN]))
        self.label_time_regex.setText(str(self.model[TIME_REGEX]))
        self.label_id_row.setText(str(self.model[SENSOR_ID_ROW]))
        self.label_id_column.setText(str(self.model[SENSOR_ID_COLUMN]))
        self.label_id_regex.setText(str(self.model[SENSOR_ID_REGEX]))
        self.label_headers_row.setText(str(self.model[HEADERS_ROW]))
        self.label_comment_style.setText(str(self.model[COMMENT_STYLE]))

    def convert_none_type(self):
        # Convert None to other types
        self.model[DATE_COLUMN] = self.model[DATE_COLUMN] \
            if self.model[DATE_COLUMN] is not None \
            else -1
        self.model[DATE_REGEX] = self.model[DATE_REGEX] \
            if self.model[DATE_REGEX] is not None \
            else ""
        self.model[TIME_COLUMN] = self.model[TIME_COLUMN] \
            if self.model[TIME_COLUMN] is not None \
            else -1
        self.model[TIME_REGEX] = self.model[TIME_REGEX] \
            if self.model[TIME_REGEX] is not None \
            else ""
        self.model[SENSOR_ID_COLUMN] = self.model[SENSOR_ID_COLUMN] \
            if self.model[SENSOR_ID_COLUMN] is not None \
            else -1
        self.model[SENSOR_ID_REGEX] = self.model[SENSOR_ID_REGEX] \
            if self.model[SENSOR_ID_REGEX] is not None \
            else ""

    def save_to_database(self):
        self.convert_none_type()

        if self.model_id is not None:
            self.sensor_model_manager.update_sensor_model(
                self.model_id,
                self.model[MODEL_NAME],
                self.model[DATE_FORMAT],
                self.model[DATE_ROW],
                self.model[DATE_COLUMN],
                self.model[DATE_REGEX],
                self.model[TIME_FORMAT],
                self.model[TIME_ROW],
                self.model[TIME_COLUMN],
                self.model[TIME_REGEX],
                self.model[SENSOR_ID_ROW],
                self.model[SENSOR_ID_COLUMN],
                self.model[SENSOR_ID_REGEX],
                self.model[HEADERS_ROW],
                self.model[COMMENT_STYLE]
            )
        else:
            self.sensor_model_manager.insert_sensor_model(
                self.model[MODEL_NAME],
                self.model[DATE_FORMAT],
                self.model[DATE_ROW],
                self.model[DATE_COLUMN],
                self.model[DATE_REGEX],
                self.model[TIME_FORMAT],
                self.model[TIME_ROW],
                self.model[TIME_COLUMN],
                self.model[TIME_REGEX],
                self.model[SENSOR_ID_ROW],
                self.model[SENSOR_ID_COLUMN],
                self.model[SENSOR_ID_REGEX],
                self.model[HEADERS_ROW],
                self.model[COMMENT_STYLE]
            )

        self.close()

        if self.parent is not None:
            self.parent.init()

    def open_previous_dialog(self):
        from gui.dialogs.new_sensor_model_id import SensorModelIdDialog
        dialog = SensorModelIdDialog(self.settings, self.model, self.model_id, self.parent)
        self.close()
        dialog.exec()
