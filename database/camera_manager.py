import sqlite3
from typing import List, Tuple

import pytz

from project_settings import ProjectSettings

SQL_CREATE_TABLE = "create table camera \
( \
  name     TEXT    not null, \
  timezone TEXT default 'UTC' not null, \
  id       INTEGER not null \
    constraint cameras_pk \
      primary key autoincrement \
); \
 \
create unique index cameras_name_uindex \
  on camera (name);"

SQL_DELETE_CAMERA = "DELETE FROM camera WHERE id = ?"
SQL_INSERT_CAMERA = "INSERT INTO camera(name, timezone) VALUES (?, ?)"
SQL_SELECT_ALL_CAMERAS = "SELECT id, name, timezone FROM camera"
SQL_SELECT_CAMERA_ID = "SELECT id FROM camera WHERE name = ?"
SQL_SELECT_CAMERA_NAME = "SELECT name FROM camera WHERE id = ?"
SQL_SELECT_TIMEZONE = "SELECT timezone FROM camera WHERE id = ?"
SQL_UPDATE_TIMEZONE = "UPDATE camera SET timezone = ? WHERE id = ?"
SQL_UPDATE_CAMERA = "UPDATE camera SET name = ?,  timezone = ? WHERE id = ?"


class CameraManager:

    def __init__(self, settings: ProjectSettings):
        self._conn = sqlite3.connect(
            settings.database_file.as_posix(),
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        # Enable Sqlite foreign key support
        self._conn.execute("PRAGMA foreign_keys = 1")

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
        self._cur.execute(SQL_INSERT_CAMERA, (camera_name, timezone))
        self._conn.commit()

    def delete_camera(self, camera_id: int) -> None:
        """
        Deletes a camera from the table.

        :param camera_id: The name of the camera
        """
        self._cur.execute(SQL_DELETE_CAMERA, (camera_id,))
        self._conn.commit()

    def get_camera_name(self, camera_id: int) -> str:
        """
        Returns the camera name of the camera.

        :return: The camera name of the camera if exists, else None
        """
        self._cur.execute(SQL_SELECT_CAMERA_NAME, (camera_id,))
        return self._cur.fetchone()[0] # TODO: Why is this subscripted? When returns None, an error is raised

    def get_camera_id(self, camera_name: str) -> int:
        """
        Returns the camera name of the camera.

        :return: The camera name of the camera if exists, else None
        """
        self._cur.execute(SQL_SELECT_CAMERA_ID, (camera_name,))
        return self._cur.fetchone()[0]

    def get_all_cameras(self) -> List[Tuple[str, str, str]]:
        """
        Returns all cameras

        :return: List of tuples (id, name, timezone) of all cameras
        """
        self._cur.execute(SQL_SELECT_ALL_CAMERAS)
        return self._cur.fetchall()

    def get_timezone(self, camera_id: int) -> pytz.timezone:
        self._cur.execute(SQL_SELECT_TIMEZONE, (camera_id,))
        timezone_str = self._cur.fetchone()[0]

        return pytz.timezone(timezone_str)

    def update_timezone(self, camera_id: int, timezone: str):
        """
        Updates the timezone of a camera.

        :param camera_id: The ID of the camera
        :param timezone: The timezone that has been set on the camera
        """
        self._cur.execute(SQL_UPDATE_TIMEZONE, (timezone, camera_id))
        self._conn.commit()

    def update_camera(self, camera_id: int, camera_name: str, timezone: str):
        """
        Updates the name and timezone of a camera. The camera is selected by camera_id.

        :param camera_id: The ID of the camera
        :param camera_name: The name of the camera
        :param timezone: The timezone that has been set on the camera
        """
        self._cur.execute(SQL_UPDATE_CAMERA, (camera_name, timezone, camera_id))
        self._conn.commit()
