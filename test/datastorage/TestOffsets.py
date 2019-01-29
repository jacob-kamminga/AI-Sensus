import unittest
from datastorage.deviceoffsets import *


class TestOffsets(unittest.TestCase):

    o = OffsetManager()

    def setUp(self):
        self.o.create_table()

    def tearDown(self):
        self.o._cur.execute('DROP TABLE offsets')

    def test_get_offset(self):
        self.assertEqual(0, self.o.get_offset(
            'camera1', 'sensor1', date(2018, 9, 23)))  # no offset known at all, should be 0
        self.o._cur.execute('INSERT INTO offsets(Camera, Sensor, Offset, Date) VALUES (?,?,?,?)',
                            ('camera1', 'sensor1', 10, date(2018, 9, 24)))
        self.assertEqual(5, self.o.get_offset(
            'camera1', 'sensor1', date(2018, 9, 25)))  # offsets 0 and 10 known, should be 5
        self.assertEqual(10, self.o.get_offset(
            'camera1', 'sensor1', date(2018, 9, 24)))  # should be 10

    def test_set_offset(self):
        self.o.get_offset('camera1', 'sensor1', date(2018, 9, 23))      # will set this offset to 0
        self.o.set_offset('camera1', 'sensor1', 10, date(2018, 9, 23))  # set that offset to 10
        self.assertEqual(10, self.o.get_offset('camera1', 'sensor1', date(2018, 9, 23)))  # should be 10
