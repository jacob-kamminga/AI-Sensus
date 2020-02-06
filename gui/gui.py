from datetime import datetime
from datetime import timedelta

import matplotlib.animation
import matplotlib.pyplot as plt
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QShortcut, QDialog
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from pandas.plotting import register_matplotlib_converters
from sklearn.naive_bayes import GaussianNB

from data_export import export_data, windowing as wd
from database.db_subject import SubjectManager
from gui.camera_settings_dialog import CameraSettingsDialog
from gui.designer_gui import Ui_MainWindow
from gui.export_dialog import ExportDialog
from gui.label_dialog import LabelSpecs
from gui.label_settings_dialog import LabelSettingsDialog
from gui.machine_learning_dialog import MachineLearningDialog
from gui.new_dialog import NewProject
from gui.settings_dialog import SettingsDialog
from gui.subject_dialog import SubjectTable
from gui_components.camera import Camera
from gui_components.plot import Plot
from gui_components.sensor_data import SensorData
from gui_components.video import Video
from machine_learning.classifier import Classifier, make_predictions

LABEL_COL = 'Label'
TIME_COL = 'Time'
TIMESTAMP_COL = 'Timestamp'


class GUI(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        # Initialize the generated UI from designer_gui.py.
        self.setupUi(self)

        register_matplotlib_converters()

        # Before showing the full GUI, a dialog window needs to be prompted where the user can choose between an
        # existing project and a new project, in which case the settings need to be specified
        self.project_dialog = NewProject()
        self.project_dialog.exec_()

        # Save the settings from the new project dialog window.
        self.settings = self.project_dialog.new_settings

        # GUI components
        self.video = Video(self)
        self.sensor_data = SensorData(self)
        self.plot = Plot(self)
        self.camera = Camera(self)

        # Create video key shortcuts
        self.shortcut_plus_10s = QShortcut(Qt.Key_Right, self)
        self.shortcut_minus_10s = QShortcut(Qt.Key_Left, self)
        self.shortcut_pause = QShortcut(Qt.Key_Space, self)

        # Connect all the buttons, spin boxes, combo boxes and line edits to their appropriate helper functions.
        self.pushButton_play.clicked.connect(self.video.toggle_play)
        self.shortcut_pause.activated.connect(self.video.toggle_play)
        self.shortcut_plus_10s.activated.connect(self.video.fast_forward_10s)
        self.shortcut_minus_10s.activated.connect(self.video.rewind_10s)
        self.actionOpen_Video.triggered.connect(self.video.prompt_file)
        self.actionOpen_Sensor_Data.triggered.connect(self.sensor_data.prompt_file)
        self.pushButton_label.clicked.connect(self.open_label)
        self.actionImport_Settings.triggered.connect(self.open_settings)
        self.actionCamera_Settings.triggered.connect(self.open_camera_settings)
        self.actionLabel_Settings.triggered.connect(self.open_label_settings)
        self.lineEdit_function_regex.returnPressed.connect(self.plot.new_plot)
        self.doubleSpinBox_video_offset.valueChanged.connect(self.camera.change_offset)
        self.doubleSpinBox_speed.valueChanged.connect(self.video.change_speed)
        self.doubleSpinBox_plot_width.valueChanged.connect(self.plot.change_plot_width)
        self.doubleSpinBox_plot_height.valueChanged.connect(self.plot.change_plot_height)
        self.comboBox_functions.activated.connect(self.plot.change_plot)
        self.actionSubject_Mapping.triggered.connect(self.open_subject_mapping)
        self.actionExport_Sensor_Data.triggered.connect(self.open_export)
        self.actionMachine_Learning.triggered.connect(self.open_machine_learning)

        # Initialize the libraries that are needed to plot the sensor data, and add them to the GUI
        self.figure = matplotlib.pyplot.figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.resize(self.canvas.width(), 200)
        self.verticalLayout_plot.addWidget(self.canvas)
        self.canvas.mpl_connect('button_press_event', self.plot.onclick)
        self.canvas.mpl_connect('button_release_event', self.plot.onrelease)

        # Connect the QMediaPlayer to the right widget
        self.mediaPlayer.setVideoOutput(self.videoWidget_player)

        # Connect some events that QMediaPlayer generates to their appropriate helper functions
        self.mediaPlayer.positionChanged.connect(self.video.position_changed)
        self.mediaPlayer.durationChanged.connect(self.video.duration_changed)

        # Connect the usage of the slider to its appropriate helper function
        self.horizontalSlider_time.sliderMoved.connect(self.video.set_position)
        self.horizontalSlider_time.setEnabled(False)

        # Initialize a timer that makes sure that the sensor data plays smoothly
        self.timer = QtCore.QTimer(self)

        # Variable that stores start and stop time of a loop that the video-player should play
        self.loop = None

        # Load the stored width that the data-plot should have
        self.doubleSpinBox_plot_width.setValue(self.plot.plot_width)
        self.doubleSpinBox_plot_height.setValue(self.plot.plot_height_factor)

        # Initialize the classes that retrieve information from the database
        self.subject_mapping = SubjectManager(self.project_dialog.project_name)

        # Machine learning fields
        self.ml_dataframe = None
        self.ml_classifier_engine = GaussianNB()
        self.ml_used_columns = []
        self.ml_classifier = Classifier(self.ml_classifier_engine)

        # Open the last opened files
        self.video.open_previous_file()
        self.sensor_data.open_previous_file()

    def open_label(self):
        """
        Opens the label dialog window.
        """
        if not self.sensor_data.data:
            QMessageBox.information(self, "Warning", "You need to import sensor data first.", QMessageBox.Ok)
        else:
            dialog = LabelSpecs(self.project_dialog.project_name,
                                self.sensor_data.data.metadata['sn'],
                                self.plot.label_storage)
            dialog.exec_()
            dialog.show()

            if dialog.is_accepted:
                self.add_label_highlight(dialog.label.start, dialog.label.end, dialog.label.label)

    def open_settings(self):
        """
        Opens the settings dialog window.
        """
        settings = SettingsDialog(self.settings)
        settings.exec_()
        settings.show()

    def open_camera_settings(self):
        """
        Opens the camera settings dialog window.
        """
        camera_settings = CameraSettingsDialog(self.video.camera_manager)
        camera_settings.exec_()
        camera_settings.show()

        if camera_settings.selected_camera_id is not None:
            self.camera.change_camera(camera_settings.selected_camera_id)

    def open_label_settings(self):
        """
        Opens the label settings dialog window.
        """
        label_settings = LabelSettingsDialog(self.plot.label_storage, self.settings)
        label_settings.exec_()
        label_settings.show()

        # Upon window close
        if label_settings.settings_changed:
            self.plot.draw_graph()

    def open_subject_mapping(self):
        """
        Opens the subject mapping dialog window.
        """
        subject_mapping = SubjectTable(self.project_dialog.project_name)
        subject_mapping.exec_()
        subject_mapping.show()

    def open_export(self):
        """
        Opens the export dialog window, and if a subject and a file location and name are chosen, exports the data
        accordingly.
        """
        export = ExportDialog()
        export.comboBox.addItems(self.subject_mapping.get_subjects())
        export.exec_()
        export.show()

        if export.is_accepted and export.comboBox.currentText():
            filename, _ = QFileDialog.getSaveFileName(self, "Save File", QDir.homePath())

            try:
                export_data.export(self.subject_mapping.get_dataframes_subject(export.comboBox.currentText()), "Label",
                                   "Timestamp", filename, [])
            except Exception as e:
                print(e)
                QMessageBox.warning(self, 'Warning', str(e), QMessageBox.Cancel)

    def open_machine_learning(self):
        """
        Opens the machine learning dialog window.
        :return:
        """
        # TODO: Rewrite function such that 'start' and 'end' are datetimes instead of floats
        columns = [self.comboBox_functions.itemText(i) for i in range(self.comboBox_functions.count())]
        dialog = MachineLearningDialog(columns)
        dialog.exec()

        self.ml_used_columns = []
        funcs = {
            'mean': np.mean,
            'std': np.std
        }
        features = []

        if dialog.is_accepted:
            # save current position in the video
            original_position = self.mediaPlayer.position()

            at_least_1_column = False
            # for each selected column, add new column names to the lists for machine learning
            for column in columns:
                if dialog.column_dict[column]:
                    at_least_1_column = True
                    self.ml_used_columns.append(column)

                    for func in funcs:
                        features.append(column + '_' + func)

            # Show warning if user has selected no columns
            if not at_least_1_column:
                QMessageBox.warning(self, 'Warning', "At least one column needs to be selected.", QMessageBox.Cancel)
                return

            if self.label_data.get_sensor_id() is None:
                if self.sensor_data.sensor_id is None:
                    raise Exception('self.sensor_id is None')

                self.label_data.set_sensor_id(self.sensor_data.sensor_id)

            # show a window to tell the user that the classifier is running
            working_msg = QDialog()
            working_msg.setWindowTitle("Loading...")
            working_msg.resize(200, 0)
            working_msg.open()

            # run the classifier
            self.ml_dataframe = self.sensor_data.data.__copy__()
            self.ml_dataframe.add_timestamp_column(TIME_COL, TIMESTAMP_COL)
            labels = self.plot.label_storage.get_labels_date(self.sensor_data.sensor_id,
                                                             self.sensor_data.datetime.date())
            self.ml_dataframe.add_labels(labels, LABEL_COL, TIMESTAMP_COL)
            raw_data = self.ml_dataframe.get_data()

            # Remove data points where label is unknown
            raw_data = raw_data[raw_data[LABEL_COL] != 'unknown']

            self.ml_dataframe = wd.windowing(raw_data, self.ml_used_columns, LABEL_COL, TIMESTAMP_COL, **funcs)
            self.ml_classifier.set_df(self.ml_dataframe)
            self.ml_classifier.set_features(features)
            res = self.ml_classifier.classify()

            # close the info window
            working_msg.close()

            self.video.play()

            for prediction in make_predictions(res):
                label, start_dt, end_dt = prediction['label'], datetime.fromisoformat(prediction['begin']), \
                                          datetime.fromisoformat(prediction['end'])
                # convert datetime times to time in seconds, which is used on the x-axis of the data-plot
                start = (start_dt - self.sensor_data.datetime).total_seconds()
                end = (end_dt - self.sensor_data.datetime).total_seconds()

                # add highlight to data-plot and play video in a loop
                span, text = self.add_suggestion_highlight(start, end, label)
                self.loop = (int((start + self.doubleSpinBox_video_offset.value()) * 1000),
                             int((end + self.doubleSpinBox_video_offset.value()) * 1000))
                if not self.mediaPlayer.media().isNull():
                    # if a video is opened set video position to start of the suggested label
                    self.mediaPlayer.setPosition(self.loop[0])
                else:
                    # no video; stop updating-timer and move plot to start of the suggested label
                    self.timer.stop()
                    self.plot.update_plot_axis(position=start + self.doubleSpinBox_video_offset.value())

                # ask user to accept or reject the suggested label
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Question)
                msg.setWindowTitle("Label suggestion")
                msg.setText("The classifier suggests the following label:")
                msg.setInformativeText("Label: {}\nLabel start: {}\nLabel end: {}\n\n"
                                       "Do you want to accept this suggestion?"
                                       .format(label, self.ms_to_hms(int(start * 1000)),
                                               self.ms_to_hms(int(end * 1000))))
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                stop_button = msg.addButton("Stop suggestions", QMessageBox.ActionRole)
                response = msg.exec_()

                # user has given a response, stop the loop and remove highlight
                self.loop = None
                span.remove()
                text.remove()

                # user clicked the "Stop suggestions" button
                if msg.clickedButton() == stop_button:
                    break

                # user accepted the current suggestion, add it to the database and make a new highlight
                if response == QMessageBox.Yes:
                    self.plot.label_storage.add_label(start_dt, end_dt, label, self.sensor_data.sensor_id)
                    self.add_label_highlight(start, end, label)
                    self.canvas.draw()

            # reset the video-player and data-plot to the original position and pause the video
            if not self.mediaPlayer.media().isNull():
                self.mediaPlayer.setPosition(original_position)
            else:
                # no video was playing, restart the updating-timer
                self.timer.start(25)

            self.plot.update_plot_axis(position=original_position / 1000)
            self.video.pause()


def add_seconds_to_datetime(date_time: datetime, seconds: float):
    """
    Returns a datetime object after adding the specified number of seconds to it.

    :param date_time: The datetime object
    :param seconds: The number of seconds to add
    :return: A datetime object with the number of seconds added to it
    """
    return date_time + timedelta(seconds=seconds)
