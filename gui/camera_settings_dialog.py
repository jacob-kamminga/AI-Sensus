import pytz
from PyQt5 import QtWidgets

from datastorage.camerainfo import CameraManager
from gui.designer_camera_settings import Ui_Dialog


class CameraSettingsDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, camera_manager: CameraManager):
        super().__init__()
        self.setupUi(self)
        self.camera_manager = camera_manager

        # Fill camera dictionary and add camera names to combobox
        self.camera_dict = dict()
        cameras = self.camera_manager.get_all_cameras()

        for camera in cameras:
            name = camera[0]
            timezone = camera[1]

            self.camera_dict[name] = timezone
            self.comboBox_camera.addItem(name)

        # Add timezones to combobox
        self.listWidget_timezones.addItems(pytz.common_timezones)

        # Connect UI elements
        self.comboBox_camera.currentTextChanged.connect(self.camera_changed)
        self.lineEdit_timezone.textChanged.connect(self.filter_text_changed)

        # Select the timezone of the current camera
        timezone_index = pytz.common_timezones.index(cameras[0][1])
        self.listWidget_timezones.setCurrentRow(timezone_index)

    def camera_changed(self, text: str):
        if self.camera_dict and self.comboBox_camera.count():
            index = pytz.common_timezones.index(self.camera_dict[text])
            self.listWidget_timezones.setCurrentRow(index)

    def filter_text_changed(self):
        filter_text = str(self.lineEdit_timezone.text()).lower()

        for i in range(len(pytz.common_timezones)):
            if filter_text in str(pytz.common_timezones[i]).lower():
                self.listWidget_timezones.setRowHidden(i, False)
            else:
                self.listWidget_timezones.setRowHidden(i, True)

    def selection_changed(self):
        # TODO: Enable 'save timezone' pushbutton
        pass

    def save_timezone(self):
        # TODO: Save timezone to database
        pass
