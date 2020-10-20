class SensorModel:

    def __init__(self, id_=None, name=None, date_row=None, time_row=None, timestamp_column=None, relative_absolute=None,
                 timestamp_unit=None, format_string=None, sensor_id_row=None, sensor_id_column=None,
                 sensor_id_regex=None, headers_row=None, comment_style=None):
        self.id_ = id_
        self.name = name
        self.date_row = date_row
        self.time_row = time_row
        self.timestamp_column = timestamp_column
        self.relative_absolute = relative_absolute
        self.timestamp_unit = timestamp_unit
        self.format_string = format_string
        self.sensor_id_row = sensor_id_row
        self.sensor_id_col = sensor_id_column
        self.sensor_id_regex = sensor_id_regex
        self.col_names_row = headers_row
        self.comment_style = comment_style
