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
        # self.camera_dict = dict()  # Unused
        if self.camera_controller.camera is not None:
            self.load_cameras(self.camera_controller.camera.name)

        # Connect UI elements
        self.pushButton_new_camera.setEnabled(False)
        self.pushButton_new_camera.clicked.connect(lambda: self.add_camera(self.lineEdit_new_camera_name.text()))
        self.pushButton_use_camera.clicked.connect(lambda: self.use_camera(self.get_selected_camera_name()))
        self.pushButton_edit_camera.clicked.connect(lambda: self.edit_camera(self.get_selected_camera_name()))
        self.pushButton_cancel_select_camera.clicked.connect(self.close)
        self.pushButton_delete_camera.clicked.connect(lambda: self.delete_camera(self.get_selected_camera_name()))
        self.lineEdit_new_camera_name.textChanged.connect(self.toggle_add_camera_pushbutton)

    def get_selected_camera_name(self):
        """Get the name of the camera that is currently selected in the combobox."""
        return self.comboBox_camera.currentText()

    def load_cameras(self, camera_name: str):
        """Load all the cameras from the database into the combobox and store their timezones in a dict."""
        self.comboBox_camera.clear()  # Clear the list

        cameras = Camera.select()                            # Retrieve all the cameras in the database
        for camera in cameras:
            # self.camera_dict[camera.name] = camera.timezone  # Store all their timezones (unused)
            self.comboBox_camera.addItem(camera.name)        # Fill the list with all the camera names

        # Set current camera in combobox
        if camera_name is not None:
            self.comboBox_camera.setCurrentText(camera_name)

    def add_camera(self, camera_name: str):
        if camera_name != '':
            Camera.create(name=camera_name)
            self.comboBox_camera.addItem(camera_name)  # Add the new camera to the list
            self.comboBox_camera.setCurrentText(camera_name)  # Set the new camera as the selected camera.
            self.edit_camera(self.get_selected_camera_name())

            # Clear the line edit field
            self.lineEdit_new_camera_name.clear()

    def use_camera(self, camera_name: str):
        """
        Change the camera to the one that is selected when pressing "Save changes".
        """
        if camera_name != '':
            self.camera_controller.camera = Camera.get(Camera.name == camera_name)
            self.close()

    def edit_camera(self, camera_name: str):
        """Open the edit dialog for the selected camera and load it to """
        if camera_name != '':
            selected_camera = Camera.get(Camera.name == camera_name)  # Retrieve the selected camera from the database.
            dialog = CameraSettingsDialog(selected_camera)            # Open the setting dialogs to allow for changes.
            dialog.exec()
            self.load_cameras(selected_camera.name)                   # Reload the cameras name in the combobox.

    def delete_camera(self, camera_name: str):
        if camera_name != '':
            res = QMessageBox(
                QMessageBox.Warning,
                'Heads up!',
                f'Are you sure you want to delete the camera \"{camera_name}\"?',
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
        """Disable the "Add" button if the camera name field is empty."""
        if self.lineEdit_new_camera_name.text() == '':
            self.pushButton_new_camera.setEnabled(False)
        else:
            self.pushButton_new_camera.setEnabled(True)
