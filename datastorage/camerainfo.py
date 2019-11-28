import sqlite3
from typing import List, Tuple

import pytz

SQL_CREATE_TABLE = "CREATE TABLE cameras (Name TEXT PRIMARY KEY, Timezone VARCHAR(50))"
SQL_ADD_CAMERA = "INSERT INTO cameras VALUES (?, ?)"
SQL_DELETE_CAMERA = "DELETE FROM cameras WHERE Name = ?"
SQL_GET_ALL_CAMERAS = "SELECT Name, Timezone FROM cameras"
SQL_UPDATE_TIMEZONE = "UPDATE cameras SET Timezone = ? WHERE Name = ?"


class CameraManager:

    def __init__(self):
        self._conn = sqlite3.connect('data.db')
        self._cur = self._conn.cursor()

    def create_table(self) -> None:
        """Creates the necessary cameras table in the database."""
        self._cur.execute(SQL_CREATE_TABLE)
        self._conn.commit()

    def add_camera(self, name: str, timezone: str = 'UTC') -> None:
        """
        Adds a camera to the table.

        :param name: The name of the new camera
        :param timezone: The timezone that has been set on the camera
        """
        self._cur.execute(SQL_ADD_CAMERA, [timezone, name])
        self._conn.commit()

    def delete_camera(self, name: str) -> None:
        """
        Deletes a camera from the table.

        :param name: The name of the camera
        """
        self._cur.execute(SQL_DELETE_CAMERA, [name])
        self._conn.commit()

    def get_all_cameras(self) -> List[Tuple[str, str]]:
        """
        Returns all cameras

        :return: list of tuples (name, timezone) of all cameras
        """
        self._cur.execute(SQL_GET_ALL_CAMERAS)
        return self._cur.fetchall()

    def update_timezone(self, name: str, timezone: str):
        """
        Updates the timezone of a camera.

        :param name: The name of the camera
        :param timezone: The timezone that has been set on the camera
        """
        self._cur.execute(SQL_UPDATE_TIMEZONE, [timezone, name])
        self._conn.commit()
