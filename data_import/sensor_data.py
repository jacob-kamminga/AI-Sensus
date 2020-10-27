import datetime as dt
from pathlib import Path

import pandas as pd
import pytz

import parse_function.custom_function_parser as parser
from constants import COL_ABSOLUTE_DATETIME, RELATIVE_TIME_ITEM, ABSOLUTE_TIME_ITEM
from data_import import sensor as sens, column_metadata as cm
from database.sensor_model_manager import SensorModelManager
from date_utils import utc_to_local
from machine_learning.classifier import CLASSIFIER_NAN
from models.sensor_metadata import SensorMetadata
from parse_function.parse_exception import ParseException
from project_settings import ProjectSettingsDialog

START_TIME_INDEX = 0
STOP_TIME_INDEX = 1
LABEL_INDEX = 2
COLUMN_TIMESTAMP = "Timestamp"


class SensorData:

    def __init__(self, file_path: Path, settings: ProjectSettingsDialog, sensor_model_id, sensor_timezone=pytz.utc):
        # Initialize primitives
        self.settings = settings
        self.sensor_model_manager = SensorModelManager(self.settings)
        self.file_path = file_path

        self.sensor_model_id = sensor_model_id
        self.sensor_model = self.sensor_model_manager.get_model_by_id(sensor_model_id)
        self.metadata = SensorMetadata(self.file_path, self.sensor_model, sensor_model_id, None, sensor_timezone)
        self.col_metadata = dict()
        self.project_timezone = pytz.timezone(settings.get_setting('timezone'))
        self.sensor_timezone = sensor_timezone

        # Parse metadata and data
        self._settings_dict = settings.settings_dict
        self._df = self.parse()

        if self.sensor_model.relative_absolute == RELATIVE_TIME_ITEM:
            self.normalize_rel_datetime_column()
        """ The sensor data as a DataFrame. """

    def __copy__(self):
        new = type(self)(self.file_path, self.settings, self.sensor_model_id, self.sensor_timezone)
        new.__dict__.update(self.__dict__)
        return new

    def parse(self) -> pd.DataFrame:
        """
        Parses a csv file to get metadata and data.

        :return: the parsed data as a DataFrame
        """
        self.metadata.load_values()

        # Parse data from file
        df = pd.read_csv(self.file_path,
                         names=self.metadata.col_names,
                         skip_blank_lines=False,
                         skiprows=self.sensor_model.col_names_row + 1,
                         comment=self.sensor_model.comment_style if self.sensor_model.comment_style else None)

        df.columns = df.columns.str.strip()
        columns = df.columns.values.tolist()

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
                df.eval(name + " = " + parsed_expr, inplace=True)
        except ParseException:
            # Pass ParseException
            raise

        return df

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

    def get_data(self):
        return self._df.copy()

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

    def add_abs_datetime_column(self):
        """
        Add an absolute time column to the existing dataframe.
        """
        time_col = self.sensor_model.timestamp_column

        # If time column is relative, convert relative time to absolute time
        if self.sensor_model.relative_absolute == RELATIVE_TIME_ITEM:
            time_unit = self.sensor_model.timestamp_unit

            # Add absolute datetime column to dataframe
            self._df[COL_ABSOLUTE_DATETIME] = \
                utc_to_local(self.metadata.utc_dt, self.project_timezone) + \
                pd.to_timedelta(self._df.iloc[:, time_col], unit=time_unit)

        # If time column is absolute, rename the column
        elif self.sensor_model.relative_absolute == ABSOLUTE_TIME_ITEM:
            self._df.rename(columns={time_col: COL_ABSOLUTE_DATETIME})

    def normalize_rel_datetime_column(self):
        time_col = self.sensor_model.timestamp_column
        first_val = self._df.iloc[0, time_col]

        if first_val != 0:
            # Subtract the (non-zero) first value from all values in the timestamp column to normalize the data
            self._df.iloc[:, time_col] = self._df.iloc[:, time_col].subtract(first_val)

    def add_labels_ml(self, label_data: [], label_col: str):
        """
        Add labels to the DataFrame for machine learning.

        :param label_data:
        :param label_col:
        :param timestamp_col:
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
            # start = self.sensor_timezone.localize(label["start"])
            # end = self.sensor_timezone.localize(label["end"])
            # TODO are labels always stored as UTC?
            start = pytz.utc.localize(label["start"])
            end = pytz.utc.localize(label["end"])
            activity = label["activity"]

            self._df.loc[
                (self._df[COLUMN_TIMESTAMP] >= start) & (self._df[COLUMN_TIMESTAMP] < end),
                "Label"
            ] = activity
