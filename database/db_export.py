import sqlite3
from datetime import datetime

SQL_SELECT_LABEL_DATA_BETWEEN_DATES = "SELECT start_time, end_time, label_name, sensor.name FROM label_data, sensor " \
                                      "WHERE sensor_id = ? AND " \
                                      "start_time BETWEEN ? AND ? AND " \
                                      "end_time BETWEEN ? AND ? AND " \
                                      "label_data.sensor_id = sensor.id"


class ExportManager:

    def __init__(self, project_name: str):
        """
        :param project_name: The name of the current project
        """
        self.project_name = project_name
        self._conn = sqlite3.connect('projects/' + project_name + '/project_data.db',
                                     detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self._cur = self._conn.cursor()

    def get_label_data_between_dates(self, sensor_id: int, start_datetime: datetime, end_datetime: datetime):
        self._cur.execute(SQL_SELECT_LABEL_DATA_BETWEEN_DATES, (sensor_id,
                                                                start_datetime,
                                                                end_datetime,
                                                                start_datetime,
                                                                end_datetime))
        return self._cur.fetchall()
