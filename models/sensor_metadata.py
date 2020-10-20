import datetime as dt

import dateutil.parser
import pytz

from date_utils import naive_to_utc
from models.sensor_model import SensorModel


class Metadata:

    def __init__(self, file_path, sensor_model: SensorModel, sensor_id=None, utc_dt=None, sensor_timezone=pytz.utc):
        self.file_path = file_path
        self.sensor_model = sensor_model
        self.sensor_id = sensor_id
        self.utc_dt = utc_dt
        self.sensor_timezone = sensor_timezone
        self.headers = None

        self._metadata_list = None
        self.col_names = None

        self._parse_metadata()

    def _parse_metadata(self):
        comment = self.sensor_model.comment_style
        header_rows = []

        with self.file_path.open() as f:
            # Parse all
            for i in range(self.sensor_model.col_names_row):
                line = f.readline()

                if comment and line.startswith(comment):
                    # Remove the leading comment char
                    line = line[len(comment):]

                if i == self.sensor_model.col_names_row - 1:
                    self.col_names = line.strip().split(',')
                else:
                    header_rows.append(line)

            self._metadata_list = [value.strip().split(',') for value in header_rows]

    def _get_value(self, row, col=-1):
        """
        Parses a specific part of the header with a line number and a column number. Raises an ImportException if the
        file is smaller than the given row number or if the line is smaller than the given column number.

        :param row: row number of header
        :param col: column number of header data
        :return: data on row and column number
        """
        if col > -1:
            return self._metadata_list[row - 1][col - 1]
        else:
            return ''.join(self._metadata_list[row - 1])

    def parse_datetime(self):
        # Automatically parse date and time from string
        date_row = self._get_value(self.sensor_model.date_row)
        date = dateutil.parser.parse(date_row, fuzzy=True).date()
        time = dateutil.parser.parse(self._get_value(self.sensor_model.time_row), fuzzy=True).time()

        # Create datetime object from date and time
        naive_dt = dt.datetime.combine(date, time)

        # Convert naive datetime to UTC
        self.utc_dt = naive_to_utc(naive_dt, self.sensor_timezone)

    def load_values(self):
        self.sensor_id = self._get_value(self.sensor_model.sensor_id_row, self.sensor_model.sensor_id_col)
