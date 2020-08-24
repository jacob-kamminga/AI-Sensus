import re
import datetime as dt
import sqlite3
from pathlib import Path
from typing import List

import datefinder
import pandas as pd

import parse_function.custom_function_parser as parser
from constants import DATE_ROW, DATE_COLUMN, TIME_ROW, TIME_COLUMN, SENSOR_ID_ROW, SENSOR_ID_COLUMN, HEADERS_ROW, \
    COMMENT_STYLE
from data_import import sensor as sens, column_metadata as cm
from data_import.import_exception import ImportException
from database.sensor_model_manager import SensorModelManager
from parse_function.parse_exception import ParseException
from machine_learning.classifier import CLASSIFIER_NAN
from project_settings import ProjectSettings

START_TIME_INDEX = 0
STOP_TIME_INDEX = 1
LABEL_INDEX = 2
COLUMN_TIMESTAMP = "Timestamp"


def parse_header_option(file, row_nr, col_nr=1):
    """
    Parses a specific part of the header with a line number and a column number. Raises an ImportException if the file
    is smaller than the given row number or if the line is smaller than the given column number.

    :param file: file to be parsed
    :param row_nr: row number of header
    :param col_nr: column number of header data
    :return: data on row and column number
    """
    # return to start of file
    file.seek(0)

    i = 1  # row numbers start at 1

    for line in file:
        if i == row_nr:
            # Turn line into list of columns
            line_list = re.split(', *', line[1:-1])

            # If col_nr is larger than number of columns, raise ImportException
            if col_nr - 1 >= len(line_list):
                raise ImportException("Given column number exceeds number of columns in line - given column number: "
                                      + str(col_nr) + ", number of columns: " + str(len(line_list)))

            return line_list[col_nr - 1]  # column numbers start at 1
        else:
            i += 1

    # row_nr is higher than number of rows in file
    raise ImportException("Given row number exceeds numbers of rows in file - given row number: "
                          + str(row_nr) + ", number of rows: " + str(i))


def parse_names(file, row_nr):
    """
    Parses the names of the data columns using a row number. Raises an ImportException if the file is smaller than
    the given row number.

    :param file: file to be parsed
    :param row_nr: row number of names
    :return: list of column names
    """
    # return to start of file
    file.seek(0)

    i = 1
    for line in file:
        if i == row_nr:
            return re.split(', *', line[1:-1])
        else:
            i += 1
    # row_nr is higher than number of rows in file
    raise ImportException("Given row number exceeds numbers of rows in file - given row number: "
                          + str(row_nr) + ", number of rows: " + str(i))


def parse_date(file, config: sqlite3.Row):
    header_date = parse_header_option(file, config[DATE_ROW])

    matches: List[dt.datetime] = datefinder.find_dates(header_date)

    if len(matches) == 1:
        return matches[0].date().strftime('%Y-%m-%d')

    return None


def parse_time(file, config: sqlite3.Row):
    header_time = parse_header_option(file, config[TIME_ROW])

    matches: List[dt.datetime] = datefinder.find_dates(header_time)

    if len(matches) == 1:
        return matches[0].time().strftime('%H:%M:%S')

    return None


