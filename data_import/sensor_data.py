import datetime as dt
from pathlib import Path

import pandas as pd
import pytz
from PyQt5.QtWidgets import QMessageBox

import parse_function.custom_function_parser as parser
from constants import COL_ABS_DATETIME, RELATIVE_TIME_ITEM, ABSOLUTE_TIME_ITEM
from data_import import sensor as sens, column_metadata as cm
from date_utils import utc_to_local
from machine_learning.classifier import CLASSIFIER_NAN
from models.sensor_metadata import SensorMetadata
from parse_function.parse_exception import ParseException
from gui.dialogs.project_settings_dialog import ProjectSettingsDialog
from database.models import *

START_TIME_INDEX = 0
STOP_TIME_INDEX = 1
LABEL_INDEX = 2
COLUMN_TIMESTAMP = COL_ABS_DATETIME


class SensorData:

    def __init__(self, file_path: Path, settings: ProjectSettingsDialog, sensor_model_id):
        # Initialize primitives
        self.settings = settings
        self.file_path = file_path

        self.sensor_model_id = sensor_model_id
        self.sensor_model = SensorModel.get_by_id(sensor_model_id)
        self.sensor_name = None
        self.metadata = SensorMetadata(self.file_path, self.sensor_model, sensor_model_id)
        self.col_metadata = dict()
        self.project_timezone = pytz.timezone(settings.get_setting('timezone'))

        # Parse metadata and data
        self._settings_dict = settings.settings_dict
        self._df = None
        self.parse()

    def __copy__(self):
        new = type(self)(self.file_path, self.settings, self.sensor_model_id)
        new.__dict__.update(self.__dict__)
        return new

    def parse(self):
        """
        Parses a csv file to get metadata and data.

        :return: the parsed data as a DataFrame
        """
        if not self._df:
            self.metadata.load_values()
            if not self.metadata.sensor_timezone:
                return
            self.metadata.parse_datetime()

            # Parse data from file
            self._df = pd.read_csv(self.file_path,
                                   names=self.metadata.col_names,
                                   skip_blank_lines=False,
                                   skiprows=self.sensor_model.col_names_row + 1,
                                   comment=self.sensor_model.comment_style if self.sensor_model.comment_style else None)

            self._df.columns = self._df.columns.str.strip()
            columns = self._df.columns.values.tolist()

            # set column metadata
            self.set_column_metadata(columns)

            try:
                # Convert sensor data to correct unit
                for name in columns:
                    # Retrieve conversion rate from column metadata
                    conversion = self.col_metadata[name].sensor.conversion

                    # If column doesn't have a conversion, continue to next column
                    if conversion is None:
                        continue

                    # Parse conversion to python readable expression
                    parsed_expr = parser.parse(conversion)

                    # Apply parsed expression to the data
                    self._df.eval(name + " = " + parsed_expr, inplace=True)
            except ParseException:
                # Pass ParseException
                raise

            if self.sensor_model.relative_absolute == RELATIVE_TIME_ITEM:
                try:
                    self.normalize_rel_datetime_column()
                except TypeError as e:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("Error")
                    msg.setText("Datetime column not relative.")
                    msg.setInformativeText("The sensor data datetime format was set to be relative "
                                           "but may actually be absolute. Please verify in the sensor model settings. "
                                           "The data will be parsed as absolute.")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec()

    def set_column_metadata(self, columns):
        """
        Sets the metadata for every column using the settings_dict.
        """
        for name in columns:
            # parse data_type
            data_type = (self._settings_dict[name + "_data_type"]
                         if name + "_data_type" in self._settings_dict.keys() else None)

            # parse sensor:
            # sensor name
            sensor_name = (self._settings_dict[name + "_sensor_name"]
                           if name + "_sensor_name" in self._settings_dict.keys() else None)

            # sampling rate
            sr = (self._settings_dict[name + "_sampling_rate"]
                  if name + "_sampling_rate" in self._settings_dict.keys() else None)

            # unit of measurement
            unit = (self._settings_dict[name + "_unit"]
                    if name + "unit" in self._settings_dict.keys() else None)

            # conversion rate
            conversion = (self._settings_dict[name + "_conversion"]
                          if name + "_conversion" in self._settings_dict.keys() else None)

            # construct sensor
            sensor = sens.Sensor(sensor_name, sr, unit, conversion)

            # create new column metadata and add it to list with metadata
            self.col_metadata[name] = cm.ColumnMetadata(name, data_type, sensor)

    def get_data(self, label=None):
        if label is None:
            return self._df.copy()
        else:
            return self._df[self._df["Label"] == label]

    def add_column_from_func(self, name: str, func: str):
        """
        Constructs a new column in the data frame using a given function.

        :param name: The name of the new column
        :param func: The function to calculate the values of the new column as a string
        """
        # Pass parse exception on
        try:
            # Parses a function into a python readable expression
            parsed_expr = parser.parse(func)

            # Apply parsed expression to data to create new column
            self._df.eval(name + " = " + parsed_expr, inplace=True)
        except ParseException:
            # Pass ParseException
            raise

    def add_timestamp_column(self, time_col: str, time_unit='s'):
        """
        Adds a timestamp column to the sensor data.

        :param time_col: The name of the column that contains the recorded time.
        :param time_unit: The time unit of the time column.
        """
        self._df[COLUMN_TIMESTAMP] = \
            pd.to_timedelta(self._df[time_col], unit=time_unit) + \
            utc_to_local(self.metadata.utc_dt, self.project_timezone)

    def add_abs_dt_col(self, use_utc=False):
        """
        Add an absolute time column to the existing dataframe.
        """
        time_col = self.sensor_model.timestamp_column

        # If time column is relative, convert relative time to absolute time
        if self.sensor_model.relative_absolute == RELATIVE_TIME_ITEM:
            time_unit = self.sensor_model.timestamp_unit

            # Add absolute datetime column to dataframe
            if use_utc:
                self._df[COL_ABS_DATETIME] = self.metadata.utc_dt + pd.to_timedelta(self._df.iloc[:, time_col],
                                                                                    unit=time_unit)
            else:
                try:
                    self._df[COL_ABS_DATETIME] = \
                        utc_to_local(self.metadata.utc_dt, self.project_timezone) + \
                        pd.to_timedelta(self._df.iloc[:, time_col], unit=time_unit)
                except ValueError as e:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("Invalid datetime string format")
                    msg.setText("Error: " + str(e))
                    msg.setInformativeText("The sensor datetime string format you entered is invalid. "
                                           f"Please change it to the correct format under Sensor > Sensor models > {self.sensor_name} > View settings.")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec()
                    return False
                except AttributeError as e:
                    # Relative time format could not be parsed.
                    self.sensor_model.relative_absolute = ABSOLUTE_TIME_ITEM

        # If time column is absolute, rename the column
        if self.sensor_model.relative_absolute == ABSOLUTE_TIME_ITEM:
            self._df.rename(columns={self._df.columns[time_col]: COL_ABS_DATETIME}, inplace=True)

            # Make sure the column is datetime
            if not pd.api.types.is_datetime64_any_dtype(self._df[COL_ABS_DATETIME]):
                try:
                    # Convert to datetime
                    self._df[COL_ABS_DATETIME] = pd.to_datetime(
                        self._df[COL_ABS_DATETIME],
                        errors='raise',
                        format=self.sensor_model.format_string,
                        exact=True
                    )

                except ValueError as e:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("Parse DateTime Error")
                    msg.setText("Error: " + str(e))
                    msg.setInformativeText("Could not add datetime column in data. Please verify "
                                           "the format string in the sensor model settings. ")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec()
                    return False
                except:
                    return False

                # Localize to sensor timezone and convert to project timezone
                self._df[COL_ABS_DATETIME] = \
                    self._df[COL_ABS_DATETIME].dt.tz_localize(self.metadata.sensor_timezone).dt.tz_convert(
                        self.project_timezone)

            # If start datetime of file is not in metadata, then we take the first value as utc_dt
            if self.metadata.utc_dt is None:
                first_value = self._df.iloc[0, time_col]
                first_value = first_value.astimezone(pytz.utc)

                if type(first_value) == pd.Timestamp:
                    self.metadata.utc_dt = first_value.to_pydatetime()
                else:
                    self.metadata.utc_dt = first_value

        return True

    def normalize_rel_datetime_column(self):
        """
        Normalize the relative datetime such that the first row will start at 0.
        """
        time_col = self.sensor_model.timestamp_column
        first_val = self._df.iloc[0, time_col]

        if type(first_val) == str:
            raise TypeError("Datetime is not relative.")

        if first_val != 0:
            # Subtract the (non-zero) first value from all values in the timestamp column to normalize the data
            self._df.iloc[:, time_col] = self._df.iloc[:, time_col].subtract(first_val)

    def add_labels_ml(self, label_data: [], label_col: str):
        """
        Add labels to the DataFrame for machine learning.

        :param label_data:
        :param label_col:
        :return:
        """
        # Add Label column to the DataFrame and initialize it to NaN
        self._df[label_col] = CLASSIFIER_NAN

        for label_entry in label_data:
            start_time = label_entry[START_TIME_INDEX]
            stop_time = label_entry[STOP_TIME_INDEX]
            label = label_entry[LABEL_INDEX]

            # Add label to the corresponding rows in the sensor data
            self._df.loc[
                (self._df[COLUMN_TIMESTAMP] >= start_time) & (self._df[COLUMN_TIMESTAMP] < stop_time),
                label_col
            ] = label

    def filter_between_dates(self, start: dt.datetime, end: dt.datetime):
        self._df = self._df[(self._df[COLUMN_TIMESTAMP] >= start) & (self._df[COLUMN_TIMESTAMP] < end)]

    def add_labels(self, labels):
        """
        Add labels to the DataFrame for exporting.

        :param labels:
        :return:
        """
        self._df["Label"] = ""

        for label in labels:
            start = pytz.utc.localize(label["start"])
            end = pytz.utc.localize(label["end"])
            activity = label["activity"]

            # Select all rows with timestamp between start and end and set activity label
            self._df.loc[(self._df[COLUMN_TIMESTAMP] >= start) & (self._df[COLUMN_TIMESTAMP] < end),
                         "Label"] = activity
