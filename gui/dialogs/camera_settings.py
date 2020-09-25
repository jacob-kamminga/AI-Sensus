import pytz
from PyQt5 import QtWidgets

from database.camera_manager import CameraManager
from gui.designer.camera_settings import Ui_Dialog

CAMERA_ID_INDEX = 0
CAMERA_NAME_INDEX = 1
CAMERA_TIMEZONE_INDEX = 2


class CameraSettingsDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, camera_manager: CameraManager, camera_name):
        super().__init__()
        self.setupUi(self)
        self.camera_manager = camera_manager
        self.camera_name = camera_name
        self.selected_camera_id = self.camera_manager.get_camera_id(camera_name)
        self.time_zone = self.camera_manager.get_timezone(self.selected_camera_id).zone

        # Pre-fill name in edit box
        self.lineEdit_change_camera_name.setText(self.camera_name)

        # Add timezones to combobox
        self.listWidget_timezones.addItems(pytz.common_timezones)

        # Select the timezone of the current camera
        timezone_index = pytz.common_timezones.index(self.time_zone)
        self.listWidget_timezones.setCurrentRow(timezone_index)
        self.lineEdit_timezone.setText(self.time_zone)

        # Connect UI elements
        self.lineEdit_timezone.textChanged.connect(self.filter_timezone_rows)
        # self.listWidget_timezones.selectionModel().selectionChanged.connect(self.enable_timezone_pushbutton)
        self.pushButton_save_camera_settings.clicked.connect(self.save_camera_settings)
        self.pushButton_cancel_camera_settings.clicked.connect(self.close)

    def load_timezones(self, text: str):
        if self.camera_dict and self.comboBox_camera.count():
            index = pytz.common_timezones.index(self.camera_dict[text])
            self.listWidget_timezones.setCurrentRow(index)

    def filter_timezone_rows(self):
        filter_text = str(self.lineEdit_timezone.text()).lower()

        for i in range(len(pytz.common_timezones)):
            if filter_text in str(pytz.common_timezones[i]).lower():
                self.listWidget_timezones.setRowHidden(i, False)
            else:
                self.listWidget_timezones.setRowHidden(i, True)

    def save_camera_settings(self):
        # Get selection
        self.camera_name = self.lineEdit_change_camera_name.text()
        selected_timezone = self.listWidget_timezones.selectedItems()[0].text()

        # Update database entry
        self.camera_manager.update_camera(self.selected_camera_id, self.camera_name, selected_timezone)
        self.close()
    # def enable_timezone_pushbutton(self):
    #     self.pushButton_save_timezone.setEnabled(True)
    #
    # def disable_timezone_pushbutton(self):
    #     self.pushButton_save_timezone.setEnabled(False)
