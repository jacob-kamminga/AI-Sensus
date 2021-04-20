from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

from database.models import Camera, Video
from gui.designer.select_camera import Ui_Dialog
from gui.dialogs.camera_settings_dialog import CameraSettingsDialog

CAMERA_ID_INDEX = 0
CAMERA_NAME_INDEX = 1
CAMERA_TIMEZONE_INDEX = 2


class SelectCameraDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, gui):
        super().__init__()
        self.setupUi(self)
        self.camera_controller = gui.camera_controller
        self.camera = None

        # Fill camera dictionary and add camera names to combobox
        self.camera_dict = dict()
        self.load_cameras(self.camera_controller.camera_name)

        # Connect UI elements
        self.pushButton_new_camera.setEnabled(False)
        self.pushButton_new_camera.clicked.connect(self.add_camera)
        self.pushButton_use_camera.clicked.connect(self.use_camera)
        self.pushButton_edit_camera.clicked.connect(self.edit_camera)
        self.pushButton_cancel_select_camera.clicked.connect(self.close)
        self.pushButton_delete_camera.clicked.connect(self.delete_camera)
        self.lineEdit_new_camera_name.textChanged.connect(self.toggle_add_camera_pushbutton)

    def add_camera(self):
        camera_name = self.lineEdit_new_camera_name.text()
        if camera_name != '':
            Camera.create(name=camera_name)
            self.comboBox_camera.addItem(camera_name)
            self.comboBox_camera.setCurrentText(camera_name)
            self.edit_camera()

            # Clear the line edit field
            self.lineEdit_new_camera_name.clear()

    def use_camera(self):
        camera_name = self.comboBox_camera.currentText()

        if camera_name:
            self.camera = Camera.get(Camera.name == camera_name)
            self.close()

    def edit_camera(self):
        camera_name = self.comboBox_camera.currentText()
        if camera_name:
            camera = Camera.get(Camera.name == camera_name)
            dialog = CameraSettingsDialog(camera)
            dialog.exec()
            dialog.show()
            self.load_cameras(dialog.camera.name)

    def load_cameras(self, camera_name):
        self.comboBox_camera.clear()
        cameras = Camera.select()

        for camera in cameras:
            self.camera_dict[camera.name] = camera.timezone
            self.comboBox_camera.addItem(camera.name)

        # Select current camera in combobox
        if camera_name is not None:
            self.comboBox_camera.setCurrentText(camera_name)

    def delete_camera(self):
        camera_name = self.comboBox_camera.currentText()

        if camera_name:
            res = QMessageBox(
                QMessageBox.Warning,
                'Heads up!',
                'Are you sure you want to delete ' + camera_name + '?',
                QMessageBox.Ok | QMessageBox.Cancel
            ).exec()

            if res == QMessageBox.Ok:
                # First delete all videos that assigned this camera to it
                query = Video.delete().where(Video.camera.name == camera_name)
                query.execute()
                # Delete camera
                camera = Camera.get(Camera.name == camera_name)
                camera.delete_instance()
                self.comboBox_camera.removeItem(self.comboBox_camera.findText(camera_name))

    def toggle_add_camera_pushbutton(self):
        if self.lineEdit_new_camera_name.text() == '':
            self.pushButton_new_camera.setEnabled(False)
        else:
            self.pushButton_new_camera.setEnabled(True)
