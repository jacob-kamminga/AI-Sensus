import datetime as dt
import sqlite3
from typing import List

from gui.dialogs.project_settings import ProjectSettingsDialog


SQL_INSERT_FILE = (
    "INSERT INTO sensor_data_file(file_name, file_path, sensor_id, datetime) "
    "VALUES (?, ?, ?, ?)"
)
SQL_SELECT_ID_BY_FILE_NAME = (
    "SELECT id "
    "FROM sensor_data_file "
    "WHERE file_name = ?"
)
SQL_SELECT_ID_BY_FILE_PATH = (
    "SELECT id "
    "FROM sensor_data_file "
    "WHERE file_path = ?"
)
SQL_SELECT_SENSOR_MODEL_BY_FILE_NAME = (
    "SELECT sensor_model.id "
    "FROM sensor_data_file, sensor, sensor_model "
    "WHERE sensor_data_file.file_name = ? "
    "AND sensor_data_file.sensor_id = sensor.id "
    "AND sensor.model = sensor_model.id"
)
SQL_SELECT_SENSOR_MODEL_BY_FILE_PATH = (
    "SELECT sensor_model.id "
    "FROM sensor_data_file, sensor, sensor_model "
    "WHERE sensor_data_file.file_path = ? "
    "AND sensor_data_file.sensor_id = sensor.id "
    "AND sensor.model = sensor_model.id"
)
SQL_SELECT_SENSOR_MODEL_BY_ID = (
    "SELECT sensor_model.id "
    "FROM sensor_data_file, sensor, sensor_model "
    "WHERE sensor_data_file.id = ? "
    "AND sensor_data_file.sensor_id = sensor.id "
    "AND sensor.model = sensor_model.id"
)
SQL_SELECT_FILE_NAME_BY_ID = (
    "SELECT file_name "
    "FROM sensor_data_file "
    "WHERE id = ?"
)
SQL_SELECT_FILE_PATH_BY_ID = (
    "SELECT file_path "
    "FROM sensor_data_file "
    "WHERE id = ?"
)
SQL_SELECT_IDS_BY_SENSOR_AND_DATES = (
    "SELECT id "
    "FROM sensor_data_file "
    "WHERE sensor_id = ? "
    "AND (datetime BETWEEN ? AND ?)"
)
SQL_SELECT_SENSOR_IDS = (
    "SELECT sensor_id "
    "FROM sensor_data_file"
)
SQL_SELECT_SENSOR_BY_ID = (
    "SELECT sensor_id "
    "FROM sensor_data_file "
    "WHERE id = ?"
)
SQL_SELECT_FILE_PATH_BY_FILE_NAME = (
    "SELECT file_path "
    "FROM sensor_data_file "
    "WHERE file_name = ?"
)
SQL_UPDATE_FILE_PATH = (
    "UPDATE sensor_data_file "
    "SET file_path = ? "
    "WHERE file_name = ?"
)
SQL_SELECT_LAST_USED_COL_BY_ID = (
    "SELECT last_used_column "
    "FROM sensor_data_file "
    "WHERE id = ?"
)
SQL_UPDATE_LAST_USED_COL = (
    "UPDATE sensor_data_file "
    "SET last_used_column = ? "
    "WHERE id = ?"
)
SQL_UPDATE_SENSOR = "UPDATE sensor_data_file SET sensor_id = ? WHERE id = ?"


