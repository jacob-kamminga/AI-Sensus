import shutil
import sys
import unittest
from datetime import datetime
from pathlib import Path

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

import constants
from database.models import SensorModel, Camera, SensorDataFile, Sensor, Video
from gui import gui


class TestAll(unittest.TestCase):
    """
    1. Setup GUI
    2. Create new project at test location
    3. Create camera
    4. Open dummy video
    5. Insert test sensor
    6. Insert test sensor model
    3. Open test sensor data file
    7. Create 3 test annotations
    8. Export to .csv
    9. Compare to handmade file
    """

    def setUp(self) -> None:
        print("setUp()")
        # Run unittests in the order in which they are defined.
        unittest.defaultTestLoader.sortTestMethodsUsing = lambda *args: -1

        self.app = QApplication(sys.argv)
        self.gui = gui.GUI(app_config_file=Path.cwd() / 'test_app_config.json', testing=True)
        self.cwd = Path.cwd()

    def test_all(self):
        print("test_all()")

        ########## testCreateNewProject ##########
        self.project_name = "Unittest-" + datetime.now().strftime('%H%M%S')
        self.gui.project_controller.create_new_project(new_project_name=self.project_name,
                                                       new_project_dir=self.cwd)
        self.gui.reset_gui_components()
        self.gui.project_controller.set_setting('timezone', 'Europe/Amsterdam')
        self.gui.init_project()

        self.project_dir = self.cwd / self.project_name
        self.assertTrue(self.project_dir.is_dir())
        self.assertTrue((self.project_dir / constants.PROJECT_CONFIG_FILE).is_file())
        self.assertTrue((self.project_dir / constants.PROJECT_DATABASE_FILE).is_file())

        ########## testCreateNewCamera ##########
        cam_controller = self.gui.camera_controller
        camera = Camera(name="test_camera",
                        timezone='Europe/Amsterdam',
                        manual_offset=0)
        camera.save()

        cam_controller.change_camera(Camera.get(name="test_camera").id)
        self.assertEqual(self.gui.camera_controller.camera, Camera.get(name="test_camera"))

        ########## testAddSensorModel ##########
        test_sensor_model = SensorModel(id_=1,
                                        model_name="test_sensor_model",
                                        date_row=-1,
                                        time_row=-1,
                                        timestamp_column=1,
                                        relative_absolute="absolute",
                                        timestamp_unit="seconds",
                                        format_string="%d-%m-%y %H:%M:%S.%f",
                                        sensor_id_row=-1,
                                        sensor_id_column=-1,
                                        # sensor_id_regex="",
                                        col_names_row=0,
                                        # comment_style=""
                                        )
        test_sensor_model.save()
        self.assertEqual(SensorModel.get(model_name="test_sensor_model"), test_sensor_model)

        ########## testAddSensor        ##########
        self.gui.sensor_controller.add_sensor(name="test_sensor",
                                              sensor_model=test_sensor_model,
                                              timezone='Europe/Amsterdam')

        self.gui.sensor_controller.update_sensor(sensor_id=test_sensor_model.id)

        ########## testAddSensorDataFile ##########
        sdf_path = self.cwd / 'fixtures' / 'WolvendataCaleb15092015.csv'
        sdf = SensorDataFile(file_id_hash=self.gui.sensor_controller.create_file_id(sdf_path),
                             file_name=sdf_path.name,
                             file_path=sdf_path,
                             sensor=Sensor.get(name="test_sensor").id
                             )
        sdf.save()

        # See if the SDF is stored in the database and can be retrieved properly.
        sdf = self.gui.sensor_controller.get_or_create_sdf(sdf_path)
        self.assertEqual(sdf, SensorDataFile.get_by_id(sdf.id))

        # Load the sdf as if it was an ordinary file.
        self.gui.sensor_controller.open_file(sdf_path)
        self.assertEqual(list(self.gui.sensor_controller.df.columns), ['Relative Time', 'absolute_datetime',
                                                                       'Ax', 'Ay', 'Az'])
        ########## testOpenVideo ##########

        # TODO: If the video has not been loaded in before, the attached camera won't exist, causing a manual prompt
        #  to select a camera. Verify that this should always be the case, or if the currently selected camera (if any)
        #  should automatically be attached to the video, and saved in the database together.
        video_path = self.cwd / 'fixtures' / '00001.MTS'
        video = Video(file_name=video_path.name,
                      file_path=video_path,
                      datetime=datetime.now(),
                      camera=Camera.get(name="test_camera").id)
        video.save()
        self.gui.video_controller.open_file(video_path)

        ########## testAddAnnotations ##########

        ########## testExport ##########

        ########## testCompareOutput ##########

        ########## Compare hashes ##########

    def tearDown(self) -> None:
        print("tearDown()")
        self.gui.project_controller.close_db()  # Close the connection to the database to release the file.
        shutil.rmtree(self.project_dir)  # Delete the test project folder and its contents.
        self.gui.app_controller.app_config_file.unlink()  # Delete the app config file.
