import pytz
from PyQt5 import QtWidgets

from database.models import Camera
from gui.designer.camera_settings import Ui_Dialog

CAMERA_ID_INDEX = 0
CAMERA_NAME_INDEX = 1
CAMERA_TIMEZONE_INDEX = 2


class CameraSettingsDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, camera: Camera):
        super().__init__()
        self.setupUi(self)
        self.camera = camera

        # Pre-fill name in edit box
        self.lineEdit_change_camera_name.setText(self.camera.name)

        # Add timezones to combobox
        self.listWidget_timezones.addItems(pytz.common_timezones)

        # Select the timezone of the current camera
        tz_index = pytz.common_timezones.index(self.camera.timezone)
        self.listWidget_timezones.setCurrentRow(tz_index)
        self.lineEdit_timezone.setText(self.camera.timezone)

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
        """
        Filter timezone options in list widget based on text input.
        """
        filter_text = str(self.lineEdit_timezone.text()).lower()

        for i in range(len(pytz.common_timezones)):
            if filter_text in str(pytz.common_timezones[i]).lower():
                self.listWidget_timezones.setRowHidden(i, False)
            else:
                self.listWidget_timezones.setRowHidden(i, True)

    def save_camera_settings(self):
        self.camera.name = self.lineEdit_change_camera_name.text()
        self.camera.timezone = self.listWidget_timezones.selectedItems()[0].text()
        self.camera.save()
        self.close()
    # def enable_timezone_pushbutton(self):
    #     self.pushButton_save_timezone.setEnabled(True)
    #
    # def disable_timezone_pushbutton(self):
    #     self.pushButton_save_timezone.setEnabled(False)
