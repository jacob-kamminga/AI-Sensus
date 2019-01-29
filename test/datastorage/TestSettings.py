import shutil
import unittest
from datastorage.settings import *
import os.path


class TestSettings(unittest.TestCase):

    def tearDown(self):
        shutil.rmtree('projects/new_project')

    def test_get_set_setting(self):
        self.assertFalse(os.path.isdir('projects/new_project'))
        new_project('new_project')  # create a new project
        self.assertTrue(os.path.isdir('projects/new_project'))
        self.assertTrue(os.path.isfile('projects/new_project/' + settings_file_name))
        self.assertTrue(os.path.isfile('projects/new_project/project_data.db'))

        s1 = Settings('new_project')
        self.assertIs(None, s1.get_setting('test_setting1'))  # setting 'test_setting1' should not be set yet
        s1.set_setting('test_setting1', 'test_value')         # set the value of 'test_setting1' to 'test_value'

        s2 = Settings('new_project')                                    # create a new Settings instance
        self.assertEqual('test_value', s2.get_setting('test_setting1'))  # 'test_setting1' should return 'test_value'
        s2.set_setting('test_setting2', 42)
        self.assertEqual(42, s2.get_setting('test_setting2'))  # integer values should also work
