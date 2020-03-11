import os.path
import sqlite3
from database import settings
from datetime import datetime
from typing import Any, List
from data_import.sensor_data import SensorData
import pandas as pd

SQL_CREATE_TABLE = "create table subject_sensor_map\
(\
    subject_id INTEGER,\
    sensor_id  INTEGER   not null,\
    start_date TIMESTAMP not null,\
    end_date   TIMESTAMP not null,\
    id         INTEGER\
        constraint subject_sensor_map_pk\
            primary key\
);\
\
create unique index subject_sensor_map_subject_id_start_date_uindex\
    on subject_sensor_map (subject_id, start_date);"

SQL_DELETE_map = "DELETE FROM subject_sensor_map WHERE id = ?"
SQL_INSERT_map = "INSERT INTO subject_sensor_map (subject_id, sensor_id, start_datetime, end_datetime) VALUES (?, ?, ?, ?)"

SQL_SELECT_ALL_MAPS = "SELECT * FROM subject_sensor_map"
SQL_UPDATE_map = "UPDATE subject_sensor_map SET subject_id = ?, sensor_id = ?, start_datetime = ?, end_datetime = ? " \
                 "WHERE id = ?"
SQL_UPDATE_START_DATE = "UPDATE subject_sensor_map SET start_datetime = ? WHERE id = ?"
SQL_UPDATE_END_DATE = "UPDATE subject_sensor_map SET end_datetime = ? WHERE id = ?"

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


class SubjectSensorMapManager:

    def __init__(self, project_name: str):
        """
        :param project_name: The name of the current project
        """
        self.project_name = project_name
        self._conn = sqlite3.connect('projects/' + project_name + '/project_data.db',
                                     detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self._cur = self._conn.cursor()
        self.settings = settings.Settings(project_name)

    def create_table(self) -> None:
        """Method for creating the necessary subject map table."""
        self._cur.execute(SQL_CREATE_TABLE)
        self._conn.commit()

    def add_map(self, subject_id: int, sensor_id: int, start_date: datetime, end_date: datetime) -> None:
        """
        Adds a new subject.

        :param subject_id:
        :param sensor_id:
        :param start_date:
        :param end_date:
        """
        self._cur.execute(SQL_INSERT_map, (subject_id, sensor_id, start_date, end_date))
        self._conn.commit()

    def get_all_maps(self) -> List[str]:
        self._cur.execute(SQL_SELECT_ALL_MAPS)
        return self._cur.fetchall()

    def delete_map(self, id: int) -> None:
        """
        Removes a subject from the table.

        :param id: The ID of the map to delete
        """
        self._cur.execute(SQL_DELETE_map, (id,))
        self._conn.commit()

    def update_map(self, name_old: str, name_new: str) -> None:
        """
        Changes the name of a subject.

        :param name_old: name that should be changed
        :param name_new: name that it should be changed to
        """
        self._cur.execute(SQL_UPDATE_map, (name_new, name_old))
        self._conn.commit()

    def update_start_date(self, id: int, start_date: datetime) -> None:
        """
        Changes the start date for a map.

        :param id: The ID of the map
        :param start_date: The start date
        """
        self._cur.execute(SQL_UPDATE_START_DATE, (start_date, id))
        self._conn.commit()

    def update_end_date(self, id: int, end_date: datetime) -> None:
        """
        Changes the end date for a map.

        :param id: The ID of the map
        :param end_date: The end date
        """
        self._cur.execute(SQL_UPDATE_END_DATE, (end_date, id))
        self._conn.commit()
