import datetime as dt
import hashlib
import ntpath
import os
from pathlib import Path
from typing import Optional

# import PyQt5
import pandas as pd
import pytz
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from peewee import DoesNotExist

from constants import PREVIOUS_SENSOR_DATA_FILE
from data_import.sensor_data import SensorData
from database.peewee.models import SensorDataFile, SensorModel, Sensor, Camera, Offset
from gui.dialogs.edit_sensor_dialog import EditSensorDialog
from gui.dialogs.project_settings_dialog import ProjectSettingsDialog
from gui.dialogs.sensor_model_dialog import SensorModelDialog


# from PyQt5.QtGui import QCursor
# from PyQt5 import QtGui


class SensorController:
    """
    Contains methods for manipulating sensor data.
    """

    def __init__(self, gui):
        self.gui = gui
        self.settings: ProjectSettingsDialog = gui.settings
        self.file_path: Optional[Path] = None

        self.file_name = None

        self.file_id_hash = None
        """" The hashed ID, used to recognize the file independent from location on disk """
        self.id_: Optional[int] = None
        """ The database ID of the sensor data file. """
        self.sensor_id: Optional[int] = None
        """ The database ID of the sensor. """
        self.sensor_name: Optional[str] = None
        """ The name of the sensor associated with this sensor datafile"""
        self.sensor_data: Optional[SensorData] = None
        """ The data_import.SensorData object. """
        self.df: Optional[pd.DataFrame] = None
        """ The pandas DataFrame. """
        self.utc_dt: Optional[dt.datetime] = None
        """ The datetime of the sensor data. """
        self.model_id: Optional[int] = None
        """ The model ID. """
        # TODO: Use the model instances instead of storing the separate IDs defined above
        self.sensor_model = None
        self.sensor_data_file = None

    def open_previous_file(self):
        previous_path = self.settings.get_setting(PREVIOUS_SENSOR_DATA_FILE)

        if previous_path:
            previous_path = Path(previous_path)

            if previous_path.is_file():
                self.file_path = previous_path
                self.open_file()

                if hasattr(self.gui, 'video') and self.gui.video_controller.project_dt is not None:
                    self.gui.video_controller.set_position(0)

    def prompt_file(self):
        """
        Opens a file dialog that lets the user select a file.
        """
        path = self.settings.get_setting(PREVIOUS_SENSOR_DATA_FILE)

        if path is None:
            path = ""
        elif not os.path.isfile(path):
            # Split path to obtain the base path
            path = path.rsplit('/', 1)[0]

            if not os.path.isdir(path):
                path = QDir.homePath()

        # Get the user input from a dialog window
        self.file_path, _ = QFileDialog.getOpenFileName(self.gui, "Open Sensor Data", path, filter="csv (*.csv)")
        self.file_path = Path(self.file_path)

        self.open_file()

    def open_sensor_model_dialog(self):
        dialog = SensorModelDialog(self.settings)
        dialog.exec()
        # dialog.show()

        return dialog.selected_model_id

    def open_file(self):
        """
        Opens the file specified by self.file_path and sets the sensor data.
        """
        if self.file_path and self.file_path.is_file():
            # Store the selected file path in the configuration
            self.settings.set_setting(PREVIOUS_SENSOR_DATA_FILE, self.file_path.as_posix())

            self.file_name = ntpath.basename(self.file_path.as_posix())
            self.file_id_hash = self.create_file_id(self.file_path)

            # Get or create the sensor data file model instance
            self.sensor_data_file = SensorDataFile.get_or_create(
                file_id_hash=self.file_id_hash,
                defaults={
                    'file_name': self.file_name,
                    'file_path': self.file_path,
                    'sensor': -1,
                }
            )[0]

            # Reset the dictionary that maps function names to functions
            self.gui.plot_controller.formula_dict = dict()

            # Retrieve the sensor model ID from the database
            try:
                sensor_model_id = (SensorModel
                                   .select(SensorModel.id)
                                   .join(Sensor)
                                   .where(Sensor.id == self.sensor_data_file.sensor)
                                   .get())
            except DoesNotExist:
                sensor_model_id = None

            # If not found, open a dialog where the user can select the sensor model
            while sensor_model_id is None:
                sensor_model_id = self.open_sensor_model_dialog()

            # Retrieve the SensorData object that parses the sensor data file
            self.sensor_data = SensorData(self.file_path, self.settings, sensor_model_id)
            # Try to load sensor name from either metadata or DB
            if self.sensor_data.metadata.sensor_name:
                sensor_name = self.sensor_data.metadata.sensor_name
            else:
                # Check if sensor data has been loaded before and name is known in DB
                try:
                    sensor_name = Sensor.get_by_id(self.sensor_data_file.sensor).name
                except DoesNotExist:
                    sensor_name = None

            # When sensor ID (name) cannot be parsed it has to be manually linked to datafile by user
            while sensor_name is None:
                sensor_name = self.gui.open_select_sensor_dialog(self.model_id)
                # Verify that user indeed selected a sensor ID
                if sensor_name is None:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Warning")
                    msg.setText("A sensor ID must be selected")
                    msg.setInformativeText("The selected sensor model states that sensor identifier (ID) cannot "
                                           "be parsed from sensor datafile. Please select sensor ID manually.")
                    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                    response = msg.exec()
                    if response == QMessageBox.Cancel:
                        return

            sensor = Sensor.get_or_create(name=sensor_name, defaults={'model': sensor_model_id})[0]

            while sensor.timezone is None:
                # Prompt user for timezone of sensor
                dialog = EditSensorDialog(sensor)
                dialog.exec()

            self.sensor_data.metadata.sensor_timezone = pytz.timezone(sensor.timezone)

            self.sensor_data_file.sensor = sensor

            # Parse the sensor data from the file
            self.sensor_data.parse()

            # Retrieve the formulas that are associated with this sensor data file, and store them in the dictionary
            stored_formulas = self.settings.get_setting('formulas')

            for formula_name in stored_formulas:
                try:
                    self.sensor_data.add_column_from_func(formula_name, stored_formulas[formula_name])
                    self.gui.plot_controller.formula_dict[formula_name] = stored_formulas[formula_name]
                except Exception as e:
                    print(e)

            # Parse the utc datetime of the sensor data from metadata when possible
            # self.sensor_data.metadata.parse_datetime()
            # self.gui.setCursor(.WaitCursor)
            # Add absolute time column to dataframe
            self.sensor_data.add_abs_datetime_column()
            # Save the starting time of the sensor data in a DateTime object
            self.sensor_data_file.datetime = self.sensor_data.metadata.utc_dt

            # Retrieve the DataFrame with all the raw sensor data
            self.df = self.sensor_data.get_data()

            # Update file path in DB if it has changed
            if self.sensor_data_file.file_path != self.file_path.as_posix():
                self.sensor_data_file.file_path = self.file_path.as_posix()
                self.sensor_data_file.save()

            # self.gui.setCursor(QtGui.QCursor(0))
            self.init_functions()
            self.draw_graph()
            # self.update_camera_text()
            try:
                self.gui.label_sensor_data_filename.setText(
                    self.file_path.parts[-3] + "/" + self.file_path.parts[-2] + "/" + self.file_path.parts[-1]
                )
            except:
                pass
            self.gui.update_camera_sensor_offset()
            self.gui.video_controller.sync_with_sensor_data()

    def init_functions(self):
        # Add every column in the DataFrame to the possible Data Series that can be plotted, except for time,
        # and plot the first one
        self.gui.comboBox_functions.clear()

        data_cols = self.df.columns.tolist()
        del data_cols[self.sensor_data.sensor_model.timestamp_column]

        for col in data_cols:
            self.gui.comboBox_functions.addItem(col)

        last_used_col = self.sensor_data_file.last_used_column

        if last_used_col:
            self.gui.plot_controller.current_plot = last_used_col
            self.gui.comboBox_functions.setCurrentText(last_used_col)

        self.gui.plot_controller.current_plot = self.gui.comboBox_functions.currentText()

    def save_last_used_column(self, col_name):
        self.sensor_data_file.last_used_column = col_name
        self.sensor_data_file.save()

    def draw_graph(self):
        # Reset the figure and add a new subplot to it
        self.gui.figure.clear()
        self.gui.plot_controller.data_plot = self.gui.figure.add_subplot(1, 1, 1)
        self.gui.plot_controller.draw_graph()

        x_window_start = self.gui.plot_controller.x_min - (self.gui.plot_controller.plot_width / 2)
        x_window_end = self.gui.plot_controller.x_min + (self.gui.plot_controller.plot_width / 2)

        if self.settings.get_setting("plot_height_factor") is None:
            self.gui.plot_controller.plot_height_factor = 1.0
            self.settings.set_setting("plot_height_factor", self.gui.plot_controller.plot_height_factor)

        # Set the axis of the data plot
        self.gui.plot_controller.data_plot.axis([
            x_window_start,
            x_window_end,
            self.gui.plot_controller.y_min - ((self.gui.plot_controller.plot_height_factor - 1) * self.gui.plot_controller.y_min),
            self.gui.plot_controller.y_max + ((self.gui.plot_controller.plot_height_factor - 1) * self.gui.plot_controller.y_max)
        ])

        # Start the timer that makes the graph scroll smoothly
        self.gui.timer.timeout.connect(self.gui.plot_controller.update_plot_axis)
        self.gui.timer.start(25)

        # Draw the graph, set the value of the offset spinbox in the GUI to the correct value
        self.gui.canvas.draw()

    def update_camera_text(self):
        camera_name = self.gui.label_camera_name_value.text()

        if camera_name:
            offset = (Offset
                      .select(Offset.offset)
                      .join(Camera, Sensor)
                      .where((Camera.name == camera_name) &
                             (Sensor.id == self.sensor_id) &
                             (Offset.added == self.utc_dt.date())))

            self.gui.doubleSpinBox_video_offset.setValue(offset)

    def update_sensor(self, sensor_id: int):
        if self.id_:
            sensor_data_file = SensorDataFile.get_by_id(self.id_)
            sensor_data_file.sensor = sensor_id
            sensor_data_file.save()

    def create_file_id(self, file_path, block_size=256):
        # Function that takes a file and returns the first 10 characters of a hash of
        # 10 times block size in the middle of the file
        # Input: File path as string
        # Output: Hash of 10 blocks of 128 bits of size as string plus file size as string
        file_size = os.path.getsize(file_path)
        start_index = int(file_size / 2)
        with open(file_path, 'r') as f:
            f.seek(start_index)
            n = 1
            md5 = hashlib.md5()
            while True:
                data = f.read(block_size)
                n += 1
                if (n == 10):
                    break
                md5.update(data.encode('utf-8'))
        return '{}{}'.format(md5.hexdigest()[0:9], str(file_size))
