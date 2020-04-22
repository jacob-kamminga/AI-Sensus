import datetime as dt
import ntpath
import os
from typing import Optional

import pandas as pd
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileDialog

from data_import.sensor_data import SensorData
from database.db_label import LabelManager
from database.db_offset import OffsetManager
from database.db_sensor import SensorManager
from database.db_sensor_data_file import SensorDataFileManager
from exceptions import SensorDoesNotExist, SensorDataFileDoesNotExist


class SensorDataFile:
    """
    Contains methods for manipulating sensor data.
    """

    def __init__(self, gui):
        self.gui = gui
        self.project_name = self.gui.project_dialog.project_name
        self.settings = gui.settings
        self.file_path = None

        self.sensor_manager = SensorManager(self.project_name)
        self.sensor_data_file_manager = SensorDataFileManager(self.project_name)
        self.offset_manager = OffsetManager(self.project_name)
        self.label_manager = LabelManager(self.project_name)

        self.id_: Optional[int] = None
        """ The database ID of the sensor data file. """
        self.sensor_id: Optional[int] = None
        """ The database ID of the sensor. """
        self.sensor_data: Optional[SensorData] = None
        """ The data_import.SensorData object. """
        self.df: Optional[pd.DataFrame] = None
        """ The pandas DataFrame. """
        self.datetime: Optional[dt.datetime] = None
        """ The datetime of the sensor data. """

    def open_previous_file(self):
        previous_path = self.settings.get_setting('last_datafile')

        if previous_path is not None:
            if os.path.isfile(previous_path):
                self.file_path = previous_path
                self.open_file()

    def prompt_file(self):
        """
        Opens a file dialog that lets the user select a file.
        """
        path = self.settings.get_setting('last_datafile')

        if path is None:
            path = ""
        elif not os.path.isfile(path):
            # Split path to obtain the base path
            path = path.rsplit('/', 1)[0]

            if not os.path.isdir(path):
                path = QDir.homePath()

        # Get the user input from a dialog window
        self.file_path, _ = QFileDialog.getOpenFileName(self.gui, "Open Sensor Data", path, filter="csv (*.csv)")

        self.open_file()

    def open_file(self):
        """
        Opens the file specified by self.file_path and sets the sensor data.
        """
        if self.file_path is not None and os.path.isfile(self.file_path):
            self.settings.set_setting('last_datafile', self.file_path)

            # Reset the dictionary that maps function names to functions
            self.gui.plot.formula_dict = dict()

            # Retrieve the SensorData object that parses the sensor data file
            self.sensor_data = SensorData(self.file_path, self.settings.settings_dict)
            sensor_name = self.sensor_data.metadata['sn']

            try:
                self.sensor_id = self.sensor_manager.get_id_by_name(sensor_name)
            except SensorDoesNotExist:
                self.sensor_id = self.sensor_manager.insert_sensor(sensor_name)

            # Retrieve the formulas that are associated with this sensor data file, and store them in the dictionary
            stored_formulas = self.settings.get_setting('formulas')

            for formula_name in stored_formulas:
                try:
                    self.sensor_data.add_column_from_func(formula_name, stored_formulas[formula_name])
                    self.gui.plot.formula_dict[formula_name] = stored_formulas[formula_name]
                except Exception as e:
                    print(e)

            # Retrieve the DataFrame with all the raw sensor data
            self.df = self.sensor_data.get_data()

            # Save the starting time of the sensor data in a DateTime object
            self.datetime = self.sensor_data.metadata['datetime']

            # Check if the sensor data file is already in the label database, if not add it
            file_name = ntpath.basename(self.file_path)

            try:
                self.id_ = self.sensor_data_file_manager.get_id_by_file_name(file_name)

                if self.sensor_data_file_manager.get_file_path_by_id(self.id_) != self.file_path:
                    self.sensor_data_file_manager.update_file_path(file_name, self.file_path)

            except SensorDataFileDoesNotExist:
                self.id_ = self.sensor_data_file_manager.add_file(file_name,
                                                                  self.file_path,
                                                                  self.sensor_id,
                                                                  self.datetime)

            # Add every column in the DataFrame to the possible Data Series that can be plotted, except for time,
            # and plot the first one
            self.gui.comboBox_functions.clear()

            for column in self.df.columns:
                self.gui.comboBox_functions.addItem(column)

            self.gui.comboBox_functions.removeItem(0)
            self.gui.plot.current_plot = self.gui.comboBox_functions.currentText()

            # Reset the figure and add a new subplot to it
            self.gui.figure.clear()
            self.gui.plot.data_plot = self.gui.figure.add_subplot(1, 1, 1)

            # Determine the length of the y-axis and plot the graph with the specified width
            self.gui.plot.y_min = self.df[self.gui.plot.current_plot].min()
            self.gui.plot.y_max = self.df[self.gui.plot.current_plot].max()

            self.gui.plot.draw_graph()

            x_window_start = self.gui.plot.x_min - (self.gui.plot.plot_width / 2)
            x_window_end = self.gui.plot.x_min + (self.gui.plot.plot_width / 2)

            if self.settings.get_setting("plot_height_factor") is None:
                self.gui.plot.plot_height_factor = 1.0
                self.settings.set_setting("plot_height_factor", self.gui.plot.plot_height_factor)

            # Set the axis of the data plot
            self.gui.plot.data_plot.axis([x_window_start,
                                          x_window_end,
                                          self.gui.plot.y_min,
                                          self.gui.plot.plot_height_factor * self.gui.plot.y_max])

            # Start the timer that makes the graph scroll smoothly
            self.gui.timer.timeout.connect(self.gui.plot.update_plot_axis)
            self.gui.timer.start(25)

            # Draw the graph, set the value of the offset spinbox in the GUI to the correct value
            self.gui.canvas.draw()

            camera_name = self.gui.label_camera_name_value.text()

            if camera_name != "":
                camera_id = self.gui.video.camera_manager.get_camera_id(camera_name)

                self.gui.doubleSpinBox_video_offset.setValue(
                    self.offset_manager.get_offset(
                        camera_id,
                        self.sensor_id,
                        self.datetime))

            self.gui.video.sync_with_sensor_data()
