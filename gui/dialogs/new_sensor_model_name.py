from PyQt5.QtWidgets import QDialog, QErrorMessage

from constants import *
from gui.designer.new_sensor_model_name import Ui_Dialog
from gui.dialogs.new_sensor_model_date import SensorModelDateDialog
from project_settings import ProjectSettings


class SensorModelNameDialog(QDialog, Ui_Dialog):

    def __init__(self, settings: ProjectSettings, model=None, model_id=None, parent=None):
        super().__init__()
        self.setupUi(self)
        self.settings = settings
        self.model_id = model_id
        self.parent = parent

        if model is not None:
            self.model = model
            self.fill_existing_data()
        elif self.model_id is not None:
            from database.sensor_model_manager import SensorModelManager
            sensor_model_manager = SensorModelManager(self.settings)
            existing_model = sensor_model_manager.get_model_by_id(model_id)

            self.model = {
                MODEL_NAME: existing_model[MODEL_NAME],

                DATE_FORMAT: existing_model[DATE_FORMAT],
                DATE_ROW: existing_model[DATE_ROW],
                DATE_COLUMN: existing_model[DATE_COLUMN],
                DATE_REGEX: existing_model[DATE_REGEX],

                TIME_FORMAT: existing_model[TIME_FORMAT],
                TIME_ROW: existing_model[TIME_ROW],
                TIME_COLUMN: existing_model[TIME_COLUMN],
                TIME_REGEX: existing_model[TIME_REGEX],

                SENSOR_ID_ROW: existing_model[SENSOR_ID_ROW],
                SENSOR_ID_COLUMN: existing_model[SENSOR_ID_COLUMN],
                SENSOR_ID_REGEX: existing_model[SENSOR_ID_REGEX],

                HEADERS_ROW: existing_model[HEADERS_ROW],

                COMMENT_STYLE: existing_model[COMMENT_STYLE]
            }
            self.fill_existing_data()
        else:
            self.model = {
                MODEL_NAME: '',

                DATE_FORMAT: '',
                DATE_ROW: -1,
                DATE_COLUMN: -1,
                DATE_REGEX: '',

                TIME_FORMAT: '',
                TIME_ROW: -1,
                TIME_COLUMN: -1,
                TIME_REGEX: '',

                SENSOR_ID_ROW: -1,
                SENSOR_ID_COLUMN: -1,
                SENSOR_ID_REGEX: '',

                HEADERS_ROW: -1,

                COMMENT_STYLE: ''
            }

        self.pushButton_next.pressed.connect(self.open_date_dialog)

    def fill_existing_data(self):
        self.lineEdit_model_name.setText(self.model[MODEL_NAME])

    def open_date_dialog(self):
        model_name = self.lineEdit_model_name.text()

        if model_name != '':
            self.model[MODEL_NAME] = model_name
            dialog = SensorModelDateDialog(self.settings, self.model, self.model_id, self.parent)
            self.close()
            dialog.exec()
        else:
            error_dialog = QErrorMessage()
            error_dialog.setModal(True)
            error_dialog.showMessage("Project name cannot be empty.")
            error_dialog.exec()
