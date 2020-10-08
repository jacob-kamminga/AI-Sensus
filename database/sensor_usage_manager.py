import datetime as dt
import sqlite3
from typing import List, Tuple

from project_settings import ProjectSettingsDialog

SQL_CREATE_TABLE = "create table sensor_usage \
( \
    id             INTEGER \
        constraint subject_sensor_map_pk \
            primary key, \
    subject_id     INTEGER  not null, \
    sensor_id      INTEGER  not null, \
    start_datetime DATETIME not null, \
    end_datetime   DATETIME not null \
); \
\
create unique index subject_sensor_map_subject_id_start_datetime_uindex \
    on sensor_usage (subject_id, start_datetime);"

SQL_DELETE_MAP = \
    "DELETE FROM sensor_usage " \
    "WHERE id = ?"
SQL_INSERT_MAP = \
    "INSERT INTO sensor_usage (subject_id, sensor_id, start_datetime, end_datetime) " \
    "VALUES (?, ?, ?, ?)"

SQL_SELECT_ALL_MAPS = \
    "SELECT * " \
    "FROM sensor_usage"
SQL_SELECT_MAP_BY_ID = \
    "SELECT * " \
    "FROM sensor_usage " \
    "WHERE id = ?"
SQL_SELECT_SENSOR_IDS_BETWEEN_DATES = \
    "SELECT sensor_id " \
    "FROM sensor_usage " \
    "WHERE subject_id = ? " \
    "AND (? BETWEEN start_datetime AND end_datetime " \
    "OR ? BETWEEN start_datetime AND end_datetime " \
    "OR start_datetime BETWEEN ? AND ? " \
    "OR end_datetime BETWEEN ? AND ?)"
SQL_UPDATE_MAP = \
    "UPDATE sensor_usage " \
    "SET subject_id = ?, sensor_id = ?, start_datetime = ?, end_datetime = ? " \
    "WHERE id = ?"
SQL_UPDATE_START_DATE = \
    "UPDATE sensor_usage " \
    "SET start_datetime = ? " \
    "WHERE id = ?"
SQL_UPDATE_END_DATE = \
    "UPDATE sensor_usage " \
    "SET end_datetime = ? " \
    "WHERE id = ?"

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


class SensorUsageManager:

    def __init__(self, settings: ProjectSettingsDialog):
        self._conn = sqlite3.connect(
            settings.database_file.as_posix(),
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        # Enable Sqlite foreign key support
        self._conn.execute("PRAGMA foreign_keys = 1")

        self._cur = self._conn.cursor()

    def create_table(self) -> None:
        """Method for creating the necessary subject map table."""
        self._cur.executescript(SQL_CREATE_TABLE)
        self._conn.commit()

    def add_usage(self, subject_id: int, sensor_id: int, start_date: dt.datetime, end_date: dt.datetime) -> None:
        """
        Adds a new subject.

        :param subject_id:
        :param sensor_id:
        :param start_date:
        :param end_date:
        """
        self._cur.execute(SQL_INSERT_MAP, (subject_id, sensor_id, start_date, end_date))
        self._conn.commit()

    def get_all_usages(self) -> List[Tuple[str]]:
        self._cur.execute(SQL_SELECT_ALL_MAPS)
        return self._cur.fetchall()

    def get_usage_by_id(self, map_id: int) -> List[Tuple[str]]:
        self._cur.execute(SQL_SELECT_MAP_BY_ID, (map_id,))
        return self._cur.fetchall()

    def get_sensor_ids_by_dates(self, subject_id: [int], start_dt: dt.datetime, end_dt: dt.datetime):
        self._cur.execute(
            SQL_SELECT_SENSOR_IDS_BETWEEN_DATES,
            (subject_id, start_dt, end_dt, start_dt, end_dt, start_dt, end_dt)
        )
        return [row[0] for row in self._cur.fetchall()]

    def delete_usage(self, id_: int) -> None:
        """
        Removes a subject from the table.

        :param id_: The ID of the map to delete
        """
        self._cur.execute(SQL_DELETE_MAP, (id_,))
        self._conn.commit()

    def update_usage(
            self,
            id_: int,
            subject_id: int,
            sensor_id: int,
            start_dt: dt.datetime,
            end_dt: dt.datetime
    ) -> None:
        """
        Changes the name of a subject.

        :param id_:
        :param subject_id:
        :param sensor_id:
        :param start_dt:
        :param end_dt:
        """
        self._cur.execute(SQL_UPDATE_MAP, (subject_id, sensor_id, start_dt, end_dt, id_))
        self._conn.commit()

    def update_start_date(self, id_: int, start_date: dt.datetime) -> None:
        """
        Changes the start date for a map.

        :param id_: The ID of the map
        :param start_date: The start date
        """
        self._cur.execute(SQL_UPDATE_START_DATE, (start_date, id_))
        self._conn.commit()

    def update_end_date(self, id_: int, end_date: dt.datetime) -> None:
        """
        Changes the end date for a map.

        :param id_: The ID of the map
        :param end_date: The end date
        """
        self._cur.execute(SQL_UPDATE_END_DATE, (end_date, id_))
        self._conn.commit()
