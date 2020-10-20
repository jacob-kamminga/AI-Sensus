import datetime as dt
from pathlib import Path

import pandas as pd
import pytz

import parse_function.custom_function_parser as parser
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
        """
        The SensorData starts parsing as soon as it's constructed. Only SensorData.get_data() needs to
        be called in order to get the parsed data. SensorData.metadata contains the metadata.

        :param file_path: path to the file to be parsed
        :param settings: The settings_dict dictionary contains information on where metadata can
        be found in the parsed file. It should have the following keys in order for it to work:

            - time_row, time_col   (row and column where 'time' attribute is located)
            - date_row, date_col   (row and column where 'date' attribute is located)
            - sr_row, sr_col       (row and column where 'sampling rate' attribute is located)
            - sn_row, sn_col       (row and column where 'serial number' attribute is located)
            - names_row            (row where the names of the columns are located)

            - comment              (symbol used to indicate a comment !this is a value, not a location!)

        The next keys are variable depending on the name of the column (these are not locations, but values!):

            - <name>_data_type     (data type of the column)
            - <name>_sensor_name   (name of the sensor used)
            - <name>_sampling_rate (sampling rate of the sensor)
            - <name>_unit          (unit of measurement of the sensor)
            - <name>_conversion    (conversion function for the data,
                                    for more information on the function see parse_function.custom_function_parser)
        """
        # Initialize primitives
        self.settings = settings
        self.sensor_model_manager = SensorModelManager(self.settings)
        self.file_path = file_path

        self.sensor_model_id = sensor_model_id
        self.sensor_model = self.sensor_model_manager.get_model_by_id(sensor_model_id)
        self.metadata = SensorMetadata(self.file_path, self.sensor_model)
        self.col_metadata = dict()
        self.project_timezone = pytz.timezone(settings.get_setting('timezone'))
        self.sensor_timezone = sensor_timezone

        # Parse metadata and data
        self._settings_dict = settings.settings_dict
        self._df = self.parse()
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
                         skiprows=self.sensor_model.col_names_row,
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
            start = label["start"]
            end = label["end"]
            activity = label["activity"]

            self._df.loc[
                (self._df[COLUMN_TIMESTAMP] >= start) & (self._df[COLUMN_TIMESTAMP] < end),
                "Label"
            ] = activity
