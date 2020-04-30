import sqlite3
from datetime import datetime
from typing import List, Tuple

from database import settings

SQL_CREATE_TABLE = "create table sensor_data_file\
(\
    id        INTEGER not null\
        constraint sensor_data_files_pk\
            primary key autoincrement,\
    file_name TEXT    not null,\
    file_path TEXT,\
    sensor_id INTEGER\
        references sensor,\
    datetime  TIMESTAMP\
);\
\
create unique index sensor_data_files_file_name_uindex\
    on sensor_data_file (file_name);"

SQL_DELETE_MAP = "DELETE FROM subject_sensor_map WHERE id = ?"
SQL_INSERT_MAP = "INSERT INTO subject_sensor_map (subject_id, sensor_id, start_datetime, end_datetime) VALUES " \
                 "(?, ?, ?, ?)"

SQL_SELECT_ALL_MAPS = "SELECT * FROM subject_sensor_map"
SQL_SELECT_SENSOR_IDS_BETWEEN_DATES = "SELECT sensor_id " \
                                      "FROM subject_sensor_map " \
                                      "WHERE subject_id = ? " \
                                      "AND (? BETWEEN start_datetime AND end_datetime " \
                                      "OR ? BETWEEN start_datetime AND end_datetime " \
                                      "OR start_datetime BETWEEN ? AND ? " \
                                      "OR end_datetime BETWEEN ? AND ?)"
SQL_UPDATE_MAP = "UPDATE subject_sensor_map SET subject_id = ?, sensor_id = ?, start_datetime = ?, end_datetime = ? " \
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
        self._cur.execute(SQL_INSERT_MAP, (subject_id, sensor_id, start_date, end_date))
        self._conn.commit()

    def get_all_maps(self) -> List[Tuple[str]]:
        self._cur.execute(SQL_SELECT_ALL_MAPS)
        return self._cur.fetchall()

    def get_sensor_ids_by_dates(self, subject_id: [int], start_dt: datetime, end_dt: datetime):
        self._cur.execute(
            SQL_SELECT_SENSOR_IDS_BETWEEN_DATES,
            (subject_id, start_dt, end_dt, start_dt, end_dt, start_dt, end_dt)
        )
        return [row[0] for row in self._cur.fetchall()]

    def delete_map(self, id_: int) -> None:
        """
        Removes a subject from the table.

        :param id_: The ID of the map to delete
        """
        self._cur.execute(SQL_DELETE_MAP, (id_,))
        self._conn.commit()

    def update_map(self, name_old: str, name_new: str) -> None:
        """
        Changes the name of a subject.

        :param name_old: name that should be changed
        :param name_new: name that it should be changed to
        """
        self._cur.execute(SQL_UPDATE_MAP, (name_new, name_old))
        self._conn.commit()

    def update_start_date(self, id_: int, start_date: datetime) -> None:
        """
        Changes the start date for a map.

        :param id_: The ID of the map
        :param start_date: The start date
        """
        self._cur.execute(SQL_UPDATE_START_DATE, (start_date, id_))
        self._conn.commit()

    def update_end_date(self, id_: int, end_date: datetime) -> None:
        """
        Changes the end date for a map.

        :param id_: The ID of the map
        :param end_date: The end date
        """
        self._cur.execute(SQL_UPDATE_END_DATE, (end_date, id_))
        self._conn.commit()
