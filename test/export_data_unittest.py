import filecmp
import os
import unittest

from data_export import export_data as ed
from data_export import windowing_test as wt


class ExportDataTestCase(unittest.TestCase):

    def setUp(self):
        df = wt.test_sensor_data()
        self.dfs = [df.head(1000), df.iloc[1000:2000], df.iloc[2000:3000], df.tail(1000)]

    def test_export(self):
        file_path1 = '../data/export_unit_test1.csv'
        file_path2 = '../data/export_unit_test2.csv'
        ed.export(self.dfs, 'Label', 'Timestamp', file_path1, [])
        ed.export(self.dfs, 'Label', 'Timestamp', file_path2, [])

        self.assertEqual(True, filecmp.cmp(file_path1, file_path2),
                         'Exported files are not equal')

        # Remove file after test
        if os.path.exists(file_path1):
            os.remove(file_path1)
        else:
            print('%s does not exist' % file_path1)

        if os.path.exists(file_path2):
            os.remove(file_path2)
        else:
            print('%s does not exist' % file_path2)
