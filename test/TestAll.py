import shutil
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

import constants
from database.models import SensorModel, Camera, SensorDataFile, Sensor, Video, Subject, Label, LabelType, \
    SubjectMapping
from gui import gui

from gui.dialogs.export_progress_dialog import ExportProgressDialog
import pytz

import pandas as pd


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

        # Delete the old project folders and their contents.
        self.cwd = Path.cwd()
        old_unittests = [dir_ for dir_ in self.cwd.glob('*/') if dir_.is_dir() and 'Unittest' in dir_.name]
        for dir_ in old_unittests:
            try:
                shutil.rmtree(dir_)
            except PermissionError:
                continue

        self.app = QApplication(sys.argv)

        self.gui = gui.GUI(app_config_file=self.cwd / 'test_app_config.json', testing=True)

        self.project_name = "Unittest-" + datetime.now().strftime('%H%M%S')
        self.gui.project_controller.create_new_project(new_project_name=self.project_name,
                                                       new_project_dir=self.cwd)
        self.gui.reset_gui_components()
        self.gui.project_controller.set_setting('timezone', 'US/Central')
        self.gui.init_project()

    def test_all(self):
        print("test_all()")

        ########## testCreateNewProject ##########
        self.project_dir = self.cwd / self.project_name
        self.assertTrue(self.project_dir.is_dir(), msg="The project directory does not exist.")
        self.assertTrue((self.project_dir / constants.PROJECT_CONFIG_FILE).is_file(),
                        msg="The project config file does not exist.")
        self.assertTrue((self.project_dir / constants.PROJECT_DATABASE_FILE).is_file(),
                        msg="The database does not exist.")

        ########## testCreateNewCamera ##########
        cam_controller = self.gui.camera_controller
        camera = Camera(name="test_camera",
                        timezone='US/Central',
                        manual_offset=0)
        camera.save()

        cam_controller.change_camera(Camera.get(name="test_camera").id)
        self.assertEqual(self.gui.camera_controller.camera, Camera.get(name="test_camera"),
                         msg="The camera object was not stored or retrieved from the database properly.")

        ########## testAddSensorModel ##########
        test_sensor_model = SensorModel(id_=1,
                                        model_name="test_sensor_model",
                                        date_row=-1,
                                        time_row=-1,
                                        timestamp_column=1,
                                        relative_absolute="absolute",
                                        timestamp_unit="seconds",
                                        format_string="%d/%m/%Y %H:%M:%S.%f",
                                        sensor_id_row=-1,
                                        sensor_id_column=-1,
                                        # sensor_id_regex="",
                                        col_names_row=0,
                                        # comment_style=""
                                        )
        test_sensor_model.save()
        self.assertEqual(SensorModel.get(model_name="test_sensor_model"), test_sensor_model,
                         msg="The sensor model was not stored or retrieved from the database properly.")

        ########## testAddSensor        ##########
        self.gui.sensor_controller.add_sensor(name="test_sensor",
                                              sensor_model=test_sensor_model,
                                              timezone='US/Central')

        self.gui.sensor_controller.update_sensor(sensor_id=test_sensor_model.id)

        ########## testAddAnnotations ##########
        test_subject = Subject(name="test_subject")
        test_subject.save()

        test_activity1 = LabelType(activity='test_activity1', color='red', description="", keyboard_shortcut="a")
        test_activity2 = LabelType(activity='test_activity2', color='green', description="", keyboard_shortcut="b")
        test_activity3 = LabelType(activity='test_activity3', color='blue', description="", keyboard_shortcut="c")
        test_activity4 = LabelType(activity='test_activity4', color='magenta', description="", keyboard_shortcut="d")
        test_activity5 = LabelType(activity='test_activity5', color='cyan', description="", keyboard_shortcut="e")
        test_activity6 = LabelType(activity='test_activity6', color='yellow', description="", keyboard_shortcut="f")

        test_activity1.save()
        test_activity2.save()
        test_activity3.save()
        test_activity4.save()
        test_activity5.save()
        test_activity6.save()

        ########## testAddSensorDataFile ##########
        sdf1_path = self.cwd / 'fixtures' / 'first_half_test_data.csv'
        sdf1 = SensorDataFile(file_id_hash=self.gui.sensor_controller.create_file_id(sdf1_path),
                              file_name=sdf1_path.name,
                              file_path=sdf1_path,
                              sensor=Sensor.get(name="test_sensor").id
                              )
        sdf1.save()

        sdf2_path = self.cwd / 'fixtures' / 'second_half_test_data.csv'
        sdf2 = SensorDataFile(file_id_hash=self.gui.sensor_controller.create_file_id(sdf2_path),
                              file_name=sdf2_path.name,
                              file_path=sdf2_path,
                              sensor=Sensor.get(name="test_sensor").id)
        sdf2.save()

        # See if the SDF is stored in the database and can be retrieved properly.
        sdf1 = self.gui.sensor_controller.get_or_create_sdf(sdf1_path)
        self.assertEqual(sdf1, SensorDataFile.get_by_id(sdf1.id), msg="The created sensor data file was not "
                                                                      "stored or retrieved from the database properly.")

        # Load the first sdf as if it was an ordinary file.
        self.gui.sensor_controller.open_file(sdf1_path)
        self.assertEqual(list(self.gui.sensor_controller.df.columns), ['Relative Time', 'absolute_datetime',
                                                                       'Ax', 'Ay', 'Az'],
                         msg="The columns of the sensor data file have not been loaded properly.")
        start_time_file1_utc = self.gui.sensor_controller.df['absolute_datetime'].iloc[0] \
            .to_pydatetime().astimezone(pytz.utc)

        # Load the second sensor data file.
        self.gui.sensor_controller.open_file(sdf2_path)
        self.assertEqual(list(self.gui.sensor_controller.df.columns), ['Relative Time', 'absolute_datetime',
                                                                       'Ax', 'Ay', 'Az'],
                         msg="The columns of the sensor data file have not been loaded properly.")

        start_time_file2_utc = self.gui.sensor_controller.df['absolute_datetime'].iloc[0] \
            .to_pydatetime().astimezone(pytz.utc)
        end_time_file2_utc = self.gui.sensor_controller.df['absolute_datetime'].iloc[-1] \
            .to_pydatetime().astimezone(pytz.utc)

        five_seconds = timedelta(seconds=5)
        one_hour = timedelta(hours=1)

        # Create three annotations for the first SDF.
        label1 = Label(start_time=start_time_file1_utc + 0 * five_seconds,
                       end_time=start_time_file1_utc + 1 * five_seconds,
                       label_type=test_activity1.id,
                       sensor_data_file=sdf1.id)
        label2 = Label(start_time=start_time_file1_utc + 2 * five_seconds,
                       end_time=start_time_file1_utc + 3 * five_seconds,
                       label_type=test_activity2.id,
                       sensor_data_file=sdf1.id)
        label3 = Label(start_time=start_time_file1_utc + 4 * five_seconds,
                       end_time=start_time_file1_utc + 5 * five_seconds,
                       label_type=test_activity3.id,
                       sensor_data_file=sdf1.id)

        label1.save()
        label2.save()
        label3.save()

        # Create three annotations for the second SDF.
        label4 = Label(start_time=start_time_file2_utc + 0 * five_seconds,
                       end_time=start_time_file2_utc + 1 * five_seconds,
                       label_type=test_activity4.id,
                       sensor_data_file=sdf2.id)
        label5 = Label(start_time=start_time_file2_utc + 2 * five_seconds,
                       end_time=start_time_file2_utc + 3 * five_seconds,
                       label_type=test_activity5.id,
                       sensor_data_file=sdf2.id)
        label6 = Label(start_time=start_time_file2_utc + 4 * five_seconds,
                       end_time=start_time_file2_utc + 5 * five_seconds,
                       label_type=test_activity6.id,
                       sensor_data_file=sdf2.id)

        label4.save()
        label5.save()
        label6.save()

        subject_mapping = SubjectMapping.create(subject=Subject.get(Subject.name == "test_subject"),
                                                sensor_id=Sensor.get(Sensor.name == "test_sensor"),
                                                start_datetime=start_time_file1_utc,
                                                end_datetime=end_time_file2_utc)
        subject_mapping.save()

        ########## testOpenVideo ##########

        video_path = self.cwd / 'fixtures' / 'Testbeeld.mp4'
        video = Video(file_name=video_path.name,
                      file_path=video_path,
                      datetime=datetime.now(),
                      camera=Camera.get(name="test_camera").id)
        video.save()
        self.gui.video_controller.open_file(video_path)

        ########## testExport ##########
        subject_ids = [test_subject.id]

        exported_file_path = Path(self.project_dir)/"unittest_export.csv"
        export_dialog = ExportProgressDialog(self.gui,
                                             subject_ids=subject_ids,
                                             start_dt=start_time_file1_utc - five_seconds,  # Extra margin
                                             end_dt=start_time_file1_utc + 24 * one_hour,  # Make sure it is in range.
                                             test_file_path=exported_file_path)
        export_dialog.exec()

        self.assertTrue(exported_file_path.is_file(), msg="Export file was not created.")

        ########## testCompareOutput ##########
        example_export_file = pd.read_csv(self.cwd/'fixtures'/'example_export_two_sdfs_one_subject.csv')
        unittest_export_file = pd.read_csv(exported_file_path)
        self.assertTrue(unittest_export_file.equals(example_export_file),
                        msg="The exported file does not match the example file.")

    def tearDown(self) -> None:
        print("tearDown()")
        self.gui.project_controller.close_db()  # Close the connection to the database to release the file.
        # shutil.rmtree(self.project_dir)  # Delete the test project folder and its contents. Comment out for debugging.
        self.gui.app_controller.app_config_file.unlink()  # Delete the app config file.
