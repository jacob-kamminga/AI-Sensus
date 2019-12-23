import sqlite3
from datetime import date
from statistics import mean

sql_queryDate = "SELECT offset FROM offset WHERE camera = ? AND sensor = ? AND added = ?"
sql_queryNoDate = "SELECT offset FROM offset WHERE camera = ? AND sensor = ? ORDER BY added DESC"
sql_insertOffset = "INSERT INTO offset(camera, sensor, offset, added) VALUES (?, ?, ?, ?)"
sql_updateOffset = "UPDATE offset SET offset = ? WHERE camera = ? AND sensor = ? AND added = ?"


class OffsetManager:

    def __init__(self, project_name: str):
        self._conn = sqlite3.connect('projects/' + project_name + '/project_data.db',
                                     detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self._cur = self._conn.cursor()

    def create_table(self) -> None:
        """Method for creating the necessary offset table in the database."""
        self._cur.execute("CREATE TABLE offsets (camera TEXT, sensor TEXT, offset REAL, added TIMESTAMP,"
                          "PRIMARY KEY (camera, sensor, added), FOREIGN KEY (camera) REFERENCES camera(name))")
        self._conn.commit()

    def get_offset(self, cam_id: str, sens_id: str, added: date) -> float:
        """
        Returns the offset between a camera and sensor on a given date.
        If there is no known offset for the given date, then the offset of the most recent known date is returned.
        If no offset is known at all between the given camera and sensor, then a default offset of 0 is returned.

        :param cam_id: The name of the camera
        :param sens_id: The sensor ID of the sensor
        :param added: The date of the offset
        :return: float: The offset between camera and sensor
        """
        c = self._cur
        c.execute(sql_queryDate, (cam_id, sens_id, added))
        results = [x[0] for x in c.fetchall()]

        # If there is a known offset, return it
        if len(results) != 0:
            return results[0]

        # Otherwise check again without date and return the most recent offset, or 0 if no offset is known at all
        c.execute(sql_queryNoDate, (cam_id, sens_id))
        results = [x[0] for x in c.fetchall()]

        if len(results) == 0:
            # Camera-Sensor combination unknown; add to table with offset 0
            c.execute(sql_insertOffset, (cam_id, sens_id, 0, added))
            self._conn.commit()
            return 0

        # Camera-Sensor combination known
        res = results[0]
        c.execute(sql_insertOffset, (cam_id, sens_id, res, added))
        self._conn.commit()
        return res

    def set_offset(self, cam_id: str, sens_id: str, offset: float, added: date) -> None:
        """
        Changes the offset between a camera and sensor.

        :param cam_id: The name of the camera
        :param sens_id: The sensor ID of the sensor
        :param offset: The new offset value
        :param added: The date that the offset was added
        """
        self._cur.execute(sql_updateOffset, (offset, cam_id, sens_id, added))
        self._conn.commit()
