import sqlite3
import csv
from datetime import datetime, date
from typing import List, Tuple

SQL_ADD_LABEL_TYPE = "INSERT INTO label_type(name, color, description) VALUES (?,?,?)"
SQL_GET_LABEL_TYPES = "SELECT * FROM label_type"
SQL_DEL_LABEL_TYPE = "DELETE FROM label_type WHERE name = ?"
SQL_DEL_LABEL_DATA_ALL = "DELETE FROM label_data WHERE label_name = ?"
SQL_DEL_LABEL_DATA = "DELETE FROM label_data WHERE start_time = ? AND sensor_id = ?"
SQL_ADD_LABEL = "INSERT INTO label_data(start_time, end_time, label_name, sensor_id) VALUES (?,?,?,?)"
SQL_UPD_NAME_TYPE = "UPDATE label_type SET name = ? WHERE name = ?"
SQL_UPD_NAME_DATA = "UPDATE label_data SET label_name = ? WHERE label_name = ?"
SQL_UPD_COLOR = "UPDATE label_type SET color = ? WHERE name = ?"
SQL_UPD_DESC = "UPDATE label_type SET description = ? WHERE name = ?"
SQL_CHANGE_LABEL = "UPDATE label_data SET label_name = ? WHERE start_time = ? AND sensor_id = ?"
SQL_GET_LABELS = "SELECT start_time, end_time, label_name FROM label_data WHERE sensor_id = ? ORDER BY start_time ASC"
SQL_GET_ALL_LABELS = "SELECT * FROM label_data ORDER BY start_time ASC"
SQL_GET_LABELS_DATE = "SELECT start_time, end_time, label_name FROM label_data WHERE date(start_time) = ? AND " \
                      "sensor_id = ? ORDER BY start_time ASC"
SQL_GET_LABELS_BETWEEN_DATES = "SELECT start_time, end_time, label_name FROM label_data WHERE (start_time " \
                               "BETWEEN ? AND ?) AND sensor_id = ? ORDER BY start_time ASC"
