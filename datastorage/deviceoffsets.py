import sqlite3
from datetime import date
from statistics import mean

sql_queryDate = "SELECT Offset FROM offsets WHERE Camera = ? AND Sensor = ? AND Date = ?"
sql_queryNoDate = "SELECT Offset FROM offsets WHERE Camera = ? AND Sensor = ? ORDER BY Date DESC"
sql_insertOffset = "INSERT INTO offsets(Camera, Sensor, Offset, Date) VALUES (?, ?, ?, ?)"
sql_updateOffset = "UPDATE Offsets SET Offset = ? WHERE Camera = ? AND Sensor = ? AND Date = ?"


class OffsetManager:

    def __init__(self):
        self._conn = sqlite3.connect('data.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self._cur = self._conn.cursor()

    def create_table(self) -> None:
        """Method for creating the necessary offset table in the database."""
        self._cur.execute("CREATE TABLE offsets (Camera TEXT, Sensor TEXT, Offset REAL, Date TIMESTAMP,"
                          "PRIMARY KEY (Camera, Sensor, Date), FOREIGN KEY (Camera) REFERENCES cameras(Name))")
        self._conn.commit()

    def get_offset(self, cam_id: str, sens_id: str, date: date) -> float:
        """
        Returns the offset between a camera and sensor on a given date.
        If there is no known offset for the given date, then the offset of the most recent known date is returned.
        If no offset is known at all between the given camera and sensor, then a default offset of 0 is returned.

        :param cam_id: The name of the camera
        :param sens_id: The sensor ID of the sensor
        :param date: The date of the offset
        :return: float: The offset between camera and sensor
        """
        c = self._cur
        c.execute(sql_queryDate, (cam_id, sens_id, date))
        results = [x[0] for x in c.fetchall()]

        # If there is a known offset, return it
        if len(results) != 0:
            return results[0]

        # Otherwise check again without date and return the most recent offset, or 0 if no offset is known at all
        c.execute(sql_queryNoDate, (cam_id, sens_id))
        results = [x[0] for x in c.fetchall()]

        if len(results) == 0:
            # Camera-Sensor combination unknown; add to table with offset 0
            c.execute(sql_insertOffset, (cam_id, sens_id, 0, date))
            self._conn.commit()
            return 0

        # Camera-Sensor combination known
        res = results[0]
        c.execute(sql_insertOffset, (cam_id, sens_id, res, date))
        self._conn.commit()
        return res

    def set_offset(self, cam_id: str, sens_id: str, offset: float, date: date) -> None:
        """
        Changes the offset between a camera and sensor.

        :param cam_id: The name of the camera
        :param sens_id: The sensor ID of the sensor
        :param offset: The new offset value
        :param date: The date of the offset
        """
        self._cur.execute(sql_updateOffset, (offset, cam_id, sens_id, date))
        self._conn.commit()
