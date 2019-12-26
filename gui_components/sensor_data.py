import os

from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileDialog

from data_import import sensor_data


class SensorData:
    """
    Contains methods for manipulating sensor data.
    """

    def __init__(self, gui):
        """"
        Attributes:
            gui: The GUI instance
            settings: The Settings instance
            file_path: The file path of the sensor data
            data: The SensorData instance
            df: The pandas DataFrame

        :param gui: The GUI instance
        :param settings: The Settings instance
        """
        self.gui = gui
        self.settings = gui.settings
        self.file_path = None

        self.sensor_id = None
        self.data = None
        self.df = None
        self.datetime = None

    def open_previous_file(self):
        previous_path = self.settings.get_setting('last_datafile')

        if previous_path is not None:
            if os.path.isfile(previous_path):
                self.file_path = previous_path
                self.open_sensor_data()

    def prompt_sensor_data(self):
        path = "" if self.settings.get_setting('last_datafile') is None else self.settings.get_setting("last_datafile")

        if not os.path.isfile(path):
            path = path.rsplit('/', 1)[0]
            if not os.path.isdir(path):
                path = QDir.homePath()

        # Get the user input from a dialog window
        self.file_path, _ = QFileDialog.getOpenFileName(self.gui, "Open Sensor Data", path)

        self.open_sensor_data()

    def open_sensor_data(self):
        """
        A function that allows a user to open a CSV file in the plotting canvas via the menu bar.
        :return:
        """
        if self.file_path is not None:
            self.settings.set_setting('last_datafile', self.file_path)

            # Reset the dictionary that maps function names to functions
            self.gui.plot.formula_dict = dict()

            # Retrieve the SensorData object that parses the sensor data file
            self.data = sensor_data.SensorData(self.file_path, self.settings.settings_dict)
            self.sensor_id = self.data.metadata['sn']

            # Retrieve the formulas that are associated with this sensor data file, and store them in the dictionary
            stored_formulas = self.settings.get_setting("formulas")

            for formula_name in stored_formulas:
                try:
                    self.data.add_column_from_func(formula_name, stored_formulas[formula_name])
                    self.gui.plot.formula_dict[formula_name] = stored_formulas[formula_name]
                except Exception as e:
                    print(e)

            # Retrieve the DataFrame with all the raw sensor data
            self.df = self.data.get_data()

            # Add every column in the DataFrame to the possible Data Series that can be plotted, except for time,
            # and plot the first one
            self.gui.comboBox_functions.clear()

            for column in self.df.columns:
                self.gui.comboBox_functions.addItem(column)

            self.gui.comboBox_functions.removeItem(0)
            self.gui.plot.current_plot = self.gui.comboBox_functions.currentText()

            # Save the starting time of the sensordata in a DateTime object
            self.datetime = self.data.metadata['datetime']

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

            if self.gui.comboBox_camera_ids.currentText():
                self.gui.doubleSpinBox_video_offset.setValue(
                    self.gui.camera.offset_manager.get_offset(self.gui.comboBox_camera_ids.currentText(),
                                                              self.data.metadata['sn'],
                                                              self.data.metadata['date']))

            # Check if the sensor data file is already in the label database, if not add it
            file_name = os.path.basename(self.file_path)
            if not self.gui.plot.label_storage.file_is_added(file_name):
                self.gui.plot.label_storage.add_file(file_name, self.data.metadata['sn'], self.datetime)

            self.gui.video.sync_with_sensor_data()
