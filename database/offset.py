import sqlite3
from datetime import date

SQL_CREATE_TABLE = "create table offset \
( \
  camera_id INTEGER     not null, \
  sensor_id VARCHAR(50) not null, \
  offset    DOUBLE      not null, \
  added     DATE        not null, \
  constraint offset_pk \
    unique (camera_id, sensor_id) \
);"
SQL_QUERY_DATE = "SELECT offset FROM offset WHERE camera_id = ? AND sensor_id = ? AND added = ?"
SQL_QUERY_NO_DATE = "SELECT offset FROM offset WHERE camera_id = ? AND sensor_id = ? ORDER BY added DESC"
SQL_REPLACE_OFFSET = "REPLACE INTO offset(camera_id, sensor_id, offset, added) VALUES (?, ?, ?, ?)"
SQL_UPDATE_OFFSET = "UPDATE offset SET offset = ? WHERE camera_id = ? AND sensor_id = ? AND added = ?"


class OffsetManager:

    def __init__(self, project_name: str):
        self._conn = sqlite3.connect('projects/' + project_name + '/project_data.db',
                                     detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self._cur = self._conn.cursor()

    def create_table(self) -> None:
        """Method for creating the necessary offset table in the database."""
        self._cur.execute(SQL_CREATE_TABLE)
        self._conn.commit()

    def get_offset(self, camera_id: int, sensor_id: int, added: date) -> float:
        """
        Returns the offset between a camera and sensor on a given date.
        If there is no known offset for the given date, then the offset of the most recent known date is returned.
        If no offset is known at all between the given camera and sensor, then a default offset of 0 is returned.

        :param camera_id: The name of the camera
        :param sensor_id: The sensor ID of the sensor
        :param added: The date of the offset
        :return: float: The offset between camera and sensor
        """
        c = self._cur
        c.execute(SQL_QUERY_DATE, (camera_id, sensor_id, added))
        results = [x[0] for x in c.fetchall()]

        # If there is a known offset, return it
        if len(results) != 0:
            return results[0]

        # Otherwise check again without date and return the most recent offset, or 0 if no offset is known at all
        c.execute(SQL_QUERY_NO_DATE, (camera_id, sensor_id))
        results = [x[0] for x in c.fetchall()]

        if len(results) == 0:
            # Camera-sensor combination unknown; add to table with offset 0
            c.execute(SQL_REPLACE_OFFSET, (camera_id, sensor_id, 0, added))
            self._conn.commit()
            return 0

        # Camera-Sensor combination known
        res = results[0]
        c.execute(SQL_REPLACE_OFFSET, (camera_id, sensor_id, res, added))
        self._conn.commit()
        return res

    def set_offset(self, camera_id: str, sensor_id: str, offset: float, added: date) -> None:
        """
        Changes the offset between a camera and sensor.

        :param camera_id: The name of the camera
        :param sensor_id: The sensor ID of the sensor
        :param offset: The new offset value
        :param added: The date that the offset was added
        """
        self._cur.execute(SQL_UPDATE_OFFSET, (offset, camera_id, sensor_id, added))
        self._conn.commit()
