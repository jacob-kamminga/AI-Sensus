import sqlite3
from typing import List

sql_add_camera = "INSERT INTO cameras(Name) VALUES (?)"
sql_delete_camera = "DELETE FROM cameras WHERE Name = ?"
sql_get_all_cameras = "SELECT Name FROM cameras"


class CameraManager:

    def __init__(self):
        self._conn = sqlite3.connect('data.db')
        self._cur = self._conn.cursor()

    def create_table(self) -> None:
        """Creates the necessary cameras table in the database."""
        self._cur.execute("CREATE TABLE cameras (Name TEXT PRIMARY KEY)")
        self._conn.commit()

    def add_camera(self, name: str) -> None:
        """
        Adds a camera to the table.

        :param name: The name of the new camera
        """
        self._cur.execute(sql_add_camera, [name])
        self._conn.commit()

    def delete_camera(self, name: str) -> None:
        """
        Deletes a camera from the table.

        :param name: The name of the camera
        """
        self._cur.execute(sql_delete_camera, [name])
        self._conn.commit()

    def get_all_cameras(self) -> List[str]:
        """
        Returns all cameras

        :return: list of all known cameras
        """
        self._cur.execute(sql_get_all_cameras)
        return [x[0] for x in self._cur.fetchall()]
