import sqlite3
from datetime import datetime
from typing import List

SQL_CREATE_TABLE = "create table sensor_data_file\
(\
  id        INTEGER not null\
    constraint sensor_data_file_pk\
      primary key autoincrement,\
  file_name TEXT    not null,\
  file_path TEXT,\
  sensor_id INTEGER,\
  datetime  TIMESTAMP\
);\
\
create unique index sensor_data_file_file_name_uindex\
  on sensor_data_file (file_name);"

SQL_INSERT_FILE = \
    "INSERT INTO sensor_data_file(file_name, file_path, sensor_id, datetime) VALUES (?, ?, ?, ?)"

SQL_SELECT_ID_BY_FILE_NAME = \
    "SELECT id " \
    "FROM sensor_data_file " \
    "WHERE file_name = ?"

SQL_SELECT_FILE_NAMES_BY_SENSOR_ID = \
    "SELECT file_name " \
    "FROM sensor_data_file " \
    "WHERE sensor_id = ? " \
    "AND (datetime BETWEEN ? AND ?)"

SQL_SELECT_SENSOR_IDS = \
    "SELECT sensor_id FROM sensor_data_file"

SQL_SELECT_FILE_PATH_BY_FILE_NAME = \
    "SELECT file_path " \
    "FROM sensor_data_file " \
    "WHERE file_name = ?"

SQL_UPDATE_FILE_PATH = \
    "UPDATE sensor_data_file " \
    "SET file_path = ? " \
    "WHERE file_name = ?"


class SensorDataFileManager:
    def __init__(self, project_name: str):
        """
        :param project_name: The name of the current project
        """
        self.project_name = project_name
        self._conn = sqlite3.connect('projects/' + project_name + '/project_data.db',
                                     detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self._cur = self._conn.cursor()

    def create_table(self):
        self._cur.execute(SQL_CREATE_TABLE)
        self._conn.commit()

    def get_id_by_file_name(self, file_name: str) -> int:
        """
        Return the ID of the sensor data file, or -1 if not exists.

        :param file_name: The base name of the file
        :return: The ID of the sensor data file, or -1 if not exists
        """
        try:
            self._cur.execute(SQL_SELECT_ID_BY_FILE_NAME, (file_name,))
            return self._cur.fetchone()[0]
        except sqlite3.Error:
            return -1

    def add_file(self, file_name: str, file_path: str, sensor_id: int, datetime_: datetime) -> int:
        """
        Add a new file mapping.

        :param file_name: The file name
        :param file_path: The last known file path
        :param sensor_id: The sensor ID
        :param datetime_: datetime of the data-file
        """
        self._cur.execute(SQL_INSERT_FILE, (file_name, file_path, sensor_id, datetime_))
        self._conn.commit()
        return self._cur.lastrowid

    def update_file_path(self, file_name: str, file_path: str):
        """
        Update the last known file path of a sensor data file.

        :param file_name: The file name
        :param file_path: The file path
        """
        self._cur.execute(SQL_UPDATE_FILE_PATH, (file_path, file_name))
        self._conn.commit()

    def get_file_path_by_file_name(self, file_name: str):
        """
        Get the file path of the sensor data file indicated by the file name.

        :param file_name: The file name
        :return: The file path
        """
        self._cur.execute(SQL_SELECT_FILE_PATH_BY_FILE_NAME, (file_name,))
        return self._cur.fetchone()[0]

    def get_file_names_between_dates(self, sensor_id: int, start_date: datetime, end_date: datetime) -> List[str]:
        """
        Returns all file names for a given sensor between two dates.

        :param sensor_id: sensor id
        :param start_date: start date
        :param end_date: end date
        :return: list of file names
        """
        self._cur.execute(SQL_SELECT_FILE_NAMES_BY_SENSOR_ID, (sensor_id, start_date, end_date))
        return [x[0] for x in self._cur.fetchall()]

    def get_sensor_ids(self) -> List[str]:
        """
        Returns a list of all sensor ids that have been used so far in this project.

        :return: list of sensor ids
        """
        self._cur.execute(SQL_SELECT_SENSOR_IDS)
        return [x[0] for x in self._cur.fetchall()]