class SensorDataFileManager:

    def __init__(self, settings: ProjectSettingsDialog):
        self._conn = sqlite3.connect(
            settings.database_file.as_posix(),
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        # Enable Sqlite foreign key support
        self._conn.execute("PRAGMA foreign_keys = 1")

        self._cur = self._conn.cursor()

    def get_id_by_file_name(self, file_name: str) -> int:
        """
        Return the ID of the sensor data file, or -1 if not exists.

        :param file_name: The base name of the file
        :return: The ID of the sensor data file, or -1 if not exists
        """
        self._cur.execute(SQL_SELECT_ID_BY_FILE_NAME, (file_name,))
        res = self._cur.fetchone()

        if res is None:
            return -1
        else:
            return res[0]

    def get_id_by_file_path(self, file_path: str) -> int:
        """
        Return the ID of the sensor data file, or -1 if not exists.

        :param file_path: The file path
        :return: The ID of the sensor data file, or -1 if not exists
        """
        self._cur.execute(SQL_SELECT_ID_BY_FILE_PATH, (file_path,))
        res = self._cur.fetchone()

        if res is None:
            return -1
        else:
            return res[0]

    # Depricated, sensordata filename is not unique and should not be used. Use filepath instead

    # def get_sensor_model_by_file_name(self, file_name: str):
    #     self._cur.execute(SQL_SELECT_SENSOR_MODEL_BY_FILE_NAME, (file_name,))
    #     res = self._cur.fetchone()
    #
    #     if res is not None:
    #         return res[0]
    #
    #     return None

    def get_sensor_model_by_file_path(self, file_path: str):
        """
        Return the model ID by file path
        :param file_path:
        :return: Model ID
        """
        self._cur.execute(SQL_SELECT_SENSOR_MODEL_BY_FILE_PATH, (file_path,))
        res = self._cur.fetchone()

        if res is not None:
            return res[0]

        return None

    def get_sensor_model_by_id(self, id_: int) -> int:
        self._cur.execute(SQL_SELECT_SENSOR_MODEL_BY_ID, (id_,))
        res = self._cur.fetchone()

        if res is not None:
            return res[0]
        else:
            return -1

    def get_file_name_by_id(self, id_: int) -> str:
        """
        Get the file name of the sensor data file associated with the ID.

        :param id_: The ID of the sensor data file
        :return: The file name
        """
        self._cur.execute(SQL_SELECT_FILE_NAME_BY_ID, (id_,))
        return self._cur.fetchone()[0]

    def get_last_used_column_by_id(self, id_: int):
        """
        Get the last used column by file ID.

        :param id_: The ID of the sensor data file
        :return: The last used column
        """
        self._cur.execute(SQL_SELECT_LAST_USED_COL_BY_ID, (id_,))
        res = self._cur.fetchone()

        if res is not None:
            return res[0]

        return ""

    def set_last_used_column(self, id_: int, col_name: str):
        """
        Update the last used column.

        :param id_: The ID of the sensor data file
        :param col_name: The last used column name
        """
        self._cur.execute(SQL_UPDATE_LAST_USED_COL, (col_name, id_))
        self._conn.commit()

    def add_file(self, file_name: str, file_path: str, sensor_id: int, datetime: dt.datetime) -> int:
        """
        Add a new file mapping.

        :param file_name: The file name
        :param file_path: The last known file path
        :param sensor_id: The sensor ID
        :param datetime: datetime of the data-file
        """
        self._cur.execute(SQL_INSERT_FILE, (file_name, file_path, sensor_id, datetime))
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

    def get_file_path_by_id(self, id_: int) -> str:
        """
        Get the file path of the sensor data file associated with the ID.

        :param id_: The ID of the sensor data file entity
        :return: The file path string
        """
        self._cur.execute(SQL_SELECT_FILE_PATH_BY_ID, (id_,))
        return self._cur.fetchone()[0]

    def get_ids_by_sensor_and_dates(self, sensor_id: int, start_date: dt.datetime, end_date: dt.datetime) -> List[int]:
        """
        Returns all file names for a given sensor between two dates.

        :param sensor_id: sensor id
        :param start_date: start date
        :param end_date: end date
        :return: list of file names
        """
        self._cur.execute(SQL_SELECT_IDS_BY_SENSOR_AND_DATES, (sensor_id, start_date, end_date))
        return [x[0] for x in self._cur.fetchall()]

    def get_sensor_ids(self) -> List[str]:
        """
        Returns a list of all sensor ids that have been used so far in this project.

        :return: list of sensor ids
        """
        self._cur.execute(SQL_SELECT_SENSOR_IDS)
        return [x[0] for x in self._cur.fetchall()]

    def get_sensor_by_id(self, id_: int) -> int:
        """
        Returns the ID of the associated sensor.

        :param id_: The ID of the sensor data file
        :return: The ID of the sensor
        """
        self._cur.execute(SQL_SELECT_SENSOR_BY_ID, (id_,))
        res = self._cur.fetchone()

        if res is not None:
            return res[0]

        return -1

    def update_sensor(self, sensor_data_file_id: int, sensor_id: int):
        """
        Updates the associated sensor ID of a sensor datafile.

        :param sensor_data_file_id: The ID of the sensor datafile
        :param sensor_id: The sensor ID of the sensor associated with the datafile
        """
        self._cur.execute(SQL_UPDATE_SENSOR, (sensor_id, sensor_data_file_id))
        self._conn.commit()

