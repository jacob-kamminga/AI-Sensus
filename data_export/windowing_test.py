import csv
import numpy as np
from timeit import timeit

from data_import import sensor_data as sd
from data_import.sensor_data_test import test_settings as settings
import pandas as pd
from data_export import windowing as w
from datetime import timedelta, datetime
from data_export import export_data as ed


def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)

    return wrapped


def test_sensor_data():
    sensor_data = sd.SensorData("../data/20180515_09-58_CCDC301661B33D7_sensor.csv", settings())
    file = open('../data/20180515_09-58_CCDC301661B33D7_labels.csv')
    labels = csv.reader(file)
    next(labels)
    labels = sorted(labels, key=lambda row: row[0])

    file.close()

    res = []
    for i in range(len(labels) - 1):
        res.append([labels[i][0], labels[i + 1][0], labels[i][1]])

    sensor_data.add_timestamp_column('Time', 'Timestamp')
    sensor_data.add_labels(res, 'Label', 'Timestamp')

    return sensor_data.get_data()


def small_data_test():
    timestamps = []
    for i in range(20):
        timestamps.append(datetime(2000, 1, 1, 0, 0, 0) + timedelta(milliseconds=i*500))
    df = pd.DataFrame({'Timestamp': timestamps,
                       'Data': list(range(20))})

    df1 = df.rolling(window='2s', on='Timestamp').mean()
    print(df)
    print(df1)

    start = df['Timestamp'].iloc[0]
    pivot = start + timedelta(seconds=1)
    cutoff = df.loc[df['Timestamp'] == w.nearest(df['Timestamp'].tolist(), pivot)]
    rps = cutoff.index[0] - df.index[0]
    print('rows per second:', rps)

    df2 = df1[rps*2 - 1::rps]
    print(df2)


def windowing_test():
    df = test_sensor_data()
    print("DataFrame constructed")

    # Get columns to be windowed over
    collist = df.columns.tolist()
    collist.remove('Label')
    collist.remove('Timestamp')
    collist.remove('Time')

    n = 10
    wrapped = wrapper(w.windowing, df.head(6000), collist, 'Label', 'Timestamp',
                      mean=np.mean, std=np.std, max=np.max, min=np.min)
    print('windowing average of %s:' % n, timeit(wrapped, number=n) / n)
    # return w.windowing(df, ['Ax', 'Ay', 'Az'], 'Label', 'Timestamp', mean=np.mean, std=np.std)


def windowing_fast_test():
    df = test_sensor_data()
    print("DataFrame constructed")

    # Get columns to be windowed over
    collist = df.columns.tolist()
    collist.remove('Label')
    collist.remove('Timestamp')
    collist.remove('Time')

    # Time test
    n = 10
    wrapped = wrapper(w.windowing_fast, df.head(6000), collist)
    print('windowing_fast average of %s:' % n, timeit(wrapped, number=n) / n)

    # return w.windowing_fast(df, ['Ax', 'Ay', 'Az'])


def export_test():
    df = test_sensor_data()
    print("DataFrame constructed")

    c1 = 'First 5000 rows of test DataFrame are windowed'
    c2 = 'This is a simple test comment'

    ed.export([df.head(5000)], 'Label', 'Timestamp', '../data/test_export.csv', [c1, c2])


if __name__ == '__main__':
    # export_test()
    windowing_test()
    windowing_fast_test()
