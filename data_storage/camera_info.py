import sqlite3
from typing import List, Tuple

import pytz

SQL_CREATE_TABLE = "CREATE TABLE camera (id INTEGER PRIMARY KEY, name TEXT, timezone TEXT)"
SQL_ADD_CAMERA = "INSERT INTO camera(name, timezone) VALUES (?, ?)"
SQL_DELETE_CAMERA = "DELETE FROM camera WHERE name = ?"
SQL_GET_ALL_CAMERAS = "SELECT name, timezone FROM camera"
SQL_GET_TIMEZONE = "SELECT timezone FROM camera WHERE name = ?"
SQL_UPDATE_TIMEZONE = "UPDATE camera SET timezone = ? WHERE name = ?"


class CameraManager:

    def __init__(self, project_name: str):
        self._conn = sqlite3.connect('projects/' + project_name + '/project_data.db',
                                     detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self._cur = self._conn.cursor()

    def create_table(self) -> None:
        """Creates the necessary cameras table in the database."""
        self._cur.execute(SQL_CREATE_TABLE)
        self._conn.commit()

    def add_camera(self, camera_name: str, timezone: str = 'UTC') -> None:
        """
        Adds a camera to the table.

        :param camera_name: The name of the new camera
        :param timezone: The timezone that has been set on the camera
        """
        self._cur.execute(SQL_ADD_CAMERA, (camera_name, timezone))
        self._conn.commit()

    def delete_camera(self, camera_name: str) -> None:
        """
        Deletes a camera from the table.

        :param camera_name: The name of the camera
        """
        self._cur.execute(SQL_DELETE_CAMERA, (camera_name,))
        self._conn.commit()

    def get_all_cameras(self) -> List[Tuple[str, str]]:
        """
        Returns all cameras

        :return: list of tuples (name, timezone) of all cameras
        """
        self._cur.execute(SQL_GET_ALL_CAMERAS)
        return self._cur.fetchall()

    def get_timezone(self, camera_name: str) -> pytz.timezone:
        self._cur.execute(SQL_GET_TIMEZONE, (camera_name,))
        timezone_str = self._cur.fetchone()[0]

        return pytz.timezone(timezone_str)

    def update_timezone(self, camera_name: str, timezone: str):
        """
        Updates the timezone of a camera.

        :param camera_name: The name of the camera
        :param timezone: The timezone that has been set on the camera
        """
        self._cur.execute(SQL_UPDATE_TIMEZONE, (timezone, camera_name))
        self._conn.commit()
