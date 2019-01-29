import unittest
from datastorage.camerainfo import *


class TestCameras(unittest.TestCase):

    c = CameraManager()

    def setUp(self):
        self.c.create_table()

    def tearDown(self):
        self.c._cur.execute('DROP TABLE cameras')

    def test_add_del_camera(self):
        self.c.add_camera('camera1')                    # add new camera with name 'camera1'
        self.assertEqual('camera1', self.c.get_all_cameras()[0])  # there should be a camera with name 'camera1'
        self.c.delete_camera('camera1')
        self.assertEqual(0, len(self.c._cur.execute(
            'SELECT * FROM cameras').fetchall()))       # the camera should not be there anymore
