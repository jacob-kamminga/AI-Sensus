import datetime as dt
from typing import Optional

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

        self.label_dialog: Optional[LabelDialog] = None

        # Initialize the boolean that keeps track if the user is labeling with the right-mouse button
        self.labeling = False

    # def reset(self):
    #     """
    #     Part of init functionality is in reset_plot method, so that plot can be reset when changing project
    #     :return:
    #     """

    def new_plot(self):
        """
        Adds a function to the DataFrame as new column.
        """
        try:
            # If no function is selected, raise an exception
            if not self.gui.lineEdit_function_name.text():
                raise Exception

            # Add a column to the sensor data, based on the selected function
            self.sensor_controller.sensor_data.add_column_from_func(
                self.gui.lineEdit_function_name.text(),
                self.gui.lineEdit_function_regex.text()
            )

            # Get the dataframe
            self.sensor_controller.df = self.sensor_controller.sensor_data.get_data()

            # Add the new function to the combobox
            self.gui.comboBox_functions.addItem(self.gui.lineEdit_function_name.text())

            self.formulas[self.gui.lineEdit_function_name.text()] = self.gui.lineEdit_function_regex.text()
            stored_formulas = self.project_controller.get_setting("formulas")
            stored_formulas[self.gui.lineEdit_function_name.text()] = self.gui.lineEdit_function_regex.text()
            self.project_controller.set_setting("formulas", stored_formulas)
            self.gui.lineEdit_function_regex.clear()
            self.gui.lineEdit_function_name.clear()
        except Exception as e:
            print(e)
            QMessageBox.warning(self.gui, 'Warning', "Please enter a valid regular expression",
                                QMessageBox.Cancel)

    def change_plot(self):
        """
        If the user changes the variable on the y-axis, this function changes the label if necessary and redraws the
        plot.
        """
        self.set_current_plot(self.gui.comboBox_functions.currentText())

        if self.current_plot in self.formulas:
            self.gui.label_current_function_value.setText(self.formulas[self.current_plot])
        else:
            self.gui.label_current_function_value.clear()

        self.draw_graph()

        # Save the column in the database
        self.sensor_controller.save_last_used_column(self.current_plot)

    def set_current_plot(self, new_plot):
        # test if this column has numeric values
        if is_numeric_dtype(self.sensor_controller.df[new_plot]):
            self.current_plot = new_plot
            return True
        else:
            # self.current_plot = None
            return False

    def delete_formula(self):
        selected_plot = self.gui.comboBox_functions.currentText()
        index = self.gui.comboBox_functions.findText(selected_plot)

        if selected_plot in self.formulas:
            res = QMessageBox.warning(
                self.gui,
                'Confirm delete',
                'Are you sure you want to delete the selected formula?',
                QMessageBox.Ok | QMessageBox.Cancel
            )

            if res == QMessageBox.Ok:
                # Delete the selected plot from settings
                self.formulas.pop(selected_plot)
                self.project_controller.set_setting('formulas', self.formulas)

                # Delete the selected plot from the combobox and update the plot
                self.gui.comboBox_functions.removeItem(index)
                self.gui.comboBox_functions.setCurrentIndex(0)
                self.change_plot()

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
        span = self.data_plot.axvspan(label_start_num,
                                      label_end_num,
                                      facecolor=label_type.color,
                                      alpha=alpha)
        text = self.data_plot.text((label_start_num + label_end_num) / 2,
                                   self.y_max * 0.75,
                                   label_type.activity,
                                   horizontalalignment='center')
        self.highlights[label_start] = (span, text)

    def add_suggestion_highlight(self, start: float, end: float, label: str):
        span = self.data_plot.axvspan(start, end, facecolor='gold', alpha=0.4)
        text = self.data_plot.text((start + end) / 2, self.y_max * 0.5, "Suggested label:\n" + label,
                                   horizontalalignment='center')

        self.gui.canvas.draw()
        return span, text

    def onclick(self, event):
        """
        Handles the labeling by clicking on the graph.

        :param event: Specifies what event triggered this function.
        """
        if self.sensor_controller.sensor_data is not None:
            # Convert the x-position to a Python datetime localized as UTC
            x_datetime = num2date(event.xdata).astimezone(pytz.utc)

            # If the left mouse button is used, start a new labeling dialog with the right starting time and
            # wait for the onrelease function
            if event.button == MouseButton.LEFT:
                self.label_dialog = LabelDialog(self.sensor_controller.sensor_data_file.id,
                                                self.sensor_controller.sensor_data.metadata.sensor_timezone)

                self.label_dialog.label.start_time = x_datetime

            # If the right mouse button is used, check if this is the first or second time
            elif event.button == MouseButton.RIGHT:
                if not self.labeling:
                    self.label_dialog = LabelDialog(self.sensor_controller.sensor_data_file.id,
                                                    self.sensor_controller.sensor_data.metadata.sensor_timezone)
                    self.label_dialog.label.start_time = x_datetime
                # If it is the second time, check if the user wants to delete the label or if the label should start
                # or end at the start or end of another label
                else:
                    deleting = False
                    delete_label = None

                    if x_datetime < self.label_dialog.label.start_time:
                        self.label_dialog.label.end_time = self.label_dialog.label.start_time
                        self.label_dialog.label.start_time = x_datetime
                    else:
                        self.label_dialog.label.end_time = x_datetime

                    new_start = self.label_dialog.label.start_time.replace(tzinfo=None)
                    new_end = self.label_dialog.label.end_time.replace(tzinfo=None)

                    labels = (Label
                              .select(Label.start_time, Label.end_time, Label.label_type)
                              .where(Label.sensor_data_file == self.sensor_controller.sensor_data_file.id))

                    for label in labels:
                        start = label.start_time
                        end = label.end_time

                        if start < new_start < end and \
                                start < new_end < end:
                            deleting = True
                            delete_label = label
                            break
                        elif start < new_start < end or \
                                start < new_end < end:
                            if start < new_start < end:
                                self.label_dialog.label.start_time = end
                            else:
                                self.label_dialog.label.end_time = start

                    if deleting:
                        self.delete_label(delete_label)
                    else:
                        if self.gui.current_key_pressed:
                            label_shortcut = (LabelType
                                              .get(LabelType.keyboard_shortcut == self.gui.current_key_pressed)
                                              ).id
                        else:
                            label_shortcut = None

                        self.label_dialog.show_dialog(label_shortcut)

                    if self.label_dialog.is_accepted:
                        self.add_label_highlight(self.label_dialog.label.start_time,
                                                 self.label_dialog.label.end_time,
                                                 self.label_dialog.label.label_type)
                        self.gui.canvas.draw()

                self.labeling = not self.labeling

    def onrelease(self, event):
        """
        Handles the labeling by clicking, but is only triggered when the user releases the mouse button.
        :param event: Specifies the event that triggers this function.
        """
        if self.sensor_controller.sensor_data is not None:
            # Convert the x-position to a Python datetime
            x_data_dt_sensor_utc = num2date(event.xdata).astimezone(pytz.utc)

            # If the left mouse button is released, delete or label the right area, similar to the latter
            # part of onclick.
            if event.button == MouseButton.LEFT:
                deleting = False
                delete_label = None
                if x_data_dt_sensor_utc < self.label_dialog.label.start_time:
                    # Switch the values of start and end
                    self.label_dialog.label.end_time = self.label_dialog.label.start_time
                    self.label_dialog.label.start_time = x_data_dt_sensor_utc
                else:
                    self.label_dialog.label.end_time = x_data_dt_sensor_utc

                new_start = self.label_dialog.label.start_time.replace(tzinfo=None)
                new_end = self.label_dialog.label.end_time.replace(tzinfo=None)

                labels = (Label
                          .select(Label.start_time, Label.end_time, Label.label_type)
                          .where(Label.sensor_data_file == self.sensor_controller.sensor_data_file.id))

                for label in labels:
                    start = label.start_time
                    end = label.end_time
                    # TODO implement the possibility for label overlap here (and in export of course)
                    # If 'onclick' and 'onrelease' are both inside the label, then delete the label
                    if start < new_start < end and \
                            start < new_end < end:
                        deleting = True
                        delete_label = label
                        break
                    # Else if only 'onclick' is inside the label, then set the new start value equal to the end of
                    # the existing label
                    elif start < new_start < end:
                        self.label_dialog.label.start_time = end
                    # Else if only 'onrelease' is inside the label, then set the end value equal to the start of the
                    # existing label
                    elif start < new_end < end:
                        self.label_dialog.label.end_time = start

                if deleting:
                    self.delete_label(delete_label)
                else:
                    if self.gui.current_key_pressed:
                        try:
                            label_shortcut = (LabelType
                                              .get(LabelType.keyboard_shortcut == self.gui.current_key_pressed)
                                              ).id
                        except DoesNotExist:
                            label_shortcut = None
                    else:
                        label_shortcut = None

                    self.label_dialog.show_dialog(label_shortcut)

                if self.label_dialog.is_accepted:
                    self.add_label_highlight(self.label_dialog.label.start_time,
                                             self.label_dialog.label.end_time,
                                             self.label_dialog.label.label_type)
                    self.gui.canvas.draw()
            elif event.button == MouseButton.RIGHT:
                pass

    def delete_label(self, delete_label):
        reply = QMessageBox.question(self.gui, "Message", "Are you sure you want to delete this label?",
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            label = Label.get(Label.start_time == delete_label.start_time,
                              Label.sensor_data_file == self.sensor_controller.sensor_data_file.id)
            label.delete_instance()

            # Remove label highlight and text from plot
            self.highlights[delete_label.start_time][0].remove()
            self.highlights[delete_label.start_time][1].remove()
