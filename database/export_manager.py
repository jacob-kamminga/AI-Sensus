import datetime as dt
import sqlite3

from gui.dialogs.project_settings_dialog import ProjectSettingsDialog

SQL_SELECT_LABELS_BY_DATES = "SELECT start_time, end_time, activity " \
                             "FROM label, label_type " \
                             "WHERE sensor_data_file = ? " \
                             "AND (start_time BETWEEN ? AND ? " \
                             "OR end_time BETWEEN ? AND ?) " \
                             "AND label.label_type = label_type.id"


class ExportManager:

    def __init__(self, settings: ProjectSettingsDialog):
        self._conn = sqlite3.connect(
            settings.database_file.as_posix(),
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        # Enable Sqlite foreign key support
        self._conn.execute("PRAGMA foreign_keys = 1")

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
