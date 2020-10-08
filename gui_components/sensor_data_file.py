import datetime as dt
import ntpath
import os
from pathlib import Path
from typing import Optional

import pandas as pd
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileDialog

from constants import PREVIOUS_SENSOR_DATA_FILE
from data_import.sensor_data import SensorData
from database.label_manager import LabelManager
from database.offset_manager import OffsetManager
from database.sensor_manager import SensorManager
from database.sensor_data_file_manager import SensorDataFileManager
from database.sensor_model_manager import SensorModelManager
from gui.dialogs.sensor_model import SensorModelDialog
from project_settings import ProjectSettingsDialog


class SensorDataFile:
    """
    Contains methods for manipulating sensor data.
    """

    def __init__(self, gui):
        self.gui = gui
        self.settings: ProjectSettingsDialog = gui.settings
        self.file_path: Optional[Path] = None

        self.sensor_manager = SensorManager(self.settings)
        self.sensor_model_manager = SensorModelManager(self.settings)
        self.sensor_data_file_manager = SensorDataFileManager(self.settings)
        self.offset_manager = OffsetManager(self.settings)
        self.label_manager = LabelManager(self.settings)

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
        self.model_id: Optional[int] = None
        """ The model ID. """

    def open_previous_file(self):
        previous_path = self.settings.get_setting(PREVIOUS_SENSOR_DATA_FILE)

        if previous_path is not None:
            previous_path = Path(previous_path)
            if previous_path.is_file():
                self.file_path = previous_path
                self.open_file()
                if hasattr(self.gui, 'video'):
                    self.gui.video.set_position(0)

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
        dialog.show()

        self.model_id = dialog.selected_model_id

        if self.model_id is None:
            # TODO: Show warning to user
            pass

    def open_file(self):
        """
        Opens the file specified by self.file_path and sets the sensor data.
        """
        if self.file_path is not None and self.file_path.is_file():
            self.settings.set_setting(PREVIOUS_SENSOR_DATA_FILE, self.file_path.as_posix())
            file_name = ntpath.basename(self.file_path.as_posix())

            # Reset the dictionary that maps function names to functions
            self.gui.plot.formula_dict = dict()

            self.model_id = self.sensor_data_file_manager.get_sensor_model_by_file_name(file_name)

            # If sensor model unknown, prompt user
            if self.model_id == -1:
                self.open_sensor_model_dialog()

            if self.model_id != -1:
                # Retrieve the SensorData object that parses the sensor data file
                self.sensor_data = SensorData(self.file_path, self.settings, self.model_id)
                sensor_name = self.sensor_data.metadata['sn']

                self.sensor_id = self.sensor_manager.get_id_by_name(sensor_name)

                if self.sensor_id == -1:
                    self.sensor_id = self.sensor_manager.insert_sensor(sensor_name, self.model_id)

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
                self.id_ = self.sensor_data_file_manager.get_id_by_file_name(file_name)

                if self.id_ == -1:
                    # File not found in database -> add it
                    self.id_ = self.sensor_data_file_manager.add_file(
                        file_name,
                        self.file_path.as_posix(),
                        self.sensor_id,
                        self.datetime
                    )

                if self.sensor_data_file_manager.get_file_path_by_id(self.id_) != self.file_path:
                    self.sensor_data_file_manager.update_file_path(file_name, self.file_path.as_posix())

                self.init_functions()
                self.draw_graph()
                # self.update_camera_text()
                self.gui.update_camera_sensor_offset()
                self.gui.video.sync_with_sensor_data()

    def init_functions(self):
        # Add every column in the DataFrame to the possible Data Series that can be plotted, except for time,
        # and plot the first one
        self.gui.comboBox_functions.clear()

        for column in self.df.columns:
            self.gui.comboBox_functions.addItem(column)

        # self.gui.comboBox_functions.removeItem(0)
        if self.settings.get_setting("current_plot"):
            self.gui.plot.current_plot = self.settings.get_setting("current_plot")
            self.gui.comboBox_functions.setCurrentText(self.gui.plot.current_plot)
        else:
            self.gui.plot.current_plot = self.gui.comboBox_functions.currentText()

    def draw_graph(self):
        # Reset the figure and add a new subplot to it
        self.gui.figure.clear()
        self.gui.plot.data_plot = self.gui.figure.add_subplot(1, 1, 1)

        # Determine the length of the y-axis and plot the graph with the specified width
        if self.df[self.gui.plot.current_plot].min() == self.df[self.gui.plot.current_plot].max():
            self.gui.plot.y_min = self.df[self.gui.plot.current_plot].min()
            self.gui.plot.y_max = self.df[self.gui.plot.current_plot].max() + 1
        else:
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

    def update_camera_text(self):
        camera_name = self.gui.label_camera_name_value.text()

        if camera_name != "":
            camera_id = self.gui.video.camera_manager.get_camera_id(camera_name)

            self.gui.doubleSpinBox_video_offset.setValue(
                self.offset_manager.get_offset(
                    camera_id,
                    self.sensor_id,
                    self.datetime.date()))
