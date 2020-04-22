import sqlite3
import datetime as dt

SQL_SELECT_LABELS_BY_DATES = "SELECT start_time, end_time, activity " \
                             "FROM label, label_type " \
                             "WHERE sensor_data_file = ? " \
                             "AND (start_time BETWEEN ? AND ? " \
                             "OR end_time BETWEEN ? AND ?) " \
                             "AND label.label_type = label_type.id"


class ExportManager:

    def __init__(self, project_name: str):
        """
        :param project_name: The name of the current project
        """
        self.project_name = project_name
        self._conn = sqlite3.connect('projects/' + project_name + '/project_data.db',
                                     detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self._conn.row_factory = sqlite3.Row
        self._cur = self._conn.cursor()

    def get_labels_by_dates(self,
                            sensor_data_file: int,
                            start_datetime: dt.datetime,
                            end_datetime: dt.datetime) -> [sqlite3.Row]:
        self._cur.execute(SQL_SELECT_LABELS_BY_DATES, (sensor_data_file,
                                                       start_datetime,
                                                       end_datetime,
                                                       start_datetime,
                                                       end_datetime))
        return self._cur.fetchall()
