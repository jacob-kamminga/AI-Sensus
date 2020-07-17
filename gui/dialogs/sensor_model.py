from PyQt5.QtWidgets import QDialog

from constants import ID, MODEL_NAME
from database.sensor_model_manager import SensorModelManager
from gui.designer.sensor_model_list import Ui_Dialog
from gui.dialogs.new_sensor_model_name import SensorModelNameDialog
from project_settings import ProjectSettings


class SensorModelDialog(QDialog, Ui_Dialog):

    def __init__(self, settings: ProjectSettings):
        super().__init__()
        self.setupUi(self)
        self.settings = settings

        self.sensor_model_manager = SensorModelManager(self.settings)
        self.models = None
        self.selected_model_id = None

        self.init()

        self.pushButton_new.pressed.connect(self.new_sensor_model_name_dialog)
        self.pushButton_settings.pressed.connect(self.edit_sensor_model_name_dialog)
        self.buttonBox.accepted.connect(self.set_selected_model)

    def init(self):
        self.models = dict((row[MODEL_NAME], row[ID]) for row in self.sensor_model_manager.get_all_models())
        self.fill_list()

    def fill_list(self):
        self.listWidget_models.blockSignals(True)
        self.listWidget_models.clear()
        self.listWidget_models.addItems(self.models.keys())
        self.listWidget_models.blockSignals(False)

    def set_selected_model(self):
        if len(self.listWidget_models.selectedItems()) > 0:
            selected_model_name = self.listWidget_models.selectedItems()[0].text()
            self.selected_model_id = self.models[selected_model_name]

    def new_sensor_model_name_dialog(self):
        dialog = SensorModelNameDialog(self.settings, parent=self)
        dialog.exec()

    def edit_sensor_model_name_dialog(self):
        if len(self.listWidget_models.selectedItems()) > 0:
            selected_model_name = self.listWidget_models.selectedItems()[0].text()
            selected_model_id = self.models[selected_model_name]
            dialog = SensorModelNameDialog(self.settings, model_id=selected_model_id, parent=self)
            dialog.exec()
