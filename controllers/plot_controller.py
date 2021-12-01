import datetime as dt
from typing import Optional, List

import pytz
from PyQt5.QtWidgets import QMessageBox
from matplotlib.backend_bases import MouseButton
from matplotlib.dates import date2num, num2date
from pandas.core.dtypes.common import is_numeric_dtype
from peewee import DoesNotExist

from constants import ABSOLUTE_DATETIME
from database.models import LabelType, Label
from gui.dialogs.label_dialog import LabelDialog

LABEL_START_TIME_INDEX = 0
LABEL_END_TIME_INDEX = 1
LABEL_TYPE_INDEX = 2

KEY_ACTIVITY = "activity"
KEY_ID = "id"
KEY_COLOR = "color"

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
QDATETIME_FORMAT = "yyyy-MM-dd HH:mm:ss.zzz"


class PlotController:

    def __init__(self, gui):
        self.gui = gui
        self.project_controller = gui.project_controller
        self.sensor_controller = gui.sensor_controller
        self.project_timezone = pytz.timezone(self.project_controller.get_setting('timezone'))

        # self.reset()
        self.formulas = self.project_controller.get_setting('formulas')
        self.plot_width = self.project_controller.get_setting('plot_width')
        self.plot_height_factor = self.project_controller.get_setting('plot_height_factor')

        self.data_plot = None
        self.current_plot = None
        self.vertical_line = None

        self.highlights = dict()
        self.label_types = dict()

        self.x_min_dt: Optional[dt.datetime] = None
        self.x_max_dt: Optional[dt.datetime] = None
        self.x_min = None
        self.x_max = None

        self.y_min = None
        self.y_max = None

        self.on_click_datetime = None

        self.label_dialog: Optional[LabelDialog] = None

        # Initialize the boolean that keeps track if the user is labeling with the right-mouse button
        self.labeling_in_progress = False

    # def reset(self):
    #     """
    #     Part of init functionality is in reset_plot method, so that plot can be reset when changing project
    #     :return:
    #     """

    def new_plot(self, function_name, function_regex):
        """
        Adds a function to the DataFrame as new column.
        """
        # Add a column to the sensor data, based on the selected function
        self.sensor_controller.sensor_data.add_column_from_func(function_name, function_regex)

        # Get the dataframe
        self.sensor_controller.df = self.sensor_controller.sensor_data.get_data()

        self.formulas[function_name] = function_regex
        stored_formulas = self.project_controller.get_setting("formulas")
        stored_formulas[function_name] = function_regex
        self.project_controller.set_setting("formulas", stored_formulas)

    def change_plot(self, plot_name):
        """
        If the user changes the variable on the y-axis, this function changes the label if necessary and redraws the
        plot.
        """
        self.set_current_plot(plot_name)

        # Save the column in the database
        # TODO: When a plot is deleted, the new plot value is not saved to the database
        self.sensor_controller.save_last_used_column(plot_name)

        if plot_name in self.formulas:
            self.draw_graph()
            return self.formulas[plot_name]

        return None

    def set_current_plot(self, plot_name):
        # test if this column has numeric values
        if is_numeric_dtype(self.sensor_controller.df[plot_name]):
            self.current_plot = plot_name
            return True
        else:
            # self.current_plot = None
            return False

    def delete_formula(self, selected_plot: str):
        self.formulas.pop(selected_plot)
        self.project_controller.set_setting('formulas', self.formulas)
        self.change_plot(selected_plot)

    def change_plot_width(self, value):  # TODO: An error occurs where there is an infinite loop of change_plot_width
        self.project_controller.set_setting('plot_width', value)
        self.plot_width = value

        if self.sensor_controller.sensor_data is not None:
            self.update_plot_axis()

    def change_plot_height(self, value):
        self.project_controller.set_setting('plot_height_factor', value)
        self.plot_height_factor = value

    def update_plot_axis(self, position=-1.0):
        """
        Every time the timer calls this function, the axis of the graph is updated.
        """
        if self.x_min_dt is None:
            return
        position_dt = self.x_min_dt + dt.timedelta(
            seconds=self.gui.mediaPlayer.position() / 1000)  # TODO: Fix bug when starting new project
        new_position_dt = position_dt if position == -1.0 else position

        plot_width_delta = dt.timedelta(seconds=(self.plot_width / 2))
        video_offset_delta = dt.timedelta(seconds=self.gui.doubleSpinBox_video_offset.value())
        video_offset = dt.timedelta(seconds=0)

        if self.gui.video_controller.init_offset is not None:
            video_offset = self.gui.video_controller.init_offset

        x_min = date2num(new_position_dt - plot_width_delta - video_offset_delta - video_offset)
        x_max = date2num(new_position_dt + plot_width_delta - video_offset_delta - video_offset)

        self.data_plot.set_xlim(x_min, x_max)
        self.data_plot.set_ylim(
            self.y_min - ((self.plot_height_factor - 1) * abs(self.y_min)),
            self.y_max + ((self.plot_height_factor - 1) * self.y_max))

        self.vertical_line.set_xdata((x_min + x_max) / 2)
        self.gui.canvas.draw()

    def draw_graph(self):
        """
        Redraws the graph with the right colors, labels, etc.
        """
        if self.sensor_controller.sensor_data is None or self.current_plot is None:
            return

        # Clear the plot
        self.data_plot.clear()

        # Get the boundaries of the plot axis
        self.x_min_dt = self.sensor_controller.df[ABSOLUTE_DATETIME].min()
        self.x_max_dt = self.sensor_controller.df[ABSOLUTE_DATETIME].max()
        self.x_min = date2num(self.x_min_dt)
        self.x_max = date2num(self.x_max_dt)
        if self.x_min == self.x_max:
            self.x_max = self.x_min + 1

        # Remove outliers before assessing y_min and y_max value for plot
        self.y_min = self.sensor_controller.df[self.current_plot].quantile(.0001)
        self.y_max = self.sensor_controller.df[self.current_plot].quantile(.9999)
        if self.y_min == self.y_max:
            self.y_max = self.y_min + 1

        # Set the axis boundaries
        self.data_plot.axis([self.x_min, self.x_max, self.y_min, self.y_max])

        # Plot the graph
        self.data_plot.plot(
            self.sensor_controller.df[ABSOLUTE_DATETIME],
            self.sensor_controller.df[self.current_plot],
            ',-',
            linewidth=1,
            color='black'
        )

        # Draw a red vertical line in the middle of the plot
        self.vertical_line = self.data_plot.axvline(x=0)
        self.vertical_line.set_color('red')

        # Add label types to dictionary
        for label_type in LabelType.select():
            self.label_types[label_type.id] = {label_type.activity, label_type.color}

        # Get labels and add to plot
        labels = Label.select().where(Label.sensor_data_file == self.sensor_controller.sensor_data_file.id)
        self.highlights = {}

        for label in labels:
            self.add_label_highlight(label.start_time, label.end_time, label.label_type)

        self.gui.canvas.draw()

    def add_label_highlight(self, label_start: dt.datetime, label_end: dt.datetime, label_type_id: int):
        label_type = LabelType.get_by_id(label_type_id)
        label_start_num = date2num(label_start)
        label_end_num = date2num(label_end)
        alpha = self.project_controller.get_setting('label_opacity') / 100
        span = self.data_plot.axvspan(
            label_start_num,
            label_end_num,
            facecolor=label_type.color,
            alpha=alpha
        )
        text = self.data_plot.text(
            (label_start_num + label_end_num) / 2,
            self.y_max * 0.75,
            label_type.activity,
            horizontalalignment='center'
        )
        self.highlights[label_start] = (span, text)

    def show_label_dialog(self, datetime1: dt.datetime, datetime2: dt.datetime, shortcut):
        self.label_dialog = LabelDialog(self.sensor_controller)
        self.label_dialog.set_times(datetime1, datetime2)
        self.label_dialog.show_dialog(shortcut)

        if self.label_dialog.is_accepted:
            self.add_label_highlight(
                self.label_dialog.label.start_time,
                self.label_dialog.label.end_time,
                self.label_dialog.label.label_type
            )
            self.gui.canvas.draw()

    def on_plot_click(self, event):
        """
        Handles the labeling by clicking on the graph.

        :param event: Specifies what event triggered this function.
        """
        if self.sensor_controller.sensor_data is None:
            return  # TODO: Raise error

        # Convert x-position to UTC datetime
        datetime = num2date(event.xdata).astimezone(pytz.utc).replace(tzinfo=None)

        if event.button == MouseButton.LEFT:
            self.on_click_datetime = datetime
        elif event.button == MouseButton.RIGHT and self.on_click_datetime is None:
            # Right mouse button clicked for first time
            self.on_click_datetime = datetime
        elif event.button == MouseButton.RIGHT:
            # Right mouse button clicked for second time
            if self.gui.current_key_pressed:
                label_shortcut = (LabelType.get(LabelType.keyboard_shortcut == self.gui.current_key_pressed)).id
            else:
                label_shortcut = None

            self.show_label_dialog(self.on_click_datetime, datetime, label_shortcut)
            self.on_click_datetime = None

    def on_plot_release(self, event):
        """
        Handles the labeling by clicking, but is only triggered when the user releases the mouse button.
        :param event: Specifies the event that triggers this function.
        """
        if event.button == MouseButton.LEFT:
            if self.sensor_controller.sensor_data is None:
                return

            # Convert the x-position to a Python datetime
            datetime = num2date(event.xdata).astimezone(pytz.utc).replace(tzinfo=None)

            # Delete the label if the on_click datetime is the same as the on_release datetime
            if datetime == self.on_click_datetime:
                try:
                    label = Label.get((Label.sensor_data_file == self.sensor_controller.sensor_data_file.id) &
                                      (Label.start_time <= datetime) &
                                      (Label.end_time >= datetime))
                    self.delete_label(label)
                except DoesNotExist as e:
                    print(e)
            else:
                if self.gui.current_key_pressed:
                    try:
                        label_shortcut = LabelType.get(LabelType.keyboard_shortcut == self.gui.current_key_pressed).id
                    except DoesNotExist:
                        label_shortcut = None
                else:
                    label_shortcut = None

                self.show_label_dialog(self.on_click_datetime, datetime, label_shortcut)

            # Set [on_click_datetime] to None to reset on_click behavior
            self.on_click_datetime = None

    def delete_label(self, label):
        reply = QMessageBox.question(self.gui, "Message", "Are you sure you want to delete this label?",
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            label.delete_instance()

            # Remove label highlight and text from plot
            self.highlights[label.start_time][0].remove()
            self.highlights[label.start_time][1].remove()
