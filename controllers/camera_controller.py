import peewee
import pytz
from PyQt5.QtWidgets import QMessageBox

from database.models import Camera


class CameraController:

    def __init__(self, gui):
        self.gui = gui
        self.camera = None

    def change_camera(self, camera_id: int):

        # Update camera name in main GUI
        self.camera = Camera.get_by_id(camera_id)
        self.gui.label_camera_name_value.setText(self.camera.name)

        if self.gui.video_controller.video is not None:
            self.gui.video_controller.update_camera(camera_id)

        # Update offset between camera and sensor data
        self.gui.update_camera_sensor_offset()

    def add_camera(self, camera_name: str, timezone: pytz.timezone = None, manual_offset: int = None):
        if timezone is None:
            project_tz = self.gui.project_controller.get_setting('timezone')
            if project_tz is not None:
                timezone = project_tz
            else:
                timezone = 'UTC'

        if manual_offset is None:
            manual_offset = 0
        try:
            Camera.create(name=camera_name,
                          timezone=timezone,
                          manual_offset=manual_offset)

        except peewee.IntegrityError:
            raise

    def delete_camera(self, camera_id: int):
        Camera.get_by_id(camera_id).delete_instance()
