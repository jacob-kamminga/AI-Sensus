import sqlite3
import datetime as dt
from typing import List, Tuple

SQL_CREATE_TABLE_LABEL = \
    "create table label\
(\
    id               INTEGER   not null\
        constraint label_pk\
            primary key autoincrement,\
    start_time       TIMESTAMP not null,\
    end_time         TIMESTAMP not null,\
    label_type       INTEGER   not null\
        references label_type\
            on update cascade on delete cascade,\
    sensor_data_file INTEGER   not null\
        references sensor_data_file\
            on update cascade on delete cascade\
);\
\
create unique index label_start_time_sensor_data_file_id_uindex\
    on label (start_time, sensor_data_file);"

SQL_DELETE_LABEL_BY_ID = \
    "DELETE FROM label " \
    "WHERE id = ?"

SQL_DELETE_LABEL_BY_START_AND_FILE = \
    "DELETE FROM label " \
    "WHERE start_time = ? " \
    "AND sensor_data_file = ?"

SQL_INSERT_LABEL = \
    "INSERT INTO label(start_time, end_time, label_type, sensor_data_file) VALUES (?, ?, ?, ?)"

SQL_SELECT_ALL_LABELS = \
    "SELECT * " \
    "FROM label " \
    "ORDER BY start_time"

SQL_SELECT_LABELS_BY_FILE = \
    "SELECT start_time, end_time, label_type " \
    "FROM label " \
    "WHERE sensor_data_file = ? " \
    "ORDER BY start_time"

SQL_SELECT_LABELS_BETWEEN_DATES = \
    "SELECT start_time, end_time, label_type " \
    "FROM label " \
    "WHERE (start_time BETWEEN ? AND ?) " \
    "AND sensor_data_file = ? " \
    "ORDER BY start_time"

# SQL_SELECT_LABELS_BY_FILE_AND_DATE = \
#     "SELECT start_time, end_time, label_type " \
#     "FROM label " \
#     "WHERE sensor_data_file = ? " \
#     "AND start_time = ? " \
#     "ORDER BY start_time"

SQL_UPDATE_LABEL = \
    "UPDATE label " \
    "SET label_type = ? " \
    "WHERE start_time = ? AND sensor_data_file = ?"


class LabelManager:

    def __init__(self, project_name: str):
        """
        :param project_name: The name of the current project
        """
        self.project_name = project_name
        self._conn = sqlite3.connect('projects/' + project_name + '/project_data.db',
                                     detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self._cur = self._conn.cursor()

    def create_tables(self) -> None:
        """Method for creating the necessary label tables in the database."""
        self._cur.execute(SQL_CREATE_TABLE_LABEL)
        self._conn.commit()

    def add_label(self, start_time: dt.datetime, end_time: dt.datetime, label_type: int, sensor_data_file: int) -> bool:
        """
        Add a label to the database.

        :param start_time: The timestamp in the sensor-data at which the label starts
        :param end_time: The The timestamp in the sensor-data at which the label ends
        :param label_type: The ID of the label type
        :param sensor_data_file: The ID of the sensor data file
        :return: True if label was added successfully
        """
        try:
            self._cur.execute(SQL_INSERT_LABEL, (start_time, end_time, label_type, sensor_data_file))
            self._conn.commit()
            return True
        except sqlite3.Error:
            return False

    def delete_label_by_id(self, id_: int) -> None:
        """
        Delete a label from the database.

        :param id_: The ID of the label to delete.
        """
        self._cur.execute(SQL_DELETE_LABEL_BY_ID, (id_,))
        self._conn.commit()
        
    def delete_label_by_start_and_file(self, start_dt: dt.datetime, sensor_data_file: int) -> None:
        """
        Delete a label from the database.

        :param start_dt: The start dt.datetime
        :param sensor_data_file: The ID of the sensor data file
        """
        self._cur.execute(SQL_DELETE_LABEL_BY_START_AND_FILE, (start_dt, sensor_data_file))
        self._conn.commit()

    def change_label(self, start_time: dt.datetime, label_name: str, sensor_data_file: int) -> None:
        """
        Changes the label type of a data-label.

        :param start_time: The start time of the label
        :param label_name: The name of the label type into which the label should be changed
        :param sensor_data_file: The ID of the sensor data file
        """
        self._cur.execute(SQL_UPDATE_LABEL, (label_name, start_time, sensor_data_file))
        self._conn.commit()

    def get_all_labels_by_file(self, sensor_data_file: int) -> List[Tuple[dt.datetime, dt.datetime, int]]:
        """
        Returns all the labels for a given sensor data file.

        :param sensor_data_file: The ID of the sensor data file
        :return: List of tuples (start_time, end_time, activity) belonging to the sensor sensor data file
        """
        self._cur.execute(SQL_SELECT_LABELS_BY_FILE, (sensor_data_file,))
        return self._cur.fetchall()

    # def get_labels_by_file_and_date(self, sensor_date_file: int, date: dt.date) \
    #         -> List[Tuple[dt.datetime, dt.datetime, int]]:
    #     """
    #     Returns all the labels for a given sensor on a given date.
    #
    #     :param sensor_date_file: The ID of the sensor data file
    #     :param date: The date for which the labels should be returned
    #     :return: List of tuples (start_time, end_time, label_name)
    #     """
    #     self._cur.execute(SQL_SELECT_LABELS_BY_FILE_AND_DATE, (sensor_date_file, date))
    #     return self._cur.fetchall()

    def get_labels_between_dates(self, sensor_id: int, start_date: dt.datetime, end_date: dt.datetime) \
            -> List[Tuple[dt.datetime, dt.datetime, str]]:
        """
        Returns all the labels for a given sensor between the given dates.

        :param sensor_id: The sensor ID of the sensor for which the labels need to be returned
        :param start_date: The first date of the interval
        :param end_date: The second date of the interval
        :return: List of tuples (start_time, end_time, label_name)
        """
        self._cur.execute(SQL_SELECT_LABELS_BETWEEN_DATES, (start_date, end_date, sensor_id))
        return self._cur.fetchall()

    # TODO: update export location?
    # def export_labels_all(self) -> None:
    #     """
    #     Exports all labels for this project to 1 .csv file
    #     """
    #     with open('projects/' + self.project_name + '/all_labels_' + self.project_name + '.csv', 'w', newline='') as csvfile:
    #         filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #         filewriter.writerow(['Start_time', 'End_time', 'label', 'sensorID'])
    #         for row in self._cur.execute(sql_get_all_labels).fetchall():
    #             filewriter.writerow([row[0], row[1], row[2], row[3]])
    #
    # def export_labels_sensor_date(self, sensor: str, date: date) -> None:
    #     """
    #     Exports the labels for a given sensor on a given date to a .csv file
    #
    #     :param sensor: the sensor ID of the sensor
    #     :param date: the date of the labels to export
    #     """
    #     with open('projects/' + self.project_name + '/' + str(date) + '_' + sensor + '.csv', 'w', newline='') as csvfile:
    #         filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #         filewriter.writerow(['Start_time', 'End_time', 'label', 'sensorID'])
    #         for row in self._cur.execute(sql_get_labels_date, (date, sensor)).fetchall():
    #             filewriter.writerow([row[0], row[1], row[2]])
