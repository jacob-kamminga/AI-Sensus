from PyQt5.QtWidgets import QMessageBox

from data_storage.camera_info import CameraManager
from data_storage.device_offsets import OffsetManager


class Camera:

    def __init__(self, gui):
        self.gui = gui
        self.settings = gui.settings

        self.camera_manager = CameraManager(self.gui.project_dialog.project_name)
        self.offset_manager = OffsetManager(self.gui.project_dialog.project_name)

        # Add the known cameras to the camera combo box in the GUI
        for camera in self.camera_manager.get_all_cameras():
            name = camera[0]
            self.gui.comboBox_camera_ids.addItem(name)

    def add_camera(self):
        """
        Adds a camera to the database and to the combobox in the GUI.
        """
        if self.gui.lineEdit_new_camera.text() \
                and self.gui.lineEdit_new_camera.text() not in self.camera_manager.get_all_cameras():
            self.camera_manager.add_camera(self.gui.lineEdit_new_camera.text())
            self.gui.comboBox_camera_ids.addItem(self.gui.lineEdit_new_camera.text())
            self.gui.comboBox_camera_ids.setCurrentText(self.gui.lineEdit_new_camera.text())
            self.gui.lineEdit_new_camera.clear()
            if self.gui.comboBox_camera_ids.currentText() and self.gui.sensor_data.data:
                self.gui.doubleSpinBox_video_offset.setValue(
                    self.offset_manager.get_offset(self.gui.comboBox_camera_ids.currentText(),
                                                   self.gui.sensor_data.data.metadata['sn'],
                                                   self.gui.sensor_data.data.metadata['date']))

    def change_camera(self):
        """
        If the user chooses a different camera, this function retrieves the right offset and timezone.
        """
        camera_name = self.gui.comboBox_camera_ids.currentText()

        if camera_name != '':
            timezone = self.camera_manager.get_timezone(camera_name)

            self.gui.video.set_timezone(timezone)

            if self.gui.sensor_data.data is not None:
                self.gui.doubleSpinBox_video_offset.setValue(
                    self.offset_manager.get_offset(self.gui.comboBox_camera_ids.currentText(),
                                                   self.gui.sensor_data.data.metadata['sn'],
                                                   self.gui.sensor_data.data.metadata['date']))

    def change_offset(self):
        """
        If the user changes the offset, this function sends it to the database.
        """
        if self.gui.comboBox_camera_ids.currentText() and self.gui.sensor_data.data:
            self.offset_manager.set_offset(self.gui.comboBox_camera_ids.currentText(),
                                           self.gui.sensor_data.data.metadata['sn'],
                                           self.gui.doubleSpinBox_video_offset.value(),
                                           self.gui.sensor_data.data.metadata['date'])

    def delete_camera(self):
        """
        Deletes the current camera.
        """
        if self.gui.comboBox_camera_ids.currentText():
            reply = QMessageBox.question(self.gui, "Message", "Are you sure you want to delete the current camera?",
                                         QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.camera_manager.delete_camera(self.gui.comboBox_camera_ids.currentText())
                self.gui.comboBox_camera_ids.clear()
                for camera in self.camera_manager.get_all_cameras():
                    self.gui.comboBox_camera_ids.addItem(camera)
                self.gui.doubleSpinBox_video_offset.clear()
                if self.gui.comboBox_camera_ids.currentText() and self.gui.sensor_data.data:
                    self.gui.doubleSpinBox_video_offset.setValue(
                        self.offset_manager.get_offset(self.gui.comboBox_camera_ids.currentText(),
                                                       self.gui.sensor_data.data.metadata['sn'],
                                                       self.gui.sensor_data.data.metadata['date']))
                else:
                    self.gui.doubleSpinBox_video_offset.setValue(0)
