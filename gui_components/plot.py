import datetime as dt
from typing import Optional

import pytz
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QMessageBox
from matplotlib.dates import date2num, num2date

from constants import COL_ABSOLUTE_DATETIME
from data_import.label_data import LabelData
from database.label_manager import LabelManager
from database.label_type_manager import LabelTypeManager
from gui.dialogs.label import LabelSpecs
from gui_components.sensor_data_file import SensorDataFile
from gui.dialogs.project_settings import ProjectSettingsDialog

LABEL_START_TIME_INDEX = 0
LABEL_END_TIME_INDEX = 1
LABEL_TYPE_INDEX = 2

KEY_ACTIVITY = "activity"
KEY_ID = "id"
KEY_COLOR = "color"

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
QDATETIME_FORMAT = "yyyy-MM-dd HH:mm:ss.zzz"


class Plot:

    def __init__(self, gui):
        self.gui = gui
        self.settings: ProjectSettingsDialog = gui.settings
        self.sensor_data_file: SensorDataFile = gui.sensor_data_file
        self.project_timezone = pytz.timezone(self.settings.get_setting('timezone'))

        # self.reset()
        self.label_manager = LabelManager(self.settings)
        self.label_type_manager = LabelTypeManager(self.settings)
        self.label_data = LabelData(self.label_manager)
        self.formulas = self.settings.get_setting('formulas')
        self.plot_width = self.settings.get_setting('plot_width')
        self.plot_height_factor = self.settings.get_setting('plot_height_factor')

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

        self.new_label: Optional[LabelSpecs] = None
        self.large_label = None

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
            self.sensor_data_file.sensor_data.add_column_from_func(
                self.gui.lineEdit_function_name.text(),
                self.gui.lineEdit_function_regex.text()
            )

            # Get the dataframe
            self.sensor_data_file.df = self.sensor_data_file.sensor_data.get_data()

            # Add the new function to the combobox
            self.gui.comboBox_functions.addItem(self.gui.lineEdit_function_name.text())

            self.formulas[self.gui.lineEdit_function_name.text()] = self.gui.lineEdit_function_regex.text()
            stored_formulas = self.settings.get_setting("formulas")
            stored_formulas[self.gui.lineEdit_function_name.text()] = self.gui.lineEdit_function_regex.text()
            self.settings.set_setting("formulas", stored_formulas)
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
        self.current_plot = self.gui.comboBox_functions.currentText()

        if self.current_plot in self.formulas:
            self.gui.label_current_function_value.setText(self.formulas[self.current_plot])
        else:
            self.gui.label_current_function_value.clear()

        self.draw_graph()

        # Save the column in the database
        self.sensor_data_file.save_last_used_column(self.current_plot)

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
                self.settings.set_setting('formulas', self.formulas)

                # Delete the selected plot from the combobox and update the plot
                self.gui.comboBox_functions.removeItem(index)
                self.gui.comboBox_functions.setCurrentIndex(0)
                self.change_plot()

    def change_plot_width(self, value):  # TODO: An error occurs where there is an infinite loop of change_plot_width
        self.settings.set_setting('plot_width', value)
        self.plot_width = value

        if self.sensor_data_file.sensor_data is not None:
            self.update_plot_axis()

    def change_plot_height(self, value):
        self.settings.set_setting('plot_height_factor', value)
        self.plot_height_factor = value

    def update_plot_axis(self, position=-1.0):
        """
        Every time the timer calls this function, the axis of the graph is updated.
        """
        if self.x_min_dt is None:
            return
        position_dt = self.x_min_dt + dt.timedelta(seconds=self.gui.mediaPlayer.position() / 1000)  #  TODO: Fix bug when starting new project
        new_position_dt = position_dt if position == -1.0 else position

        plot_width_delta = dt.timedelta(seconds=(self.plot_width / 2))
        video_offset_delta = dt.timedelta(seconds=self.gui.doubleSpinBox_video_offset.value())
        video_offset = dt.timedelta(seconds=0)

        if self.gui.video.init_offset is not None:
            video_offset = self.gui.video.init_offset

        x_min = date2num(new_position_dt - plot_width_delta - video_offset_delta - video_offset)
        x_max = date2num(new_position_dt + plot_width_delta - video_offset_delta - video_offset)

        self.data_plot.set_xlim(x_min, x_max)
        self.data_plot.set_ylim(
            self.y_min - ((self.plot_height_factor - 1) * abs(self.y_min)),
            self.y_max + ((self.plot_height_factor - 1) * self.y_max))

        # self.data_plot.set_ylim(self.y_min, self.plot_height_factor * self.y_max)
        self.vertical_line.set_xdata((x_min + x_max) / 2)
        self.gui.canvas.draw()

    def draw_graph(self):
        """
        Redraws the graph with the right colors, labels, etc.
        """
        if self.sensor_data_file.sensor_data is None:
            return

        # Clear the plot
        self.data_plot.clear()

        # Get the boundaries of the plot axis
        self.x_min_dt = self.sensor_data_file.df[COL_ABSOLUTE_DATETIME].min()
        self.x_max_dt = self.sensor_data_file.df[COL_ABSOLUTE_DATETIME].max()
        self.x_min = date2num(self.x_min_dt)
        self.x_max = date2num(self.x_max_dt)
        if self.x_min == self.x_max:
            self.x_max = self.x_min + 1

        # Remove outliers before assessing y_min and y_max value for plot
        self.y_min = self.sensor_data_file.df[self.current_plot].quantile(.0001)
        self.y_max = self.sensor_data_file.df[self.current_plot].quantile(.9999)
        if self.y_min == self.y_max:
            self.y_max = self.y_min + 1

        # Set the axis boundaries
        self.data_plot.axis([self.x_min, self.x_max, self.y_min, self.y_max])

        # Plot the graph
        self.data_plot.plot(
            self.sensor_data_file.df[COL_ABSOLUTE_DATETIME],
            self.sensor_data_file.df[self.current_plot],
            ',-',
            linewidth=1,
            color='black'
        )

        # Draw a red vertical line in the middle of the plot
        self.vertical_line = self.data_plot.axvline(x=0)
        self.vertical_line.set_color('red')

        # Add label types to dictionary
        for row in self.label_type_manager.get_all_label_types():
            self.label_types[row[KEY_ID]] = {KEY_ACTIVITY: row[KEY_ACTIVITY], KEY_COLOR: row[KEY_COLOR]}

        # Get labels and add to plot
        labels = self.label_manager.get_all_labels_by_file(self.sensor_data_file.id_)
        self.highlights = {}

        for label in labels:
            label_start = label[LABEL_START_TIME_INDEX]
            label_end = label[LABEL_END_TIME_INDEX]
            label_type = label[LABEL_TYPE_INDEX]
            self.add_label_highlight(label_start, label_end, label_type)

        self.gui.canvas.draw()

    def add_label_highlight(self, label_start: dt.datetime, label_end: dt.datetime, label_type: int):
        label_start_num = date2num(label_start)
        label_end_num = date2num(label_end)
        alpha = self.settings.get_setting('label_opacity') / 100
        span = self.data_plot.axvspan(label_start_num,
                                      label_end_num,
                                      facecolor=self.label_types[label_type][KEY_COLOR],
                                      alpha=alpha)
        text = self.data_plot.text((label_start_num + label_end_num) / 2,
                                   self.y_max * 0.75,
                                   self.label_types[label_type][KEY_ACTIVITY],
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
        if self.sensor_data_file.sensor_data is not None:
            # Convert the x-position to a Python datetime
            # xdata_dt = num2date(event.xdata).astimezone(pytz.utc).replace(tzinfo=None)
            xdata_dt = num2date(event.xdata).astimezone(self.gui.sensor_data_file.sensor_data.metadata.sensor_timezone).replace(tzinfo=None)
            # Convert to QDateTime, without milliseconds
            xdata_qdt = QDateTime.fromString(xdata_dt.strftime(DATETIME_FORMAT)[:-3], QDATETIME_FORMAT)

            # If the left mouse button is used, start a new labeling dialog with the right starting time and
            # wait for the onrelease function
            if event.button == 1:
                self.new_label = LabelSpecs(self.sensor_data_file.id_,
                                            self.label_manager,
                                            self.label_type_manager)

                self.new_label.dateTimeEdit_start.setDateTime(xdata_qdt)

            # If the right mouse button is used, check if this is the first or second time
            elif event.button == 3:
                if not self.labeling:
                    self.large_label = LabelSpecs(self.sensor_data_file.id_,
                                                  self.label_manager,
                                                  self.label_type_manager)
                    self.large_label.dateTimeEdit_start.setDateTime(xdata_qdt)
                # If it is the second time, check if the user wants to delete the label or if the label should start
                # or end at the start or end of another label
                else:
                    deleting = False

                    if xdata_qdt < self.large_label.dateTimeEdit_start.dateTime():
                        self.large_label.dateTimeEdit_end.setDateTime(self.large_label.dateTimeEdit_start.dateTime())
                        self.large_label.dateTimeEdit_start.setDateTime(xdata_qdt)
                    else:
                        self.large_label.dateTimeEdit_end.setDateTime(xdata_qdt)

                    start = self.large_label.dateTimeEdit_start.dateTime().toPyDateTime()
                    end = self.large_label.dateTimeEdit_end.dateTime().toPyDateTime()

                    for label in self.label_manager.get_all_labels_by_file(self.sensor_data_file.id_):
                        label_start = label[LABEL_START_TIME_INDEX]
                        label_end = label[LABEL_END_TIME_INDEX]
                        label_start_qdt = QDateTime.fromString(label_start.strftime(DATETIME_FORMAT)[:-3],
                                                               QDATETIME_FORMAT)
                        label_end_qdt = QDateTime.fromString(label_end.strftime(DATETIME_FORMAT)[:-3], QDATETIME_FORMAT)

                        if label_start < start < label_end and label_start < end < label_end:
                            deleting = True
                            delete_label = label
                            break
                        elif label_start < start < label_end or label_start < end < label_end:
                            if label_start < start < label_end:
                                self.large_label.dateTimeEdit_start.setDateTime(label_end_qdt)
                            else:
                                self.large_label.dateTimeEdit_end.setDateTime(label_start_qdt)

                    if deleting:
                        reply = QMessageBox.question(self.gui, "Message", "Are you sure you want to delete this label?",
                                                     QMessageBox.Yes, QMessageBox.No)
                        if reply == QMessageBox.Yes:
                            self.label_manager.delete_label_by_start_and_file(delete_label[LABEL_START_TIME_INDEX],
                                                                              self.sensor_data_file.id_)

                            # Remove label highlight and text from plot
                            self.highlights[delete_label[LABEL_START_TIME_INDEX]][0].remove()
                            self.highlights[delete_label[LABEL_START_TIME_INDEX]][1].remove()
                    else:
                        self.large_label.exec()

                    if self.large_label.is_accepted:
                        self.add_label_highlight(self.large_label.selected_label.start,
                                                 self.large_label.selected_label.end,
                                                 self.large_label.selected_label.type)
                        self.gui.canvas.draw()

                self.labeling = not self.labeling

    def onrelease(self, event):
        """
        Handles the labeling by clicking, but is only triggered when the user releases the mouse button.
        :param event: Specifies the event that triggers this function.
        """
        if self.sensor_data_file.sensor_data is not None:
            xdata_dt = num2date(event.xdata).replace(tzinfo=None)
            xdata_qdt = QDateTime.fromString(xdata_dt.strftime(DATETIME_FORMAT)[:-3], QDATETIME_FORMAT)

            # If the left mouse button is released, delete or label the right area, similar to the latter
            # part of onclick.
            if event.button == 1:
                deleting = False

                if xdata_qdt < self.new_label.dateTimeEdit_start.dateTime():
                    # Switch the values of start and end
                    self.new_label.dateTimeEdit_end.setDateTime(self.new_label.dateTimeEdit_start.dateTime())
                    self.new_label.dateTimeEdit_start.setDateTime(xdata_qdt)
                else:
                    self.new_label.dateTimeEdit_end.setDateTime(xdata_qdt)

                start = self.new_label.dateTimeEdit_start.dateTime().toPyDateTime()
                end = self.new_label.dateTimeEdit_end.dateTime().toPyDateTime()

                for label in self.label_manager.get_all_labels_by_file(self.sensor_data_file.id_):
                    label_start = label[LABEL_START_TIME_INDEX]
                    label_end = label[LABEL_END_TIME_INDEX]

                    # If 'onclick' and 'onrelease' are both inside the label, then delete the label
                    if label_start < start < label_end and label_start < end < label_end:
                        deleting = True
                        delete_label = label
                        break
                    # Else if only 'onclick' is inside the label, then set the start value equal to the end of the label
                    elif label_start < start < label_end:
                        self.new_label.dateTimeEdit_start.setDateTime(label_end)
                    # Else if only 'onrelease' is inside the label, then set the end value equal to the start of the
                    # label
                    elif label_start < end < label_end:
                        self.new_label.dateTimeEdit_end.setDateTime(label_start)

                if deleting:
                    reply = QMessageBox.question(self.gui, "Message", "Are you sure you want to delete this label?",
                                                 QMessageBox.Yes, QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        self.label_manager.delete_label_by_start_and_file(delete_label[LABEL_START_TIME_INDEX],
                                                                          self.sensor_data_file.sensor_id)
                        # Remove label highlight and text from plot
                        self.highlights[delete_label[LABEL_START_TIME_INDEX]][0].remove()
                        self.highlights[delete_label[LABEL_START_TIME_INDEX]][1].remove()
                else:
                    self.new_label.exec()

                if self.new_label.is_accepted:
                    self.add_label_highlight(self.new_label.selected_label.start,
                                             self.new_label.selected_label.end,
                                             self.new_label.selected_label.type)
                    self.gui.canvas.draw()
            elif event.button == 3:
                pass
