import sqlite3
from typing import List

from constants import *
from exceptions import SensorModelDoesNotExist
from project_settings import ProjectSettings


SQL_INSERT_MODEL = (
    "INSERT INTO sensor_model("
    + MODEL_NAME + ","
    + DATE_ROW + "," + TIME_ROW + "," + TIMESTAMP_COLUMN + ","
    + RELATIVE_ABSOLUTE + "," + TIMESTAMP_UNIT + "," + FORMAT_STRING + ","
    + SENSOR_ID_ROW + "," + SENSOR_ID_COLUMN + "," + SENSOR_ID_REGEX + ","
    + HEADERS_ROW + "," + COMMENT_STYLE +
    ") VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
)
SQL_UPDATE_MODEL = (
    "UPDATE sensor_model "
    "SET " + MODEL_NAME + " = ?,"
    + DATE_ROW + " =  ?," + TIME_ROW + " =  ?," + TIMESTAMP_COLUMN + " =  ?,"
    + RELATIVE_ABSOLUTE + " =  ?," + TIMESTAMP_UNIT + " =  ?," + FORMAT_STRING + " =  ?,"
    + SENSOR_ID_ROW + " =  ?," + SENSOR_ID_COLUMN + " =  ?," + SENSOR_ID_REGEX + " =  ?,"
    + HEADERS_ROW + " =  ?," + COMMENT_STYLE + " =  ?"
    + "WHERE id = ?"
)

# model_name = ?, "
# "date_row = ?, time_row = ?, "
# "sensor_id_row = ?, sensor_id_column = ?, sensor_id_regex = ?, "
# "headers_row = ?, "
# "comment_style = ? "

SQL_SELECT_ALL_MODELS = (
    "SELECT id, model_name "
    "FROM sensor_model"
)
SQL_SELECT_ID = (
    "SELECT id "
    "FROM sensor_model "
    "WHERE model_name = ?"
)
SQL_SELECT_MODEL_BY_ID = (
    "SELECT * "
    "FROM sensor_model "
    "WHERE id = ?"
)
SQL_SELECT_NAME = (
    "SELECT model_name "
    "FROM sensor_model "
    "WHERE id = ?"
)
SQL_SELECT_DATE_CONFIG = (
    "SELECT date_row "
    "FROM sensor_model "
    "WHERE id = ?"
)
SQL_SELECT_TIME_CONFIG = (
    "SELECT time_row "
    "FROM sensor_model "
    "WHERE id = ?"
)
SQL_SELECT_SENSOR_CONFIG = (
    "SELECT sensor_id_row, sensor_id_column, sensor_id_regex "
    "FROM sensor_model "
    "WHERE id = ?"
)
SQL_SELECT_HEADERS_CONFIG = (
    "SELECT headers_row "
    "FROM sensor_model "
    "WHERE id = ?"
)
SQL_DELETE_MODEL_BY_ID = (
    "DELETE FROM sensor_model "
    "WHERE id = ?"
)


class SensorModelManager:

    def __init__(self, settings: ProjectSettings):
        self._conn = sqlite3.connect(
            settings.database_file.as_posix(),
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        # Enable Sqlite foreign key support
        self._conn.execute("PRAGMA foreign_keys = 1")

        self._conn.row_factory = sqlite3.Row
        self._cur = self._conn.cursor()

    def get_id_by_name(self, model_name: str) -> int:
        self._cur.execute(SQL_SELECT_ID, (model_name,))
        res = self._cur.fetchone()

        if res is None:
            raise SensorModelDoesNotExist(model_name)

        return res[0]

    def get_all_models(self) -> List[sqlite3.Row]:
        try:
            self._cur.execute(SQL_SELECT_ALL_MODELS)
            return self._cur.fetchall()
        except sqlite3.Error:
            return []

    def get_model_by_id(self, model_id):
        try:
            self._cur.execute(SQL_SELECT_MODEL_BY_ID, (model_id,))
            return self._cur.fetchone()
        except sqlite3.Error:
            return None

    def get_sensor_model_name(self, id_: int) -> str:
        try:
            self._cur.execute(SQL_SELECT_ID, (id_,))
            return self._cur.fetchone()
        except sqlite3.Error:
            return ""

    def get_date_config(self, model_id: int):
        try:
            self._cur.execute(SQL_SELECT_DATE_CONFIG, (model_id,))
            return self._cur.fetchone()
        except sqlite3.Error:
            return None

    def get_time_config(self, model_id: int):
        try:
            self._cur.execute(SQL_SELECT_TIME_CONFIG, (model_id,))
            return self._cur.fetchone()
        except sqlite3.Error:
            return None

    def get_sensor_id_config(self, model_id: int):
        try:
            self._cur.execute(SQL_SELECT_SENSOR_CONFIG, (model_id,))
            return self._cur.fetchone()
        except sqlite3.Error:
            return None

    def get_headers_config(self, model_id: int):
        try:
            self._cur.execute(SQL_SELECT_HEADERS_CONFIG, (model_id,))
            return self._cur.fetchone()
        except sqlite3.Error:
            return None

    def insert_sensor_model(self, model_name: str, date_row: int, time_row: int, timestamp_column: int,
                            relative_absolute: str, timestamp_unit: str, format_string: str, sensor_id_row: int,
                            sensor_id_col: int, sensor_id_regex: str, headers_row: int, comment_style: str) -> int:
        try:
            self._cur.execute(SQL_INSERT_MODEL, (model_name, date_row, time_row, timestamp_column, relative_absolute,
                                                 timestamp_unit, format_string, sensor_id_row, sensor_id_col,
                                                 sensor_id_regex, headers_row, comment_style))
            self._conn.commit()
            return self.get_id_by_name(model_name)
        except sqlite3.Error:
            return -1

    def update_sensor_model(self, model_id: int, model_name: str, date_row: int, time_row: int, timestamp_column: int,
                            relative_absolute: str, timestamp_unit: str, format_string: str, sensor_id_row: int,
                            sensor_id_col: int, sensor_id_regex: str, headers_row: int, comment_style: str):
        try:
            self._cur.execute(SQL_UPDATE_MODEL, (model_name, date_row, time_row, timestamp_column, relative_absolute,
                                                 timestamp_unit, format_string, sensor_id_row, sensor_id_col,
                                                 sensor_id_regex, headers_row, comment_style, model_id))
            self._conn.commit()
            return self.get_id_by_name(model_name)
        except sqlite3.Error:
            return -1

    def delete_sensor_model_by_id(self, model_id: int):
        try:
            self._cur.execute(SQL_DELETE_MODEL_BY_ID, (model_id,))
            self._conn.commit()
            return True
        except sqlite3.Error:
            return False
