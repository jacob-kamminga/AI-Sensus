from PyQt5.QtWidgets import QDialog, QMessageBox, QDialogButtonBox

from controllers.sensor_controller import SensorController
from gui.designer.sensor_model_list import Ui_Dialog
from gui.dialogs.new_sensor_model_final_dialog import SensorModelFinalDialog
from gui.dialogs.new_sensor_model_name_dialog import SensorModelNameDialog
from database.models import *


class SensorModelDialog(QDialog, Ui_Dialog):

    def __init__(self, sensor_controller: SensorController):
        super().__init__()
        self.setupUi(self)

        self.closed_by_user = False

        self.sensor_controller = sensor_controller
        self.models = None
        self.selected_model_id = None

        self.load_list()

        self.listWidget_models.itemDoubleClicked.connect(self.edit_sensor_model_name_dialog)
        self.pushButton_new.pressed.connect(self.new_sensor_model_name_dialog)
        self.pushButton_settings.pressed.connect(self.edit_sensor_model_name_dialog)
        self.buttonBox.accepted.connect(self.set_selected_model)
        self.buttonBox.rejected.connect(self.close)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.listWidget_models.itemSelectionChanged.connect(self.toggle_accept_button)

    def load_list(self, new_row_name: str = None):
        all_models = SensorModel.select()
        self.models = dict((model.model_name, model.id) for model in all_models)

        self.listWidget_models.blockSignals(True)
        self.listWidget_models.clear()
        self.listWidget_models.addItems(self.models.keys())
        self.listWidget_models.blockSignals(False)

        if new_row_name is not None:
            num_rows = self.listWidget_models.count()
            self.listWidget_models.setCurrentRow(num_rows-1)

    def set_selected_model(self):
        if len(self.listWidget_models.selectedItems()) > 0:
            selected_model_name = self.listWidget_models.selectedItems()[0].text()
            self.selected_model_id = self.models[selected_model_name]

    def new_sensor_model_name_dialog(self):
        dialog = SensorModelNameDialog(self.sensor_controller, parent=self)
        dialog.exec()

    def edit_sensor_model_name_dialog(self):
        if len(self.listWidget_models.selectedItems()) > 0:
            selected_model_name = self.listWidget_models.selectedItems()[0].text()
            selected_model_id = self.models[selected_model_name]
            dialog = SensorModelFinalDialog(self.sensor_controller, model_id=selected_model_id, parent=self)
            dialog.exec()

    def closeEvent(self, event):
        self.closed_by_user = True

    def toggle_accept_button(self):
        model_is_selected = len(self.listWidget_models.selectedItems()) > 0
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(model_is_selected)
