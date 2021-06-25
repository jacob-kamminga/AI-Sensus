from PyQt5.QtWidgets import QDialog

from gui.designer.sensor_model_list import Ui_Dialog
from gui.dialogs.new_sensor_model_final_dialog import SensorModelFinalDialog
from gui.dialogs.new_sensor_model_name_dialog import SensorModelNameDialog
from gui.dialogs.project_settings_dialog import ProjectSettingsDialog
from database.models import *


class SensorModelDialog(QDialog, Ui_Dialog):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.models = None
        self.selected_model_id = None

        self.init()

        self.listWidget_models.itemDoubleClicked.connect(self.edit_sensor_model_name_dialog)
        self.pushButton_new.pressed.connect(self.new_sensor_model_name_dialog)
        self.pushButton_settings.pressed.connect(self.edit_sensor_model_name_dialog)
        self.buttonBox.accepted.connect(self.set_selected_model)

    def init(self):
        all_models = SensorModel.select()
        self.models = dict((model.model_name, model.id) for model in all_models)
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
        dialog = SensorModelNameDialog(parent=self)
        dialog.exec()

    def edit_sensor_model_name_dialog(self):
        if len(self.listWidget_models.selectedItems()) > 0:
            selected_model_name = self.listWidget_models.selectedItems()[0].text()
            selected_model_id = self.models[selected_model_name]
            dialog = SensorModelFinalDialog(model_id=selected_model_id, parent=self)
            dialog.exec()
