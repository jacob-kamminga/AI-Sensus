import pytz
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

from gui.designer.select_camera import Ui_Dialog
from gui.dialogs.camera_settings import CameraSettingsDialog
from gui_components.camera import Camera

CAMERA_ID_INDEX = 0
CAMERA_NAME_INDEX = 1
CAMERA_TIMEZONE_INDEX = 2


class SelectCameraDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, camera: Camera):
        super().__init__()
        self.setupUi(self)
        self.camera = camera
        self.selected_camera_id = None

        # Fill camera dictionary and add camera names to combobox
        self.camera_dict = dict()
        self.load_cameras(self.camera.camera_name)

        # Connect UI elements
        self.pushButton_new_camera.setEnabled(False)
        self.pushButton_new_camera.clicked.connect(self.add_camera)
        self.pushButton_use_camera.clicked.connect(self.use_camera)
        self.pushButton_edit_camera.clicked.connect(self.edit_camera)
        self.pushButton_cancel_select_camera.clicked.connect(self.close)
        self.pushButton_delete_camera.clicked.connect(self.delete_camera)
        self.lineEdit_new_camera_name.textChanged.connect(self.toggle_add_camera_pushbutton)

    def add_camera(self):
        new_camera_name = self.lineEdit_new_camera_name.text()
        if new_camera_name != '':
            self.camera.camera_manager.add_camera(self.lineEdit_new_camera_name.text())
            self.comboBox_camera.addItem(new_camera_name)
            self.comboBox_camera.setCurrentText(new_camera_name)
            self.edit_camera()
            self.lineEdit_new_camera_name.clear()

    def use_camera(self):
        selected_camera_name = self.comboBox_camera.currentText()
        self.selected_camera_id = self.camera.camera_manager.get_camera_id(selected_camera_name)
        self.close()

    def edit_camera(self):
        dialog = CameraSettingsDialog(self.camera.camera_manager, self.comboBox_camera.currentText())
        dialog.exec()
        dialog.show()
        self.load_cameras(dialog.camera_name)

    def load_cameras(self, selected_camera_name):
        self.comboBox_camera.clear()
        cameras = self.camera.camera_manager.get_all_cameras()

        for camera in cameras:
            name = camera[CAMERA_NAME_INDEX]
            timezone = camera[CAMERA_TIMEZONE_INDEX]

            self.camera_dict[name] = timezone
            self.comboBox_camera.addItem(name)
            # Select current camera in combobox
        if selected_camera_name is not None:
            self.comboBox_camera.setCurrentText(selected_camera_name)

    def delete_camera(self):
        selected_camera_name = self.comboBox_camera.currentText()
        res = QMessageBox(
            QMessageBox.Warning,
            'Heads up!',
            'Are you sure you want to delete ' + selected_camera_name + '?',
            QMessageBox.Ok | QMessageBox.Cancel
        ).exec()

        if res == QMessageBox.Ok:
            self.camera.camera_manager.delete_camera(self.camera.camera_manager.get_camera_id(selected_camera_name))
            self.comboBox_camera.removeItem(self.comboBox_camera.findText(selected_camera_name))

    def toggle_add_camera_pushbutton(self):
        if self.lineEdit_new_camera_name.text() == '':
            self.pushButton_new_camera.setEnabled(False)
        else:
            self.pushButton_new_camera.setEnabled(True)
