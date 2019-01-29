import os.path
import sqlite3
from datastorage import settings
from datetime import datetime
from typing import Any, List, Tuple
from data_import.sensor_data import SensorData
import pandas as pd

sql_add_subject = "INSERT INTO subject_map (Name) VALUES (?)"
sql_update_subject = "UPDATE subject_map SET Name = ? WHERE Name = ?"
sql_delete_subject = "DELETE FROM subject_map WHERE Name = ?"
sql_update_sensor = "UPDATE subject_map SET Sensor = ? WHERE Name = ?"
sql_update_start_date = "UPDATE subject_map SET Start_date = ? WHERE Name = ?"
sql_update_end_date = "UPDATE subject_map SET End_date = ? WHERE Name = ?"
sql_add_column = "ALTER TABLE subject_map ADD COLUMN {} TEXT"
sql_update_user_column = "UPDATE subject_map SET {} = ? WHERE Name = ?"
sql_get_table = "SELECT Name, Sensor, Start_date, End_date{} FROM subject_map"
sql_get_subject_data = "SELECT Sensor, Start_date, End_date FROM subject_map WHERE Name = ?"
sql_get_subjects = "SELECT Name FROM subject_map"


class SubjectManager:

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
        """Method for creating the necessary subject mapping table."""
        self._cur.execute("CREATE TABLE subject_map (Name TEXT PRIMARY KEY, "
                          "Sensor TEXT, Start_date TIMESTAMP, End_date TIMESTAMP)")
        self._conn.commit()

    def add_subject(self, name: str) -> None:
        """
        Adds a new subject.

        :param name: The name of the new subject
        """
        self._cur.execute(sql_add_subject, [name])
        self._conn.commit()

    def update_subject(self, name_old: str, name_new: str) -> None:
        """
        Changes the name of a subject.

        :param name_old: name that should be changed
        :param name_new: name that it should be changed to
        """
        self._cur.execute(sql_update_subject, (name_new, name_old))
        self._conn.commit()

    def delete_subject(self, name: str) -> None:
        """
        Removes a subject from the table.

        :param name: name of the subject to remove
        """
        self._cur.execute(sql_delete_subject, [name])
        self._conn.commit()

    def update_sensor(self, name: str, sens_id: str) -> None:
        """
        Changes the sensor mapped to a subject.

        :param name: The name of the subject to map this sensor to
        :param sens_id: The sensor ID of the sensor
        """
        self._cur.execute(sql_update_sensor, (sens_id, name))
        self._conn.commit()

    def update_start_date(self, name: str, date: datetime) -> None:
        """
        Changes the start date for a subject.

        :param name: The name of the subject
        :param date: The start date
        """
        self._cur.execute(sql_update_start_date, (date, name))
        self._conn.commit()

    def update_end_date(self, name: str, date: datetime) -> None:
        """
        Changes the end date for a subject.

        :param name: The name of the subject
        :param date: The end date
        """
        self._cur.execute(sql_update_end_date, (date, name))
        self._conn.commit()

    def add_column(self, name: str) -> bool:
        """
        Adds a column to the table with the given name.

        :param name: Name of the new column
        :return: boolean indicating if the column was added successfully
        """
        col_map = self.settings.get_setting("subj_map")
        if name in col_map.keys():  # if column already exists, return false
            return False
        new_col_nr = self.settings.get_setting("next_col")
        new_col_name = "c" + str(new_col_nr)
        col_map[name] = new_col_name
        self._cur.execute(sql_add_column.format(new_col_name))  # add column to database with name "c" + the next number
        self._conn.commit()
        self.settings.set_setting("subj_map", col_map)
        self.settings.set_setting("next_col", new_col_nr + 1)
        return True

    def delete_column(self, name: str) -> None:
        """
        Deletes a column from the table if it exists. (The column is not deleted from the actual database,
        it is just not visible anymore via this class.)

        :param name: the name of the column to delete
        """
        col_map = self.settings.get_setting("subj_map")
        if name in col_map.keys():
            col_map.pop(name, None)  # remove the given column from the map. the database column is not deleted.
            self.settings.set_setting("subj_map", col_map)

    def update_user_column(self, col_name: str, subj_name: str, new_value: Any) -> bool:
        """
        Update a value in a column made by the user

        :param col_name: the name of the column that should be updated
        :param subj_name: the subject name for which the row should be updated
        :param new_value: the value that should be inserted
        :return: boolean indicating if the column was updated successfully
        """
        col_map = self.settings.get_setting("subj_map")
        if col_name in col_map.keys():  # only try to update if column is known
            self._cur.execute(sql_update_user_column.format(col_map[col_name]), (new_value, subj_name))
            self._conn.commit()
            return True
        else:
            return False

    def change_column_name(self, old: str, new: str) -> bool:
        """
        Update the name of a user-made column

        :param old: the old name
        :param new: the new name
        :return: boolean indicating if the name was updated successfully
        """
        col_map = self.settings.get_setting("subj_map")
        if (new in col_map.keys()) or (old not in col_map.keys()):
            return False

        col_map[new] = col_map[old]  # add new name and map it to database column of the old name
        col_map.pop(old, None)       # remove old name from the map
        self.settings.set_setting("subj_map", col_map)
        return True

    def get_subjects(self) -> List[str]:
        """
        Returns a list of all subjects

        :return: list of subject names
        """
        self._cur.execute(sql_get_subjects)
        return [x[0] for x in self._cur.fetchall()]

    def get_dataframes_subject(self, subject_name: str) -> List[pd.DataFrame]:
        """
        Returns a list of pandas DataFrames of all the labeled sensor-data belonging to the subject

        :param subject_name: subject name
        :return: list of pandas DataFrames
        """
        from datastorage.labelstorage import LabelManager
        from datastorage.settings import Settings
        self._cur.execute(sql_get_subject_data, [subject_name])  # get the stored information for this subject
        subject_data = self._cur.fetchall()

        if len(subject_data) == 0 or subject_data[0][0] is None:  # if subject doesn't exist or sensor hasn't been set,
            return []                                             # return an empty list

        subject_data = subject_data[0]
        lm = LabelManager(self.project_name)
        paths = lm.get_file_paths(subject_data[0], subject_data[1], subject_data[2])  # get datafile paths for subject
        data_frames = []
        settings_dict = Settings(self.project_name).settings_dict
        for path in paths:
            if os.path.isfile(path):
                # for each file, load a DataFrame and add the labels to it
                sd = SensorData(path, settings_dict)
                time_col_name = sd.metadata['names'][0]  # making the assumption that the time column is always the first
                sd.add_timestamp_column(time_col_name, "Timestamp")
                end_datetime = datetime.fromisoformat(str(sd.get_data()['Timestamp'].iloc[-1]))
                labels = lm.get_labels_between_dates(subject_data[0], sd.metadata['datetime'], end_datetime)
                sd.add_labels(labels, "Label", "Timestamp")
                data_frames.append(sd.get_data())
        return data_frames

    def get_table(self):
        """
        Returns the full table together with a list of all column names.

        :return: list of column names and a list of tuples containing the table data
        """
        col_map = self.settings.get_setting("subj_map")
        col_names = ["Subject name", "Sensor ID", "Start date", "End date"] + list(col_map.keys())
        cols_to_select = list(col_map.values())  # only select the database columns that are currently used by the user
        select_string = ""
        for col in cols_to_select:
            select_string += ", " + col
        self._cur.execute(sql_get_table.format(select_string))
        return col_names, self._cur.fetchall()
