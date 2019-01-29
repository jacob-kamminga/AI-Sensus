import numpy as np
import unittest
from sklearn.naive_bayes import GaussianNB

from data_export import windowing as wd
from data_import import sensor_data as sd
from data_import import sensor_data_test as sdt
from data_import import label_data as ld
from datastorage import labelstorage as ls
from machine_learning import classifier as clsf


SENSOR_FILE = 'data/20180515_09-58_CCDC301661B33D7_sensor.csv'
PROJECT_DIR = 'test_project'
SENSOR_ID = 'CCDC301661B33D7'

LABEL_COL = 'Label'
TIME_COL = 'Time'
TIMESTAMP_COL = 'Timestamp'


class TestClassifier(unittest.TestCase):
    sensor_data = sd.SensorData(SENSOR_FILE, sdt.test_settings())
    label_manager = ls.LabelManager(PROJECT_DIR)
    label_data = ld.LabelData(label_manager, SENSOR_ID)

    # Prepare the sensor data for use by classifier
    sensor_data.add_timestamp_column(TIME_COL, TIMESTAMP_COL)
    sensor_data.add_column_from_func('accel', 'sqrt(Ax^2 + Ay^2 + Az^2)')
    sensor_data.add_column_from_func('gyro', 'sqrt(Gx^2 + Gy^2 + Gz^2)')
    sensor_data.add_labels(label_data.get_data(), LABEL_COL, TIMESTAMP_COL)
    data = sensor_data.get_data()

    # Remove data points where label == 'unknown'
    data = data[data.Label != 'unknown']

    window_cols = ['accel', 'gyro']
    used_cols = []
    funcs = {
        'mean': np.mean,
        'median': np.median,
        'std': np.std,
    }

    for func in funcs:
        for col in window_cols:
            used_cols.append('%s_%s' % (col, func))

    df = wd.windowing(data, window_cols, LABEL_COL, TIMESTAMP_COL, **funcs)
    classifier = clsf.Classifier(GaussianNB(), df, used_cols)

    def test_classify(self):
        res = self.classifier.classify()

        print(res)

    def test_make_predictions(self):
        res = self.classifier.classify()
        predictions = clsf.make_predictions(res)

        print(predictions)


if __name__ == '__main__':
    unittest.main()