SQL_GET_SENSOR_IDS = "SELECT DISTINCT sensor_id FROM sensor_map"
SQL_ADD_FILE = "INSERT INTO sensor_map(file_name, sensor_id, file_date) VALUES (?,?,?)"
SQL_GET_FILE_NAMES = "SELECT file_name FROM sensor_map WHERE sensor_id = ? AND (file_date BETWEEN ? AND ?)"


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
        c = self._conn.cursor()
        c.execute("CREATE TABLE label_type (name TEXT PRIMARY KEY, color TEXT, description TEXT)")
        c.execute("CREATE TABLE label_data (start_time TIMESTAMP, end_time TIMESTAMP, label_name TEXT, sensor_id TEXT, "
                  "PRIMARY KEY(start_time, sensor_id), FOREIGN KEY (label_name) REFERENCES label_type(name))")
        c.execute("CREATE TABLE file_mapping (file_name TEXT PRIMARY KEY, sensor_id TEXT, file_date TIMESTAMP)")
        self._conn.commit()

    def add_label_type(self, name: str, color: str, desc: str) -> bool:
        """
        Creates a new label type.

        :param name: The name of the new label type
        :param color: The color of the new label
        :param desc: The description of the label
        :return: boolean indication if the label type was added successfully
        """
        try:
            self._cur.execute(SQL_ADD_LABEL_TYPE, (name, color, desc))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            return False

    def delete_label_type(self, name: str) -> None:
        """
        Deletes a label type.

        :param name: The name of the label type
        """
        self._cur.execute(SQL_DEL_LABEL_DATA_ALL, [name])
        self._cur.execute(SQL_DEL_LABEL_TYPE, [name])
        self._conn.commit()

    def add_label(self, start_time: datetime, end_time: datetime, name: str, sensor: str) -> bool:
        """
        Adds a label to the data of a sensor.

        :param start_time: The timestamp in the sensor-data at which the label starts
        :param end_time: The The timestamp in the sensor-data at which the label ends
        :param name: The name of the label type that is used
        :param sensor: The sensor ID belonging to the data
        :return: boolean indication if the label was added successfully
        """
        try:
            self._cur.execute(SQL_ADD_LABEL, (start_time, end_time, name, sensor))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            return False

    def delete_label(self, start_time: datetime, sens_id: str) -> None:
        """
        Deletes a label linked to data.

        :param start_time: The time at which the label starts
        :param sens_id: The sensor ID for which the label is made
        """
        self._cur.execute(SQL_DEL_LABEL_DATA, (start_time, sens_id))
        self._conn.commit()

    def update_label_name(self, old_name: str, new_name: str) -> None:
        """
        Updates the name of an existing label type. This also updates the name of all the labels that were made using
        the old name.

        :param old_name: The name of the label type that has to be changed
        :param new_name: The name that the label type should get
        """
        self._cur.execute(SQL_UPD_NAME_DATA, (new_name, old_name))
        self._cur.execute(SQL_UPD_NAME_TYPE, (new_name, old_name))
        self._conn.commit()

    def update_label_color(self, label_name: str, color: str) -> None:
        """
        Updates the color of an existing label type.

        :param label_name: The name of the label type
        :param color: The new color that the label type should get
        """
        self._cur.execute(SQL_UPD_COLOR, (color, label_name))
        self._conn.commit()

    def update_label_description(self, label_name: str, desc: str) -> None:
        """
        Updates the description of an existing label type.

        :param label_name: The name of the label type
        :param desc: The new description that the label type should get
        """
        self._cur.execute(SQL_UPD_DESC, (desc, label_name))
        self._conn.commit()

    def change_label(self, start_time: datetime, label_name: str, sens_id: str) -> None:
        """
        Changes the label type of a data-label.

        :param start_time: The start time of the label
        :param label_name: The name of the label type into which the label should be changed
        :param sens_id: The sensor ID belonging to this label
        """
        self._cur.execute(SQL_CHANGE_LABEL, (label_name, start_time, sens_id))
        self._conn.commit()

    def get_label_types(self) -> List[Tuple[str, str, str]]:
        """
        Returns all label types.

        :return: List of tuples (label name, label color, label description) of all label types
        """
        self._cur.execute(SQL_GET_LABEL_TYPES)
        return self._cur.fetchall()

    def get_all_labels(self, sensor_id: str) -> List[Tuple[datetime, datetime, str]]:
        """
        Returns all the labels for a given sensor.

        :param sensor_id: The sensor ID of the sensor for which the labels need to be returned
        :return: List of tuples (start_time, end_time, label_name) of all labels belonging to the sensor
        """
        self._cur.execute(SQL_GET_LABELS, [sensor_id])
        return self._cur.fetchall()

    def file_is_added(self, file_name: str) -> bool:
        """
        Function for checking if a file is already added.

        :param file_name: The base name of the file
        :return: boolean indicating if the file is already added or not
        """
        self._cur.execute("SELECT 1 FROM sensor_map WHERE file_name = ?", [file_name])
        return len(self._cur.fetchall()) == 1

    def add_file(self, filename: str, sensor_id: str, date: datetime) -> None:
        """
        Adds a new file mapping.

        :param filename: file path
        :param sensor_id: sensor id
        :param date: date of the data-file
        """
        self._cur.execute(SQL_ADD_FILE, (filename, sensor_id, date))
        self._conn.commit()

    def get_file_names(self, sensor_id: str, start_date: datetime, end_date: datetime) -> List[str]:
        """
        Returns all file paths for a given sensor between two dates.

        :param sensor_id: sensor id
        :param start_date: start date
        :param end_date: end date
        :return: list of file paths
        """
        self._cur.execute(SQL_GET_FILE_NAMES, (sensor_id, start_date, end_date))
        return [x[0] for x in self._cur.fetchall()]

    def get_labels_date(self, sensor_id: str, date: date) -> List[Tuple[datetime, datetime, str]]:
        """
        Returns all the labels for a given sensor on a given date.

        :param sensor_id: The sensor ID of the sensor for which the labels need to be returned
        :param date: The date for which the labels should be returned
        :return: List of tuples (start_time, end_time, label_name)
        """
        self._cur.execute(SQL_GET_LABELS_DATE, (date, sensor_id))
        return self._cur.fetchall()

    def get_labels_between_dates(self, sensor_id: str, start_date: datetime, end_date: datetime) \
            -> List[Tuple[datetime, datetime, str]]:
        """
        Returns all the labels for a given sensor between the given dates.

        :param sensor_id: The sensor ID of the sensor for which the labels need to be returned
        :param start_date: The first date of the interval
        :param end_date: The second date of the interval
        :return: List of tuples (start_time, end_time, label_name)
        """
        self._cur.execute(SQL_GET_LABELS_BETWEEN_DATES, (start_date, end_date, sensor_id))
        return self._cur.fetchall()

    def get_sensor_ids(self) -> List[str]:
        """
        Returns a list of all sensor ids that have been used so far in this project.

        :return: list of sensor ids
        """
        self._cur.execute(SQL_GET_SENSOR_IDS)
        return [x[0] for x in self._cur.fetchall()]

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