class SensorData:

    def __init__(self, file_path: Path, settings: ProjectSettings, sensor_model_id):
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
        self.metadata = dict()
        self.col_metadata = dict()

        # Parse metadata and data
        self._settings_dict = settings.settings_dict
        self._data = self.parse(self._settings_dict)
        """ The sensor data as a DataFrame. """

    def __copy__(self):
        new = type(self)(self.file_path, self.settings, self.sensor_model_id)
        new.__dict__.update(self.__dict__)
        return new

    def parse_model_config(self, file, config: sqlite3.Row):
        self.metadata['date'] = parse_date(file, config)
        self.metadata['time'] = parse_time(file, config)

        if config[SENSOR_ID_COLUMN] != -1:
            self.metadata['sn'] = parse_header_option(file, config[SENSOR_ID_ROW], config[SENSOR_ID_COLUMN])
        else:
            self.metadata['sn'] = parse_header_option(file, config[SENSOR_ID_ROW])

        self.metadata['names'] = parse_names(file, config[HEADERS_ROW])
        self.metadata[COMMENT_STYLE] = config[COMMENT_STYLE]

    def parse(self, settings_dict) -> pd.DataFrame:
        """
        Parses a csv file to get metadata and data.

        :param settings_dict: contains the metadata
        :return: the parsed data as a DataFrame
        """
        # Parse metadata from headers
        with self.file_path.open() as file:
            try:
                sensor_model = self.sensor_model_manager.get_model_by_id(self.sensor_model_id)
                self.parse_model_config(file, sensor_model)

                # Create datetime object from date and time and put it in metadata
                self.metadata['datetime'] = dt.datetime.strptime(self.metadata['date'] + self.metadata['time'],
                                                                 '%Y-%m-%d%H:%M:%S.%f')
            except ImportException:
                # Pass ImportException
                raise

        # set column metadata
        self.set_column_metadata(settings_dict)

        # Parse data from file
        data = pd.read_csv(self.file_path,
                           header=None,
                           names=self.metadata['names'],
                           comment=self.metadata[COMMENT_STYLE])

        # Pass parse exceptions on
        try:
            # Convert sensor data to correct unit
            for name in self.metadata['names']:

                # Retrieve conversion rate from column metadata
                conversion = self.col_metadata[name].sensor.conversion

                # If column doesn't have a conversion, continue to next column
                if conversion is None:
                    continue

                # Parse conversion to python readable expression
                parsed_expr = parser.parse(conversion)

                # Apply parsed expression to the data
                data.eval(name + " = " + parsed_expr, inplace=True)
        except ParseException:
            # Pass ParseException
            raise
        return data

    def set_column_metadata(self, settings):
        """
        Sets the metadata for every column using the settings_dict.
        """
        for name in self.metadata['names']:
            # parse data_type
            data_type = (settings[name + "_data_type"]
                         if name + "_data_type" in settings.keys() else None)

            # parse sensor:
            # sensor name
            sensor_name = (settings[name + "_sensor_name"]
                           if name + "_sensor_name" in settings.keys() else None)

            # sampling rate
            sr = (settings[name + "_sampling_rate"]
                  if name + "_sampling_rate" in settings.keys() else None)

            # unit of measurement
            unit = (settings[name + "_unit"]
                    if name + "unit" in settings.keys() else None)

            # conversion rate
            conversion = (settings[name + "_conversion"]
                          if name + "_conversion" in settings.keys() else None)

            # construct sensor
            sensor = sens.Sensor(sensor_name, sr, unit, conversion)

            # create new column metadata and add it to list with metadata
            self.col_metadata[name] = cm.ColumnMetadata(name, data_type, sensor)

    def get_data(self):
        return self._data.copy()

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
            self._data.eval(name + " = " + parsed_expr, inplace=True)
        except ParseException:
            # Pass ParseException
            raise

    def add_timestamp_column(self, time_col: str, time_unit='s'):
        """
        Adds a timestamp column to the sensor data.

        :param time_col: The name of the column that contains the recorded time.
        :param time_unit: The time unit of the time column.
        """
        self._data[COLUMN_TIMESTAMP] = pd.to_timedelta(self._data[time_col], unit=time_unit) + self.metadata['datetime']

    def add_labels_ml(self, label_data: [], label_col: str):
        """
        Add labels to the DataFrame for machine learning.

        :param label_data:
        :param label_col:
        :param timestamp_col:
        :return:
        """
        # Add Label column to the DataFrame and initialize it to NaN
        self._data[label_col] = CLASSIFIER_NAN

        for label_entry in label_data:
            start_time = label_entry[START_TIME_INDEX]
            stop_time = label_entry[STOP_TIME_INDEX]
            label = label_entry[LABEL_INDEX]

            # Add label to the corresponding rows in the sensor data
            self._data.loc[
                (self._data[COLUMN_TIMESTAMP] >= start_time) & (self._data[COLUMN_TIMESTAMP] < stop_time),
                label_col
            ] = label

    def filter_between_dates(self, start: dt.datetime, end: dt.datetime):
        self._data = self._data[(self._data[COLUMN_TIMESTAMP] >= start) & (self._data[COLUMN_TIMESTAMP] < end)]

    def add_labels(self, labels):
        """
        Add labels to the DataFrame for exporting.

        :param labels:
        :return:
        """
        self._data["Label"] = ""

        for label in labels:
            start = label["start"]
            end = label["end"]
            activity = label["activity"]

            self._data.loc[
                (self._data[COLUMN_TIMESTAMP] >= start) & (self._data[COLUMN_TIMESTAMP] < end),
                "Label"
            ] = activity
