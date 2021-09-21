import shutil
import sys
import unittest
from datetime import datetime
from pathlib import Path

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

import constants
from gui import gui


class TestLabels(unittest.TestCase):
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
        # Run unittests in the order in which they are defined.
        unittest.defaultTestLoader.sortTestMethodsUsing = lambda *args: -1

        self.app = QApplication(sys.argv)
        self.main_window = gui.GUI(app_config_file=Path.cwd() / 'test_app_config.json')
        self.cwd = Path.cwd()

    def testCreateNewProject(self):
        self.project_name = "Unittest-" + datetime.now().strftime('%H%M%S')
        self.main_window.project_controller.create_new_project(new_project_name=self.project_name,
                                                               new_project_dir=self.cwd)
        self.main_window.reset_gui_components()
        self.main_window.project_controller.set_setting('timezone', 'Europe/Amsterdam')
        self.main_window.init_project()

        self.project_dir = self.cwd / self.project_name
        self.assertTrue(self.project_dir.is_dir())
        self.assertTrue((self.project_dir / constants.PROJECT_CONFIG_FILE).is_file())
        self.assertTrue((self.project_dir / constants.PROJECT_DATABASE_FILE).is_file())

    def testCreateNewCamera(self):
        cam_controller = self.main_window.camera_controller
        cam_controller.add_camera("Unittest")
        camera_id = cam_controller.get_camera_id_by_name("Unittest")
        cam_controller.change_camera(camera_id)

    def testOpenSensorData(self):
        # Vraag aan Dennis: Hoe voeg ik programmatisch een Sensor Model toe (dus zonder dialogs)?
        sensor_data_file_path = self.cwd / 'fixtures'/ 'WolvendataCaleb15092015.xlsx'
        self.main_window.sensor_controller.open_file(sensor_data_file_path)
        self.assertTrue(True)

    # def testOpenVideo(self):
    #     pass
    #
    # def testAddSensor(self):
    #     pass
    #
    # def testAddSensorModel(self):
    #     pass
    #
    # def testAddAnnotations(self):
    #     pass
    #
    # def testExport(self):
    #     pass
    #
    # def testCompareOutput(self):
    #     pass

    def tearDown(self) -> None:
        self.main_window.project_controller.close_db()  # Close the connection to the database to release the file.
        shutil.rmtree(self.project_dir)  # Delete the test project folder and its contents.
        self.project_dir.unlink()  # Delete the app config file.

