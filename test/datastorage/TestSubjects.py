import unittest
import os
from datetime import datetime

from datastorage.subjectmapping import SubjectManager
from datastorage.settings import Settings


class TestSubjects(unittest.TestCase):
    s = None

    def setUp(self):
        Settings('test_project', True)
        self.s = SubjectManager('test_project')
        self.s.create_table()

    def tearDown(self):
        self.s._cur.execute('DROP TABLE subject_map')
        os.remove('projects/test_project/settings.pkl')

    def test_add_subject(self):
        self.s.add_subject('subject')
        self.assertIn('subject', self.s.get_subjects())
        self.s.update_subject('subject', 'new_subject')
        self.assertNotIn('subject', self.s.get_subjects())
        self.assertIn('new_subject', self.s.get_subjects())
        self.s.delete_subject('subject')
        self.assertNotIn('subject', self.s.get_subjects())

    def test_update_subject_info(self):
        date = datetime.now()
        self.s.add_subject('subject')
        self.s.update_sensor('subject', 'sensor1')
        self.assertEqual('sensor1', self.s._cur.execute('SELECT Sensor FROM subject_map').fetchone()[0])
        self.s.update_start_date('subject', date)
        self.assertEqual(date, self.s._cur.execute('SELECT Start_date FROM subject_map').fetchone()[0])
        self.s.update_end_date('subject', date)
        self.assertEqual(date, self.s._cur.execute('SELECT End_date FROM subject_map').fetchone()[0])

    def test_user_columns(self):
        self.s.add_subject('subject')
        self.assertNotIn('column1', self.s.get_table()[0])  # 'column1' should not be a known column
        self.s.add_column('column1')
        self.assertIn('column1', self.s.get_table()[0])  # 'column1' should now be a known column
        self.assertNotEqual('test value', self.s.get_table()[1][0][4])
        self.s.update_user_column('column1', 'subject', 'test value')
        self.assertEqual('test value', self.s.get_table()[1][0][4])

        self.s.change_column_name('column1', 'column2')
        self.assertNotIn('column1', self.s.get_table()[0])  # 'column1' should not be a known column
        self.assertIn('column2', self.s.get_table()[0])  # 'column2' should now be a known column
        self.assertEqual('test value', self.s.get_table()[1][0][4])  # value of the column should be the same
        self.s.update_user_column('column2', 'subject', 'updated test value')
        self.assertEqual('updated test value', self.s.get_table()[1][0][4])  # value of the column should be updated

        self.s.delete_column('column2')
        self.assertNotIn('column2', self.s.get_table()[0])  # 'column2' should not be a known column
        self.assertEqual(4, len(self.s.get_table()[1][0]))  # only the 4 standard columns (subject name, start date,
        # end date, sensor id) should be returned
