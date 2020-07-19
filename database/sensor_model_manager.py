import sqlite3
from typing import List

from exceptions import SensorModelDoesNotExist
from project_settings import ProjectSettings

SQL_CREATE_TABLE = "create table sensor_model \
( \
    id               INTEGER \
        constraint sensor_model_pk \
            primary key autoincrement, \
    model_name       VARCHAR(50) not null, \
    date_format      TEXT        not null, \
    date_row         INTEGER     not null, \
    date_column      INTEGER, \
    date_regex       TEXT, \
    time_format      TEXT        not null, \
    time_row         INTEGER     not null, \
    time_column      INTEGER, \
    time_regex       TEXT, \
    sensor_id_row    INTEGER     not null, \
    sensor_id_column INTEGER, \
    sensor_id_regex  TEXT, \
    headers_row      INTEGER     not null, \
    comment_style    TEXT        not null \
); \
 \
create unique index sensor_model_name_uindex \
    on sensor_model (model_name);"

SQL_INSERT_MODEL = (
    "INSERT INTO sensor_model("
    "model_name, "
    "date_format, date_row, date_column, date_regex, "
    "time_format, time_row, time_column, time_regex, "
    "sensor_id_row, sensor_id_column, sensor_id_regex, "
    "headers_row, "
    "comment_style)"
    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
)
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
    "SELECT date_format, date_row, date_column, date_regex "
    "FROM sensor_model "
    "WHERE id = ?"
)
SQL_SELECT_TIME_CONFIG = (
    "SELECT time_format, time_row, time_column, time_regex "
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
SQL_UPDATE_MODEL = (
    "UPDATE sensor_model "
    "SET model_name = ?, "
    "date_format = ?, date_row = ?, date_column = ?, date_regex = ?, "
    "time_format = ?, time_row = ?, time_column = ?, time_regex = ?, "
    "sensor_id_row = ?, sensor_id_column = ?, sensor_id_regex = ?, "
    "headers_row = ?, "
    "comment_style = ? "
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
        self._conn.row_factory = sqlite3.Row
        self._cur = self._conn.cursor()

    def create_table(self) -> bool:
        """Method for creating the necessary label tables in the database."""
        try:
            c = self._conn.cursor()
            c.execute(SQL_CREATE_TABLE)
            self._conn.commit()
            return True
        except sqlite3.Error:
            return False

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

    def insert_sensor_model(
            self,
            model_name: str,
            date_format: str,
            date_row: int,
            date_col: int,
            date_regex: str,
            time_format: str,
            time_row: int,
            time_col: int,
            time_regex: str,
            sensor_id_row: int,
            sensor_id_col: int,
            sensor_id_regex: str,
            headers_row: int,
            comment_style: str
    ) -> int:
        try:
            self._cur.execute(SQL_INSERT_MODEL, (
                model_name,
                date_format,
                date_row,
                date_col,
                date_regex,
                time_format,
                time_row,
                time_col,
                time_regex,
                sensor_id_row,
                sensor_id_col,
                sensor_id_regex,
                headers_row,
                comment_style
            ))
            self._conn.commit()
            return self.get_id_by_name(model_name)
        except sqlite3.Error:
            return -1

    def update_sensor_model(
            self,
            model_id: int,
            model_name: str,
            date_format: str,
            date_row: int,
            date_col: int,
            date_regex: str,
            time_format: str,
            time_row: int,
            time_col: int,
            time_regex: str,
            sensor_id_row: int,
            sensor_id_col: int,
            sensor_id_regex: str,
            headers_row: int,
            comment_style: str
    ):
        try:
            self._cur.execute(SQL_UPDATE_MODEL, (
                model_name,
                date_format,
                date_row,
                date_col,
                date_regex,
                time_format,
                time_row,
                time_col,
                time_regex,
                sensor_id_row,
                sensor_id_col,
                sensor_id_regex,
                headers_row,
                comment_style,
                model_id
            ))
            self._conn.commit()
            return self.get_id_by_name(model_name)
        except sqlite3.Error:
            return -1

    def delete_sensor_model_by_id(self, sensor_id: int):
        try:
            self._cur.execute(SQL_DELETE_MODEL_BY_ID, (sensor_id,))
            self._conn.commit()
            return True
        except sqlite3.Error:
            return False
