import unittest
import pandas as pd
import numpy as np
from data_export import windowing as w
from data_export import windowing_test as wt


class WindowingTestCase(unittest.TestCase):

    def setUp(self):
        self.df = wt.test_sensor_data()

    def test_split_df(self):
        split = w.split_df(self.df, 'Label')

        for df in split:
            equals = pd.unique(df['Label'].values)
            self.assertEqual(1, len(equals), 'Label column should only contain 1 unique value')

    def test_windowing(self):
        windowed = w.windowing(self.df.head(5000), ['Ax', 'Ay', 'Az'], 'Label', 'Timestamp', mean=np.mean, std=np.std)

        self.assertEqual(['Ax_mean', 'Ax_std', 'Ay_mean', 'Ay_std', 'Az_mean', 'Az_std', 'Label'],
                         windowed.columns.tolist(), 'Column names are incorrect')

    def test_windowing_fast(self):
        collist = self.df.columns.tolist()
        collist.remove('Label')
        collist.remove('Timestamp')
        collist.remove('Time')

        windowed_fast = w.windowing_fast(self.df.head(5000), collist)

        self.assertEqual(['Ax_25_percentile', 'Ax_75_percentile', 'Ax_kurtosis', 'Ax_max', 
                          'Ax_mean', 'Ax_median', 'Ax_min', 'Ax_skewness', 'Ax_std',
                          'Ay_25_percentile', 'Ay_75_percentile', 'Ay_kurtosis', 'Ay_max',
                          'Ay_mean', 'Ay_median', 'Ay_min', 'Ay_skewness', 'Ay_std',
                          'Az_25_percentile', 'Az_75_percentile', 'Az_kurtosis', 'Az_max',
                          'Az_mean', 'Az_median', 'Az_min', 'Az_skewness', 'Az_std',
                          'Gx_25_percentile', 'Gx_75_percentile', 'Gx_kurtosis', 'Gx_max',
                          'Gx_mean', 'Gx_median', 'Gx_min', 'Gx_skewness', 'Gx_std',
                          'Gy_25_percentile', 'Gy_75_percentile', 'Gy_kurtosis', 'Gy_max',
                          'Gy_mean', 'Gy_median', 'Gy_min', 'Gy_skewness', 'Gy_std',
                          'Gz_25_percentile', 'Gz_75_percentile', 'Gz_kurtosis', 'Gz_max',
                          'Gz_mean', 'Gz_median', 'Gz_min', 'Gz_skewness', 'Gz_std',
                          'Label',
                          'Mx_25_percentile', 'Mx_75_percentile', 'Mx_kurtosis', 'Mx_max',
                          'Mx_mean', 'Mx_median', 'Mx_min', 'Mx_skewness', 'Mx_std',
                          'My_25_percentile', 'My_75_percentile', 'My_kurtosis', 'My_max',
                          'My_mean', 'My_median', 'My_min', 'My_skewness', 'My_std',
                          'Mz_25_percentile', 'Mz_75_percentile', 'Mz_kurtosis', 'Mz_max',
                          'Mz_mean', 'Mz_median', 'Mz_min', 'Mz_skewness', 'Mz_std',
                          'T_25_percentile', 'T_75_percentile', 'T_kurtosis', 'T_max',
                          'T_mean', 'T_median', 'T_min', 'T_skewness', 'T_std'],
                         windowed_fast.columns.tolist(), 'Column names are incorrect')
