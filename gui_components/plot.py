from datetime import timedelta, datetime

import pandas as pd
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QMessageBox
from matplotlib.dates import date2num, num2date

from data_import.label_data import LabelData
from data_storage.label_storage import LabelManager
from gui.label_dialog import LabelSpecs

LABEL_START_TIME_INDEX = 0
LABEL_END_TIME_INDEX = 1
LABEL_LABEL_NAME_INDEX = 2

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
QDATETIME_FORMAT = "yyyy-MM-dd HH:mm:ss.zzz"


class Plot:

    def __init__(self, gui):
        self.gui = gui
        self.settings = gui.settings
        self.sensor_data = gui.sensor_data

        self.label_storage = LabelManager(self.gui.project_dialog.project_name)
        self.label_data = LabelData(self.label_storage)

        self.data_plot = None
        self.current_plot = None
        self.vertical_line = None

        self.formulas = dict()
        self.highlights = dict()
        self.colors = dict()

        self.x_min_dt = None
        self.x_max_dt = None
        self.x_min = None
        self.x_max = None

        self.y_min = None
        self.y_max = None

        self.plot_width = self.settings.get_setting('plot_width')
        self.plot_height_factor = self.settings.get_setting('plot_height_factor')

        self.new_label = None
        self.large_label = None

        # Initialize the boolean that keeps track if the user is labeling with the right-mouse button
        self.labeling = False

    def new_plot(self):
        """
        Adds a function to the DataFrame as new column.
        """
        try:
            if not self.gui.lineEdit_function_name.text():
                raise Exception
            self.sensor_data.data.add_column_from_func(self.gui.lineEdit_function_name.text(),
                                                       self.gui.lineEdit_function_regex.text())
            self.sensor_data.df = self.sensor_data.data.get_data()
            self.gui.comboBox_functions.addItem(self.gui.lineEdit_function_name.text())
            self.formulas[self.gui.lineEdit_function_name.text()] = self.gui.lineEdit_function_regex.text()
            stored_formulas = self.settings.get_setting("formulas")
            stored_formulas[self.gui.lineEdit_function_name.text()] = self.gui.lineEdit_function_regex.text()
            self.settings.set_setting("formulas", stored_formulas)
            self.gui.lineEdit_function_regex.clear()
            self.gui.lineEdit_function_name.clear()
        except:
            QMessageBox.warning(self.gui, 'Warning', "Please enter a valid regular expression",
                                QMessageBox.Cancel)

    def change_plot(self):
        """
        If the user changes the variable on the y-axis, this function changes the label if necessary and redraws the
        plot.
        """
        self.current_plot = self.gui.comboBox_functions.currentText()

        if self.current_plot in self.formulas:
            self.gui.label_current_formula.setText(self.formulas[self.current_plot])
        else:
            self.gui.label_current_formula.clear()

        self.y_min = self.sensor_data.df[self.current_plot].min()
        self.y_max = self.sensor_data.df[self.current_plot].max()
        self.draw_graph()

    def change_plot_width(self, value):
        self.settings.set_setting('plot_width', value)
        self.plot_width = value

        if self.sensor_data.data:
            self.update_plot_axis()

    def change_plot_height(self, value):
        self.settings.set_setting('plot_height_factor', value)
        self.plot_height_factor = value

    def update_plot_axis(self, position=-1.0):
        """
        Every time the timer calls this function, the axis of the graph is updated.
        """
        position_dt = self.x_min_dt + timedelta(seconds=self.gui.mediaPlayer.position() / 1000)
        new_position_dt = position_dt if position == -1.0 else position

        plot_width_delta = timedelta(seconds=(self.plot_width / 2))
        video_offset_delta = timedelta(seconds=self.gui.doubleSpinBox_video_offset.value())
        video_offset = timedelta(seconds=0)

        if self.gui.video.offset is not None:
            video_offset = self.gui.video.offset

        x_min = date2num(new_position_dt - plot_width_delta - video_offset_delta - video_offset)
        x_max = date2num(new_position_dt + plot_width_delta - video_offset_delta - video_offset)

        self.data_plot.set_xlim(x_min, x_max)
        self.data_plot.set_ylim(self.y_min, self.plot_height_factor * self.y_max)
        self.vertical_line.set_xdata((x_min + x_max) / 2)
        self.gui.canvas.draw()

    def draw_graph(self):
        """
        Redraws the graph with the right colors, labels, etc.
        """
        if not self.sensor_data.data:
            return

        self.data_plot.clear()

        time = self.sensor_data.df[self.sensor_data.df.columns[0]]
        self.sensor_data.df['clock_time'] = self.sensor_data.datetime + pd.to_timedelta(time, unit='s')

        self.x_min_dt = self.sensor_data.df['clock_time'].min()
        self.x_max_dt = self.sensor_data.df['clock_time'].max()
        self.x_min = date2num(self.sensor_data.df['clock_time'].min())
        self.x_max = date2num(self.sensor_data.df['clock_time'].max())

        self.data_plot.axis([self.x_min, self.x_max, self.y_min, self.y_max])
        self.data_plot.plot(self.sensor_data.df['clock_time'], self.sensor_data.df[self.current_plot], ',-',
                            linewidth=1, color='black')
        self.vertical_line = self.data_plot.axvline(x=0)
        self.vertical_line.set_color('red')

        for label_type in self.label_storage.get_label_types():
            self.colors[label_type[0]] = label_type[1]

        labels = self.label_storage.get_labels_date(self.sensor_data.data.metadata['sn'],
                                                    self.sensor_data.data.metadata['datetime'].date())
        self.highlights = {}

        for label in labels:
            label_start = label[LABEL_START_TIME_INDEX]
            label_end = label[LABEL_END_TIME_INDEX]
            self.add_label_highlight(label_start, label_end, label[LABEL_LABEL_NAME_INDEX])

        self.gui.canvas.draw()

    def add_label_highlight(self, label_start: datetime, label_end: datetime, label_type: str):
        label_start_num = date2num(label_start)
        label_end_num = date2num(label_end)
        alpha = self.settings.get_setting('label_opacity') / 100
        span = self.data_plot.axvspan(label_start_num, label_end_num, facecolor=self.colors[label_type], alpha=alpha)
        text = self.data_plot.text((label_start_num + label_end_num) / 2, self.y_max * 0.75, label_type,
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
        if self.sensor_data.data:
            xdata_dt = num2date(event.xdata).replace(tzinfo=None)
            xdata_qdt = QDateTime.fromString(xdata_dt.strftime(DATETIME_FORMAT)[:-3], QDATETIME_FORMAT)

            # If the left mouse button is used, start a new labeling dialog with the right starting time and
            # wait for the onrelease function
            if event.button == 1:
                self.new_label = LabelSpecs(self.gui.project_dialog.project_name, self.sensor_data.data.metadata['sn'],
                                            self.label_storage)

                self.new_label.dateTimeEdit_start.setDateTime(xdata_qdt)

            # If the right mouse button is used, check if this is the first or second time
            elif event.button == 3:
                if not self.labeling:
                    self.large_label = LabelSpecs(self.gui.project_dialog.project_name,
                                                  self.sensor_data.data.metadata['sn'],
                                                  self.label_storage)
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

                    for label in self.label_storage.get_labels_date(self.sensor_data.data.metadata['sn'],
                                                                    self.sensor_data.data.metadata[
                                                                        'datetime'].date()):
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
                            self.label_storage.delete_label(delete_label[LABEL_START_TIME_INDEX],
                                                            self.sensor_data.data.metadata['sn'])

                            # Remove label highlight and text from plot
                            self.highlights[delete_label[LABEL_START_TIME_INDEX]][0].remove()
                            self.highlights[delete_label[LABEL_START_TIME_INDEX]][1].remove()
                    else:
                        self.large_label.exec_()

                    if self.large_label.is_accepted:
                        self.add_label_highlight(self.large_label.label.start, self.large_label.label.end,
                                                 self.large_label.label.label)
                        self.gui.canvas.draw()

                self.labeling = not self.labeling

    def onrelease(self, event):
        """
        Handles the labeling by clicking, but is only triggered when the user releases the mouse button.
        :param event: Specifies the event that triggers this function.
        """
        if self.sensor_data.data:
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

                for label in self.label_storage.get_labels_date(self.sensor_data.data.metadata['sn'],
                                                                self.sensor_data.data.metadata['datetime'].date()):
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
                        self.label_storage.delete_label(delete_label[LABEL_START_TIME_INDEX],
                                                        self.sensor_data.data.metadata['sn'])
                        # Remove label highlight and text from plot
                        self.highlights[delete_label[LABEL_START_TIME_INDEX]][0].remove()
                        self.highlights[delete_label[LABEL_START_TIME_INDEX]][1].remove()
                else:
                    self.new_label.exec_()

                if self.new_label.is_accepted:
                    self.add_label_highlight(self.new_label.label.start, self.new_label.label.end,
                                             self.new_label.label.label)
                    self.gui.canvas.draw()
            elif event.button == 3:
                pass