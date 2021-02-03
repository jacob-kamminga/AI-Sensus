import csv
import datetime as dt
import gc
import math
import os
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pytz
from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate, QTime, QDir, Qt
from PyQt5.QtWidgets import QFileDialog, QDialog, QPushButton, QMessageBox, QShortcut, QSizePolicy, QSizeGrip
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.dates import date2num
from pandas.core.dtypes.common import is_numeric_dtype

from constants import COL_ABSOLUTE_DATETIME
from data_import.sensor_data import SensorData
from database.export_manager import ExportManager
from database.label_type_manager import LabelTypeManager
from database.sensor_data_file_manager import SensorDataFileManager
from database.sensor_manager import SensorManager
from database.subject_manager import SubjectManager
from database.sensor_usage_manager import SensorUsageManager
from gui.designer.visual_analysis import Ui_Dialog
from gui.dialogs.project_settings import ProjectSettingsDialog
from parse_function.parse_exception import ParseException
import parse_function.custom_function_parser as parser

COL_LABEL = 'Label'
COL_TIME = 'Time'
COL_TIMESTAMP = 'Timestamp'


class VisualAnalysisDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, settings: ProjectSettingsDialog, datetime: dt.datetime = None):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Visual Inspection")
        self.settings = settings
        self.export_manager = ExportManager(settings)
        self.subject_manager = SubjectManager(settings)
        self.map_manager = SensorUsageManager(settings)
        self.sensor_data_file_manager = SensorDataFileManager(settings)
        self.sensor_manager = SensorManager(settings)
        self.label_type_manager = LabelTypeManager(settings)
        self.settings_dict = settings.settings_dict

        # Create scrolling key shortcuts
        self.shortcut_plus_10s = QShortcut(Qt.Key_Right, self)
        self.shortcut_minus_10s = QShortcut(Qt.Key_Left, self)
        self.shortcut_plus_10s.activated.connect(self.fast_forward_10s)
        self.shortcut_minus_10s.activated.connect(self.rewind_10s)

        self.subject_dict = self.subject_manager.get_all_subjects_name_id()
        self.activity_dict = self.label_type_manager.get_all_labels_activity_id()

        self.listWidget_subjects.addItems(self.subject_dict.keys())
        self.listWidget_activities.addItems(self.activity_dict.keys())
        self.init_date_time_widgets(datetime)

        self.pushButton_plot_data.clicked.connect(self.collect_and_plot_data)
        self.doubleSpinBox_plot_width.valueChanged.connect(self.change_plot_width)
        self.doubleSpinBox_plot_height.valueChanged.connect(self.change_plot_height)
        self.comboBox_functions.activated.connect(self.change_function)
        # Connect the usage of the slider to its appropriate helper function
        self.horizontalSlider_time.sliderMoved.connect(self.update_plot_axis)

        self.figure = matplotlib.pyplot.figure(constrained_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        # self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.canvas.setWindowFlags(Qt.SubWindow)
        # gripper = QSizeGrip(self.canvas)

        # self.canvas.resize(self.canvas.width(), self.canvas.height()*2)
        # self.verticalLayout_plot.addWidget(gripper, 0, Qt.AlignRight | Qt.AlignBottom)
        self.verticalLayout_plot.addWidget(self.canvas, 2)
        # self.verticalLayout_plot.addWidget(gripper)
        # self.verticalLayout_plot.setSizeConstraint()

        self.df = None
        self.data_plot = None
        self.current_function = None
        self.last_used_function = None
        self.label_color = None
        self.plot_width = 30
        self.plot_height_factor = 1
        self.x_min = self.y_min = 0
        self.x_max = self.y_max = self.sample_rate = 1

        self.canvas.mpl_connect('button_press_event', self.onclick)
        # self.canvas.mpl_connect('button_release_event', self.onrelease)

    def onclick(self, event):
        if self.df is None:
            return

        if event.button == MouseButton.LEFT:
            label_dt = self.df[COL_ABSOLUTE_DATETIME][round(event.xdata)]
            QMessageBox.information(self, "Date time", "Date and Time of this segment are: " + str(label_dt))

    def draw_graph(self, plot_nr_rows=1, plot_index=1):
        # Reset the figure and add a new subplot to it
        if plot_nr_rows > 1 or plot_index > 1:
            QMessageBox.information(self, "Notice", "Multiplots")
        self.figure.clear()
        self.horizontalSlider_time.setValue(0)
        plot_nr_cols = 1
        self.data_plot = self.figure.add_subplot(plot_nr_rows, plot_nr_cols, plot_index)

        if self.df is None or self.df.empty:
            QMessageBox.information(self, "No data found", "Please select different label or period")
            return

        # Clear the plot
        self.data_plot.clear()

        # Get the boundaries of the plot axis
        # self.x_min_dt = self.df[COL_ABSOLUTE_DATETIME].min()
        # self.x_max_dt = self.df[COL_ABSOLUTE_DATETIME].max()
        # self.x_min = date2num(self.x_min_dt)
        # self.x_max = date2num(self.x_max_dt)

        self.x_min = self.df.index.min()
        self.x_max = self.df.index.max()
        if self.x_min == self.x_max:
            self.x_max = self.x_min + 1

        self.sample_rate = round(
            10 ** 6 / (self.df[COL_ABSOLUTE_DATETIME][self.x_min + 1] - self.df[COL_ABSOLUTE_DATETIME][
                self.x_min]).microseconds)

        # Remove outliers before assessing y_min and y_max value for plot
        self.y_min = self.df[self.current_function].quantile(.0001)
        self.y_max = self.df[self.current_function].quantile(.9999)
        if self.y_min == self.y_max:
            self.y_max = self.y_min + 1

        # self.data_plot.set_xticklabels(self.df[COL_ABSOLUTE_DATETIME], rotation=45, minor=True)

        if self.label_color is not None:
            plot_color = self.label_color
        else:
            plot_color = 'black'

        # Plot the graph
        self.data_plot.plot(
            # self.df[COL_ABSOLUTE_DATETIME],
            self.df.index,
            self.df[self.current_function],
            ',-',
            linewidth=1,
            color=plot_color
        )

        # # Draw a red vertical line in the middle of the plot
        # self.vertical_line = self.data_plot.axvline(x=0)
        # self.vertical_line.set_color('red')

        x_window_start = self.x_min - ((self.plot_width * self.sample_rate) / 2)
        # if x_window_start < 0: x_window_start = 0
        x_window_end = self.x_min + ((self.plot_width * self.sample_rate) / 2)

        # Set the axis of the data plot
        self.data_plot.axis([
            x_window_start,
            x_window_end,
            self.y_min - ((self.plot_height_factor - 1) * self.y_min),
            self.y_max + ((self.plot_height_factor - 1) * self.y_max)
        ])

        # Draw the graph, set the value of the offset spinbox in the GUI to the correct value
        # self.verticalLayout_plot..setHeight.resize(self.canvas.width(), self.canvas.height())
        # self.canvas.resize(self.canvas.width(), self.data_plot.height() * 0.8)
        # self.figure.set_constrained_layout(True)
        self.canvas.draw()

    def init_functions(self):
        # Add every column in the DataFrame to the possible Data Series that can be plotted, except for time,
        # and plot the first one

        if self.df is None:
            return
        self.comboBox_functions.clear()

        # Retrieve the formulas that are associated with the project, and store them in the dictionary
        stored_formulas = self.settings.get_setting('formulas')
        for formula_name in stored_formulas:
            try:
                self.add_column_from_func(formula_name, stored_formulas[formula_name])
                self.comboBox_functions.addItem(formula_name)
            except Exception as e:
                print(e)

        data_cols = self.df.columns.tolist()
        for col in data_cols:
            if col != COL_LABEL and col != COL_ABSOLUTE_DATETIME and col != COL_TIME and col != COL_TIMESTAMP:
                self.comboBox_functions.addItem(col)

        if self.last_used_function:
            self.current_function = self.last_used_function
        else:
            self.set_current_function(self.comboBox_functions.currentText())

    def add_column_from_func(self, name: str, func: str):
        """
        Constructs a new column in the data frame using a given function.

        :param name: The name of the new column
        :param func: The function to calculate the values of the new column as a string
        """
        # Pass parse exception on
        try:
            # Parses a function into a python readable expression
            parsed_expr = parser.parse(func)

            # Apply parsed expression to data to create new column
            self.df.eval(name + " = " + parsed_expr, inplace=True)
        except ParseException:
            # Pass ParseException
            raise

    def change_function(self):
        """
        If the user changes the variable on the y-axis, this function changes the label if necessary and redraws the
        plot.
        """
        new_function = self.comboBox_functions.currentText()
        if self.set_current_function(new_function):
            self.last_used_function = new_function
            self.draw_graph()

    def set_current_function(self, new_plot):
        if new_plot == '':
            return False
        # test if this column has numeric values
        if is_numeric_dtype(self.df[new_plot]):
            self.current_function = new_plot
            return True
        else:
            # self.current_plot = None
            return False

    def change_plot_width(self, value):  # TODO: An error occurs where there is an infinite loop of change_plot_width
        # self.settings.set_setting('plot_width', value)
        self.plot_width = value

        if self.df is not None:
            self.update_plot_axis()

    def change_plot_height(self, value):
        # self.settings.set_setting('plot_height_factor', value)
        self.plot_height_factor = value
        if self.df is not None:
            self.update_plot_axis()

    def update_plot_axis(self):

        # if self.x_min_dt is None:
        #     return
        # position_dt = self.x_min_dt + dt.timedelta(
        #     seconds=self.horizontalSlider_time.value())
        # new_position_dt = position_dt if position == -1.0 else position
        # plot_width_delta = dt.timedelta(seconds=(self.plot_width / 2))
        #
        # self.x_min = date2num(new_position_dt - plot_width_delta)
        # self.x_max = date2num(new_position_dt + plot_width_delta)

        if self.x_min is None or self.data_plot is None:
            return
        position = self.x_min + ((self.horizontalSlider_time.value() / 100) * self.x_max)
        plot_width_delta = round((self.plot_width * self.sample_rate) / 2)
        x_window_start = position - plot_width_delta
        x_window_end = position + plot_width_delta

        self.data_plot.set_xlim(x_window_start, x_window_end)
        self.data_plot.set_ylim(
            self.y_min - ((self.plot_height_factor - 1) * abs(self.y_min)),
            self.y_max + ((self.plot_height_factor - 1) * self.y_max))

        # self.vertical_line.set_xdata((self.x_min + self.x_max) / 2)
        self.canvas.draw()

    def init_date_time_widgets(self, datetime):

        if datetime is not None:
            self.dateEdit_start.setDate(datetime.date())
            self.dateEdit_end.setDate(datetime.date())
            self.timeEdit_start.setTime(datetime.time())
            self.timeEdit_end.setTime((datetime + dt.timedelta(hours=1)).time())
        else:
            self.dateEdit_start.setDate(QDate.currentDate().addDays(-1))
            self.dateEdit_end.setDate(QDate.currentDate())
            self.timeEdit_start.setTime(QTime.currentTime())
            self.timeEdit_end.setTime(QTime.currentTime())

    def get_sensor_ids(self, subject_id: int, start_dt: dt.datetime, end_dt: dt.datetime) -> [int]:
        return self.map_manager.get_sensor_ids_by_dates(subject_id, start_dt, end_dt)

    def get_sensor_data_file_ids(self, sensor_id: int, start_dt: dt.datetime, end_dt: dt.datetime) -> [int]:
        return self.sensor_data_file_manager.get_ids_by_sensor_and_dates(sensor_id,
                                                                         start_dt.astimezone(pytz.utc).replace(
                                                                             tzinfo=None),
                                                                         end_dt.astimezone(pytz.utc).replace(
                                                                             tzinfo=None)
                                                                         )

    def get_labels(self, sensor_data_file_id: int, start_dt: dt.datetime, end_dt: dt.datetime):
        labels = self.export_manager.get_labels_by_dates(sensor_data_file_id,
                                                         start_dt,
                                                         end_dt)
        return [{"start": label["start_time"],
                 "end": label["end_time"],
                 "activity": label["activity"]} for label in labels]

    def get_sensor_data(self, sensor_data_file_id: int) -> SensorData:
        file_path = self.get_file_path(sensor_data_file_id)
        model_id = self.sensor_data_file_manager.get_sensor_model_by_id(sensor_data_file_id)
        sensor_id = self.sensor_data_file_manager.get_sensor_by_id(sensor_data_file_id)

        if model_id >= 0 and sensor_id >= 0:
            sensor_timezone = pytz.timezone(self.sensor_manager.get_timezone_by_id(sensor_id))
            sensor_data = SensorData(Path(file_path), self.settings, model_id)
            sensor_data.metadata.sensor_timezone = sensor_timezone
            # Parse the utc datetime of the sensor data
            sensor_data.metadata.parse_datetime()
            sensor_data.parse()
        # Sensor model unknown
        else:
            sensor_data = None

        return sensor_data

    def get_file_path(self, sensor_data_file_id: int) -> str:
        """
        Check whether the file paths in the database are still valid and update if necessary.

        :param sensor_data_file_id: The list of file names
        """
        file_path = self.sensor_data_file_manager.get_file_path_by_id(sensor_data_file_id)

        # Check whether the file path is still valid
        if os.path.isfile(file_path):
            return file_path
        else:
            # Invalid:
            # Prompt the user for the correct file path
            file_name = self.sensor_data_file_manager.get_file_name_by_id(sensor_data_file_id)
            new_file_path = self.prompt_file_location(file_name, file_path)

            # Update path in database
            self.sensor_data_file_manager.update_file_path(file_name, new_file_path)

            return new_file_path

    def prompt_file_location(self, file_name: str, old_path: str) -> str:
        """
        Open a QFileDialog in which the user can select a new file path

        :param file_name: The file name
        :param old_path: The old (invalid) file path
        :return: The new (valid) file path
        """
        # Split path to obtain the base path
        base_path = old_path.rsplit('/', 1)[0]

        if not os.path.isdir(base_path):
            base_path = QDir.homePath()

        # Open QFileDialog
        dialog = QFileDialog()
        dialog.setNameFilter(file_name)
        new_path, _ = dialog.getOpenFileName(self, "Cannot find: " + old_path, base_path, filter="csv (*.csv)")

        return new_path

    def get_start_datetime(self) -> dt.datetime:
        """

        :return: Start time localized to project timezone
        """
        start_dt = self.dateEdit_start.dateTime()
        start_dt.setTime(self.timeEdit_start.time())
        start_dt = start_dt.toPyDateTime()
        # return  start_dt
        if not start_dt.tzinfo:
            return pytz.timezone(self.settings.get_setting('timezone')).localize(start_dt)
        else:
            return start_dt

    def get_end_datetime(self) -> dt.datetime:
        """

        :return: End time localized to project timezone
        """
        end_dt = self.dateEdit_end.dateTime()
        end_dt.setTime(self.timeEdit_end.time())
        end_dt = end_dt.toPyDateTime()
        # return end_dt
        if not end_dt.tzinfo:
            return pytz.timezone(self.settings.get_setting('timezone')).localize(end_dt)
        else:
            return end_dt

    def get_subject_ids(self) -> [int]:
        return [self.subject_dict.get(item.text()) for item in self.listWidget_subjects.selectedItems()]

    def get_activity_ids(self) -> [int]:
        return [self.activity_dict.get(item.text()) for item in self.listWidget_activities.selectedItems()]

    def get_label_types(self):
        return [item.text() for item in self.listWidget_activities.selectedItems()]

    def collect_and_plot_data(self):

        # if self.current_function is None:
        #     QMessageBox.warning(self, "No function selected", "Please select the function to plot")
        #     return
        self.label_info_text.setText("Collecting data, this may take a few minutes...")
        self.label_info_text.repaint()
        subject_ids: [int] = self.get_subject_ids()
        # activity_ids: [int] = self.get_activity_ids()
        label_types = self.get_label_types()
        if self.groupBox_select_timeperiod.isChecked():
            start_dt: dt.datetime = self.get_start_datetime()
            end_dt: dt.datetime = self.get_end_datetime()
        else:
            start_dt = dt.datetime(1, 1, 1, 1, 1, 1, 1, tzinfo=pytz.utc)
            end_dt = dt.datetime(3000, 1, 1, 1, 1, 1, 1, tzinfo=pytz.utc)

        # Destroy old data and free up memory
        if hasattr(self, 'df'):
            del self.df
        gc.collect()
        # Set index counter for concatenated data segments
        idx = 0
        for subject_id in subject_ids:
            for label_type in label_types:
                subject_name = self.subject_manager.get_name_by_id(subject_id)
                sensor_ids = self.get_sensor_ids(subject_id, start_dt, end_dt)

                for plot_index, sensor_id in enumerate(sensor_ids):
                    self.df: pd.DataFrame = pd.DataFrame()
                    sensor_data_file_ids = self.get_sensor_data_file_ids(sensor_id, start_dt, end_dt)

                    for file_id in sensor_data_file_ids:
                        try:
                            labels = self.get_labels(file_id, start_dt, end_dt)
                            sensor_data = self.get_sensor_data(file_id)

                            if sensor_data is None:
                                raise Exception('Sensor data not found')

                            if not sensor_data.add_abs_datetime_column():
                                return

                            if self.groupBox_select_timeperiod.isChecked():
                                # TODO verify localization of start and end_dt
                                sensor_data.filter_between_dates(
                                    start_dt.astimezone(pytz.utc),
                                    end_dt.astimezone(pytz.utc)  # sensor_data.metadata.sensor_timezone
                                )

                            sensor_data.add_labels(labels)
                            block = sensor_data.get_data(label_type)
                            if len(block) == 0:
                                continue
                            new_idx = idx + len(block)
                            block.index = np.arange(idx, new_idx)
                            idx = new_idx + 1
                            self.df = self.df.append(block)
                            # plt.plot(self.df.Az)
                            # plt.show()
                            del sensor_data, block
                            gc.collect()
                        except MemoryError as e:
                            QMessageBox.critical(self, "Memory error", "Please try again with a smaller time period")
                            self.label_info_text.clear()
                            return

                    # Fill functions combobox for this data
                    self.init_functions()
                    # Create new index to avoid gaps in plotting
                    # self.df = self.df.reset_index(drop=True, inplace=True)
                    # self.df.reset_index(drop=True, inplace=True)
                    # self.df.index = np.arange(0, len(self.df)+1)
                    # self.df = self.df.reindex(drop=True)
                    # Get color of this label
                    self.label_color = self.label_type_manager.get_color_by_label_type(label_type)
                    # Plot the data for each sensor ID in a new subplot
                    self.draw_graph(len(sensor_ids), plot_index + 1)
                    self.label_info_text.clear()

        if not hasattr(self, 'df') or self.df is None or self.df.empty:
            QMessageBox.information(self, "No data found", "Please select different label or period")
            self.label_info_text.clear()
            return

    def fast_forward_10s(self):
        """
        Sets the position of the data 10 seconds forward
        """
        if self.df is not None:
            duration = self.x_max / self.sample_rate
            position_delta = math.ceil((10 / duration) * 100)
            self.horizontalSlider_time.setSliderPosition(self.horizontalSlider_time.value() + position_delta)
            self.update_plot_axis()

    def rewind_10s(self):
        """
        Sets the position of the data 10 seconds backward
        """
        if self.df is not None:
            duration = self.x_max / self.sample_rate
            position_delta = math.ceil((10 / duration) * 100)
            new_position = self.horizontalSlider_time.value() - position_delta
            if new_position < 0: new_position = 0
            self.horizontalSlider_time.setSliderPosition(new_position)
            self.update_plot_axis()