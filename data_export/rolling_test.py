import csv
from data_import import sensor_data as sd
from data_import.sensor_data_test import test_settings as settings
import numpy as np
from data_export import windowing as w


def split_df(df, col):
    """
    Splits a data frame into multiple data frames based on the given column; if the column value
    changes, a new data frame is created. Changes are stored in a temporary pandas Series,
    which has a False value for every new value in the given column.

    :param df: The data frame that will be split up
    :param col: The column that determines the split locations
    :return: A list with the split data frames
    """
    # Create boolean column where every False signals a new value
    temp = df[col].eq(df[col].shift())

    # Create a difference data frame with only the rows
    # of the changed values
    df_diff = df[temp == 0]

    # Get the difference data frame index
    idx = df_diff.index.tolist()

    # Determine last index of original data frame
    last = df.index.tolist()[-1]

    result = []
    for i in range(len(idx) - 1):
        # Slice original data frame from changed value until the next
        new_df = df.loc[idx[i]:idx[i + 1] - 1]

        # Add data frame to result list
        result.append(new_df)

    # Slice the last part of the data frame and add it to the result list
    last_df = df.loc[idx[len(idx) - 1]:last]
    result.append(last_df)
    return result


def nearest(items, pivot):
    """
    Finds the item in a list of items closest to a pivot.
    :param items: List of items
    :param pivot: Pivot looked for in the list.
    :return: Item in the list closest to the pivot.
    """
    return min(items, key=lambda x: abs(x - pivot))


def test_sensor_data():
    sensor_data = sd.SensorData("../data/20180515_09-58_CCDC301661B33D7_sensor.csv", settings())
    file = open('../data/20180515_09-58_CCDC301661B33D7_labels.csv')
    labels = csv.reader(file)
    next(labels)
    labels = sorted(labels, key=lambda row: row[0])

    res = []
    for i in range(len(labels) - 1):
        res.append([labels[i][0], labels[i + 1][0], labels[i][1]])

    sensor_data.add_timestamp_column('Time', 'Timestamp')
    sensor_data.add_labels(res, 'Label', 'Timestamp')

    return sensor_data.get_data()


if __name__ == '__main__':
    df = test_sensor_data()
    print('DataFrame constructed')

    df = df.drop('Label', axis=1)
    print('label column dropped')

    roll = df.rolling(window='2s', on='Timestamp')
    print('rolling finished')

    df2 = roll.mean()
    print('mean finished')

    df3 = roll.apply(np.mean, raw=True)
    print('np.mean finished')
    pass
