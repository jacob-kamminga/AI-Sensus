import pytz

from database.camera_manager import CameraManager
from project_settings import ProjectSettingsDialog


class Camera:

    def __init__(self, gui):
        self.gui = gui
        self.settings: ProjectSettingsDialog = gui.settings

        self.camera_manager = CameraManager(self.settings)

        self.camera_id = None
        self.camera_name = None
        self.timezone = None

    def change_camera(self, camera_id: int):
        # Update camera name in main GUI
        self.camera_id = camera_id
        self.camera_name = self.camera_manager.get_camera_name(self.camera_id)
        self.gui.label_camera_name_value.setText(self.camera_name)

        # Update timezone and datetime labels
        self.timezone = self.camera_manager.get_timezone(self.camera_id)
        self.gui.video.update_datetime()

        # Update offset between camera and sensor data
        self.gui.update_camera_sensor_offset()

    # def delete_camera(self):
    #     """
    #     Deletes the current camera.
    #     """
    #     if self.gui.comboBox_camera_ids.currentText():
    #         reply = QMessageBox.question(self.gui, "Message", "Are you sure you want to delete the current camera?",
    #                                      QMessageBox.Yes, QMessageBox.No)
    #         if reply == QMessageBox.Yes:
    #             self.camera_manager.delete_camera(self.gui.comboBox_camera_ids.currentText())
    #             self.gui.comboBox_camera_ids.clear()
    #
    #             for camera in self.camera_manager.get_all_cameras():
    #                 self.gui.comboBox_camera_ids.addItem(camera)
    #
    #             self.gui.doubleSpinBox_video_offset.clear()
    #
    #             if self.gui.comboBox_camera_ids.currentText() and self.gui.sensor_data_file.data:
    #                 self.gui.doubleSpinBox_video_offset.setValue(
    #                     self.offset_manager.get_offset(self.gui.comboBox_camera_ids.currentText(),
    #                                                    self.gui.sensor_data_file.data.metadata['sn'],
    #                                                    self.gui.sensor_data_file.data.metadata['date'])
    #                 )
    #             else:
    #                 self.gui.doubleSpinBox_video_offset.setValue(0)
