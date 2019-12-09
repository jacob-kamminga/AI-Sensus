import pytz
from PyQt5 import QtWidgets

from data_storage.camera_info import CameraManager
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

        # Select the timezone of the current camera
        timezone_index = pytz.common_timezones.index(cameras[0][1])
        self.listWidget_timezones.setCurrentRow(timezone_index)

        # Connect UI elements
        self.comboBox_camera.currentTextChanged.connect(self.load_timezones)
        self.lineEdit_timezone.textChanged.connect(self.filter_timezone_rows)
        self.listWidget_timezones.selectionModel().selectionChanged.connect(self.enable_timezone_pushbutton)
        self.pushButton_save_timezone.clicked.connect(self.save_timezone)
        self.pushButton_new_camera.clicked.connect(self.add_camera)

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

    def save_timezone(self):
        # Get selection
        selected_camera = self.comboBox_camera.currentText()
        selected_timezone = self.listWidget_timezones.selectedItems()[0].text()

        # Update database entry
        self.camera_manager.update_timezone(selected_camera, selected_timezone)

        # Disable save timezone pushbutton
        self.disable_timezone_pushbutton()

    def add_camera(self):
        new_camera = self.lineEdit_new_camera.text()
        current_cameras = [camera[0] for camera in self.camera_manager.get_all_cameras()]

        if new_camera != '' and new_camera not in current_cameras:
            self.camera_manager.add_camera(new_camera)
            self.comboBox_camera.addItem(new_camera)
            self.comboBox_camera.setCurrentText(new_camera)
            self.lineEdit_new_camera.clear()
        else:
            # TODO: Display error
            pass

    def enable_timezone_pushbutton(self):
        self.pushButton_save_timezone.setEnabled(True)

    def disable_timezone_pushbutton(self):
        self.pushButton_save_timezone.setEnabled(False)
