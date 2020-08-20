import sqlite3
from typing import List

from project_settings import ProjectSettings


SQL_INSERT_SENSOR = \
    "INSERT INTO sensor(name, model) " \
    "VALUES (?,?)"
SQL_SELECT_ALL_SENSORS = \
    "SELECT * " \
    "FROM sensor"
SQL_SELECT_ID = \
    "SELECT id " \
    "FROM sensor " \
    "WHERE name = ?"
SQL_SELECT_SENSOR_NAME = \
    "SELECT name " \
    "FROM sensor " \
    "WHERE id = ?"
SQL_UPDATE_NAME_BY_ID = \
    "UPDATE sensor " \
    "SET name = ? " \
    "WHERE id = ?"
SQL_DELETE_SENSOR_BY_ID = \
    "DELETE FROM sensor " \
    "WHERE id = ?"


class SensorManager:

    def __init__(self, settings: ProjectSettings):
        self._conn = sqlite3.connect(
            settings.database_file.as_posix(),
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        # Enable Sqlite foreign key support
        self._conn.execute("PRAGMA foreign_keys = 1")

        self._cur = self._conn.cursor()

    def get_id_by_name(self, sensor_name: str) -> int:
        self._cur.execute(SQL_SELECT_ID, (sensor_name,))
        res = self._cur.fetchone()

        if res is None:
            return -1

        return res[0]

    def get_all_sensors(self) -> List[str]:
        try:
            self._cur.execute(SQL_SELECT_ALL_SENSORS)
            return self._cur.fetchall()
        except sqlite3.Error:
            return ["error"]

    def get_sensor_name(self, id_: int) -> str:
        try:
            self._cur.execute(SQL_SELECT_ID, (id_,))
            return self._cur.fetchone()[0]
        except sqlite3.Error:
            return ""

    def insert_sensor(self, sensor_name: str, model_id) -> int:
        try:
            self._cur.execute(SQL_INSERT_SENSOR, (sensor_name, model_id))
            self._conn.commit()
            return self.get_id_by_name(sensor_name)
        except sqlite3.Error:
            print('Insert sensor ERROR')
            return -1

    def update_name_by_id(self, sensor_id, sensor_name):
        try:
            self._cur.execute(SQL_UPDATE_NAME_BY_ID, (sensor_name, sensor_id))
            self._conn.commit()
            return True
        except sqlite3.Error:
            return False

    def delete_sensor_by_id(self, sensor_id: int):
        try:
            self._cur.execute(SQL_DELETE_SENSOR_BY_ID, (sensor_id,))
            self._conn.commit()
            return True
        except sqlite3.Error:
            return False
