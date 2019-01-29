import unittest
from datastorage.labelstorage import *


class TestLabels(unittest.TestCase):

    l = LabelManager('test_project')

    def setUp(self):
        self.l.create_tables()

    def tearDown(self):
        self.l._cur.execute('DROP TABLE labelType')
        self.l._cur.execute('DROP TABLE labelData')
        self.l._cur.execute('DROP TABLE fileMapping')

    def test_add_del_label_type(self):
        self.l.add_label_type('label1', "red", 'This is a test label')     # add new label type with name 'label1'
        self.assertNotEqual(0, len(self.l.get_label_types()))  # new label type should be in the table
        self.l.add_label(datetime.now(), datetime.now(), 'label1', 'sensor1')  # create a label with the new type
        self.l.delete_label_type('label1')
        self.assertEqual(0, len(
            self.l._cur.execute('SELECT * FROM labelType').fetchall()))  # label type should not be in the table
        self.assertEqual(0, len(
            self.l._cur.execute('SELECT * FROM labelData').fetchall()))  # label should not be in the table

    def test_add_del_label(self):
        label_time = datetime.now()
        self.l.add_label(label_time, label_time, 'label1', 'sensor1')    # add new label at time 1.5 to sensor 'sensor1'
        self.assertNotEqual(0, len(self.l.get_all_labels('sensor1')))  # new label should be in the table
        self.assertNotEqual(0, len(self.l.get_labels_date('sensor1', label_time.date())))
        self.assertNotEqual(0, len(self.l.get_labels_between_dates('sensor1', label_time, label_time)))
        self.l.delete_label(label_time, 'sensor1')
        self.assertEqual(0, len(self.l.get_all_labels('sensor1')))  # label should not be in the table
        self.assertEqual(0, len(self.l.get_labels_date('sensor1', label_time.date())))
        self.assertEqual(0, len(self.l.get_labels_between_dates('sensor1', label_time, label_time)))

    def test_update_label_type(self):
        label_time = datetime.now()
        self.l.add_label_type('label1', "red", 'This is a test label')   # add new label type with name 'label1'
        self.l.add_label(label_time, label_time, 'label1', 'sensor1')  # create a label with the new type
        self.assertEqual('label1', self.l._cur.execute('SELECT Name FROM labelType')
                         .fetchone()[0])  # label type name should be 'label1'
        self.assertEqual("red", self.l._cur.execute('SELECT Color FROM labelType')
                         .fetchone()[0])  # label type color should be "red"
        self.assertEqual('This is a test label', self.l._cur.execute('SELECT Description FROM labelType')
                         .fetchone()[0])  # label type description should be 'This is a test label'
        self.l.update_label_color('label1', "blue")
        self.assertEqual("blue", self.l._cur.execute('SELECT Color FROM labelType')
                         .fetchone()[0])  # label type color should now be "blue"
        self.l.update_label_description('label1', 'This is a changed description')
        self.assertEqual('This is a changed description', self.l._cur.execute('SELECT Description FROM labelType')
                         .fetchone()[0])  # label type description should now be 'This is a changed description'
        self.l.update_label_name('label1', 'label2')
        self.assertEqual('label2', self.l._cur.execute('SELECT Name FROM labelType')
                         .fetchone()[0])  # label type name should now be 'label2'
        self.assertEqual('label2', self.l._cur.execute('SELECT Label_name FROM labelData')
                         .fetchone()[0])  # label created with the label type should also be named 'label2' now

    def test_file_mapping(self):
        date = datetime.now()
        self.l.add_file('file.txt', 'sensor', date)
        self.assertTrue(self.l.file_is_added('file.txt'))
        self.assertIn('file.txt', self.l.get_file_paths('sensor', date, date))
        self.assertIn('sensor', self.l.get_sensor_ids())
