from pathlib import Path

from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QDialog, QErrorMessage, QFileDialog

from constants import *
from gui.designer.new_sensor_model_name import Ui_Dialog
from gui.dialogs.new_sensor_model_date import SensorModelDateDialog
from project_settings import ProjectSettings


class SensorModelNameDialog(QDialog, Ui_Dialog):

    def __init__(self, settings: ProjectSettings, model=None, model_id=None, test_file=None, parent=None):
        super().__init__()
        self.setupUi(self)
        self.settings = settings
        self.model_id = model_id
        self.test_file = test_file
        self.parent = parent

        if model is not None:
            # Use the provided model
            self.model = model
            self.fill_existing_data()
        elif self.model_id is not None:
            # Get the saved model from the database and fill existing data
            from database.sensor_model_manager import SensorModelManager
            sensor_model_manager = SensorModelManager(self.settings)
            existing_model = sensor_model_manager.get_model_by_id(model_id)

            self.model = {
                MODEL_NAME: existing_model[MODEL_NAME],

                DATE_ROW: existing_model[DATE_ROW],
                TIME_ROW: existing_model[TIME_ROW],

                SENSOR_ID_ROW: existing_model[SENSOR_ID_ROW],
                SENSOR_ID_COLUMN: existing_model[SENSOR_ID_COLUMN],
                SENSOR_ID_REGEX: existing_model[SENSOR_ID_REGEX],

                HEADERS_ROW: existing_model[HEADERS_ROW],

                COMMENT_STYLE: existing_model[COMMENT_STYLE]
            }
            self.fill_existing_data()
        else:
            # Initialize empty model
            self.model = {
                MODEL_NAME: '',

                DATE_ROW: -1,
                TIME_ROW: -1,

                SENSOR_ID_ROW: -1,
                SENSOR_ID_COLUMN: -1,
                SENSOR_ID_REGEX: '',

                HEADERS_ROW: -1,

                COMMENT_STYLE: ''
            }

        self.pushButton_choose_file.pressed.connect(self.choose_test_file)
        self.pushButton_next.pressed.connect(self.open_date_dialog)

    def fill_existing_data(self):
        self.lineEdit_model_name.setText(self.model[MODEL_NAME])

    def choose_test_file(self):
        # Get the user input from a dialog window
        self.test_file, _ = QFileDialog.getOpenFileName(
            None,
            "Open Sensor Data",
            QDir.currentPath(),
            filter="csv (*.csv)"
        )
        self.test_file = Path(self.test_file)

        # Show the selected file path in the dialog
        self.label_selected_file.setText(self.test_file.stem)

    def open_date_dialog(self):
        model_name = self.lineEdit_model_name.text()

        if model_name != '':
            self.model[MODEL_NAME] = model_name
            dialog = SensorModelDateDialog(
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
            error_dialog.showMessage("Project name cannot be empty.")
            error_dialog.exec()
