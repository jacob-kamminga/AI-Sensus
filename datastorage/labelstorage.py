import sqlite3
import csv
from datetime import datetime, date
from typing import List, Tuple

sql_add_label_type = "INSERT INTO labelType(Name, Color, Description) VALUES (?,?,?)"
sql_get_label_types = "SELECT * FROM labelType"
sql_del_label_type = "DELETE FROM labelType WHERE Name = ?"
sql_del_label_data_all = "DELETE FROM labelData WHERE Label_name = ?"
sql_del_label_data = "DELETE FROM labelData WHERE Start_time = ? AND Sensor_id = ?"
sql_add_label = "INSERT INTO labelData(Start_time, End_time, Label_name, Sensor_id) VALUES (?,?,?,?)"
sql_upd_name_type = "UPDATE labelType SET Name = ? WHERE Name = ?"
sql_upd_name_data = "UPDATE labelData SET Label_name = ? WHERE Label_name = ?"
sql_upd_color = "UPDATE labelType SET Color = ? WHERE Name = ?"
sql_upd_desc = "UPDATE labelType SET Description = ? WHERE Name = ?"
sql_change_label = "UPDATE labelData SET Label_name = ? WHERE Start_time = ? AND Sensor_id = ?"
sql_get_labels = "SELECT Start_time, End_time, Label_name FROM labelData WHERE Sensor_id = ? ORDER BY Start_time ASC"
sql_get_all_labels = "SELECT * FROM labelData ORDER BY Start_time ASC"
sql_get_labels_date = "SELECT Start_time, End_time, Label_name FROM labelData WHERE date(Start_time) = ? AND " \
                      "Sensor_id = ? ORDER BY Start_time ASC"
sql_get_labels_between_dates = "SELECT Start_time, End_time, Label_name FROM labelData WHERE (Start_time " \
                               "BETWEEN ? AND ?) AND Sensor_id = ? ORDER BY Start_time ASC"
sql_get_sensor_ids = "SELECT DISTINCT Sensor_id FROM fileMapping"
sql_add_file = "INSERT INTO fileMapping(Filepath, Sensor_id, Filedate) VALUES (?,?,?)"
sql_get_file_names = "SELECT Filepath FROM fileMapping WHERE Sensor_id = ? AND (Filedate BETWEEN ? AND ?)"


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
        c.execute("CREATE TABLE labelType (Name TEXT PRIMARY KEY, Color TEXT, Description TEXT)")
        c.execute("CREATE TABLE labelData (Start_time TIMESTAMP, End_time TIMESTAMP, Label_name TEXT, Sensor_id TEXT, "
                  "PRIMARY KEY(Start_time, Sensor_id), FOREIGN KEY (Label_name) REFERENCES labelType(Name))")
        c.execute("CREATE TABLE fileMapping (Filepath TEXT PRIMARY KEY, Sensor_id TEXT, Filedate TIMESTAMP)")
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
            self._cur.execute(sql_add_label_type, (name, color, desc))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            return False

    def delete_label_type(self, name: str) -> None:
        """
        Deletes a label type.

        :param name: The name of the label type
        """
        self._cur.execute(sql_del_label_data_all, [name])
        self._cur.execute(sql_del_label_type, [name])
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
            self._cur.execute(sql_add_label, (start_time, end_time, name, sensor))
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
        self._cur.execute(sql_del_label_data, (start_time, sens_id))
        self._conn.commit()

    def update_label_name(self, old_name: str, new_name: str) -> None:
        """
        Updates the name of an existing label type. This also updates the name of all the labels that were made using
        the old name.

        :param old_name: The name of the label type that has to be changed
        :param new_name: The name that the label type should get
        """
        self._cur.execute(sql_upd_name_data, (new_name, old_name))
        self._cur.execute(sql_upd_name_type, (new_name, old_name))
        self._conn.commit()

    def update_label_color(self, label_name: str, color: str) -> None:
        """
        Updates the color of an existing label type.

        :param label_name: The name of the label type
        :param color: The new color that the label type should get
        """
        self._cur.execute(sql_upd_color, (color, label_name))
        self._conn.commit()

    def update_label_description(self, label_name: str, desc: str) -> None:
        """
        Updates the description of an existing label type.

        :param label_name: The name of the label type
        :param desc: The new description that the label type should get
        """
        self._cur.execute(sql_upd_desc, (desc, label_name))
        self._conn.commit()

    def change_label(self, start_time: datetime, label_name: str, sens_id: str) -> None:
        """
        Changes the label type of a data-label.

        :param start_time: The start time of the label
        :param label_name: The name of the label type into which the label should be changed
        :param sens_id: The sensor ID belonging to this label
        """
        self._cur.execute(sql_change_label, (label_name, start_time, sens_id))
        self._conn.commit()

    def get_label_types(self) -> List[Tuple[str, str, str]]:
        """
        Returns all label types.

        :return: List of tuples (label name, label color, label description) of all label types
        """
        self._cur.execute(sql_get_label_types)
        return self._cur.fetchall()

    def get_all_labels(self, sensor_id: str) -> List[Tuple[datetime, datetime, str]]:
        """
        Returns all the labels for a given sensor.

        :param sensor_id: The sensor ID of the sensor for which the labels need to be returned
        :return: List of tuples (start_time, end_time, label_name) of all labels belonging to the sensor
        """
        self._cur.execute(sql_get_labels, [sensor_id])
        return self._cur.fetchall()

    def file_is_added(self, filename: str) -> bool:
        """
        Function for checking if a file is already added.

        :param filename: file path
        :return: boolean indicating if the file is already added or not
        """
        self._cur.execute("SELECT 1 FROM fileMapping WHERE Filepath = ?", [filename])
        return len(self._cur.fetchall()) == 1

    def add_file(self, filename: str, sensor_id: str, date: datetime) -> None:
        """
        Adds a new file mapping.

        :param filename: file path
        :param sensor_id: sensor id
        :param date: date of the data-file
        """
        self._cur.execute(sql_add_file, (filename, sensor_id, date))
        self._conn.commit()

    def get_file_paths(self, sensor_id: str, start_date: datetime, end_date: datetime) -> List[str]:
        """
        Returns all file paths for a given sensor between two dates.

        :param sensor_id: sensor id
        :param start_date: start date
        :param end_date: end date
        :return: list of file paths
        """
        self._cur.execute(sql_get_file_names, (sensor_id, start_date, end_date))
        return [x[0] for x in self._cur.fetchall()]

    def get_labels_date(self, sensor_id: str, date: date) -> List[Tuple[datetime, datetime, str]]:
        """
        Returns all the labels for a given sensor on a given date.

        :param sensor_id: The sensor ID of the sensor for which the labels need to be returned
        :param date: The date for which the labels should be returned
        :return: List of tuples (start_time, end_time, label_name)
        """
        self._cur.execute(sql_get_labels_date, (date, sensor_id))
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
        self._cur.execute(sql_get_labels_between_dates, (start_date, end_date, sensor_id))
        return self._cur.fetchall()

    def get_sensor_ids(self) -> List[str]:
        """
        Returns a list of all sensor ids that have been used so far in this project.

        :return: list of sensor ids
        """
        self._cur.execute(sql_get_sensor_ids)
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
