from datetime import datetime, timedelta
from timeit import timeit

from data_import import sensor_data as sd


def test_settings():
    settings = dict()
    settings['time_row'], settings['time_col'] = 3, 3
    settings['date_row'], settings['date_col'] = 3, 2
    settings['sr_row'], settings['sr_col'] = 5, 2
    settings['sn_row'], settings['sn_col'] = 2, 5
    settings['names_row'] = 8
    settings['comment'] = ';'

    names = ["Time", "Ax", "Ay", "Az", "Gx", "Gy", "Gz", "Mx", "My", "Mz", "T"]
    for name in names:
        settings[name + "_data_type"] = "-"
        settings[name + "_sensor_name"] = "-"
        settings[name + "_sampling_rate"] = "-"
        settings[name + "_unit"] = "-"

    settings["Ax_conversion"] = "Ax * 9.807 / 4096"
    settings["Ay_conversion"] = "Ay * 9.807 / 4096"
    settings["Az_conversion"] = "Az * 9.807 / 4096"

    settings["Gx_conversion"] = "Gx / 16.384"
    settings["Gy_conversion"] = "Gy / 16.384"
    settings["Gz_conversion"] = "Gz / 16.384"

    settings["Mx_conversion"] = "Mx / 3.413"
    settings["My_conversion"] = "My / 3.413"
    settings["Mz_conversion"] = "Mz / 3.413"

    settings["T_conversion"] = "T / 1000"

    return settings


def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped


def sensor_data_time_test():
    # Time test for creating a SensorData object and parsing a file (including metadata)
    # about 1.3472 seconds
    wrapped = wrapper(sd.SensorData, "../data/DATA-001.CSV", test_settings())
    print("parse_time_test() average of 10:", timeit(wrapped, number=10) / 10)


def add_column_time_test():
    # Time test for adding a vector column to the data
    # about 0.0129 seconds
    sensor_data = sd.SensorData("../data/DATA-001.CSV", test_settings())
    wrapped = wrapper(sensor_data.add_column_from_func, "Vector", "sqrt(Ax^2 + Ay^2 + Az^2)")
    print("add_column_time_test() average of 10:", timeit(wrapped, number=10) / 10)


def add_column_test():
    sens_data = sd.SensorData("../data/DATA-001.CSV", test_settings())
    sens_data.add_column_from_func("Vector", "sqrt(Ax^2 + Ay^2 + Az^2)")
    print(sens_data.get_data()[['Ax', 'Ay', 'Az', 'Vector']])


def datetime_test():
    date = '2018-05-15'
    time = '08:54:32.261'
    timestamp = 0.006042
    print(date + time)
    dt = datetime.strptime(date + time, '%Y-%m-%d%H:%M:%S.%f')
    return dt + timedelta(seconds=timestamp)


if __name__ == '__main__':
    sensor_data_time_test()
    add_column_time_test()
