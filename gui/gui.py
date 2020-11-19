import json
import sqlite3
import sys
from datetime import datetime
from datetime import timedelta
from os import getenv
from typing import Optional

import matplotlib.animation
import matplotlib.pyplot as plt
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QShortcut, QDialog, QFileDialog, qApp
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from pandas.plotting import register_matplotlib_converters
from sklearn.naive_bayes import GaussianNB
from pathlib import Path
from data_export import windowing as wd
from database.offset_manager import OffsetManager
from database.sensor_usage_manager import SensorUsageManager
from database.create_database import create_database
from gui.designer.gui import Ui_MainWindow
from gui.dialogs.export import ExportDialog
from gui.dialogs.label import LabelSpecs
from gui.dialogs.label_settings import LabelSettingsDialog
from gui.dialogs.machine_learning import MachineLearningDialog
from gui.dialogs.select_camera import SelectCameraDialog
from gui.dialogs.select_sensor import SelectSensorDialog
from gui.dialogs.sensor import SensorDialog
from gui.dialogs.sensor_model import SensorModelDialog
from gui.dialogs.subject import SubjectDialog
from gui.dialogs.subject_sensor_map import SubjectSensorMapDialog
from gui.dialogs.welcome import Welcome
from gui.dialogs.new_project import NewProject
from gui_components.camera import Camera
from gui_components.plot import Plot
from gui_components.sensor_data_file import SensorDataFile
from gui_components.video import Video
from machine_learning.classifier import Classifier, make_predictions
from gui.dialogs.project_settings import ProjectSettingsDialog

from constants import PREVIOUS_PROJECT_DIR, PROJECTS, PROJECT_NAME, PROJECT_DIR, PROJECT_DATABASE_FILE, APP_CONFIG_FILE

COL_LABEL = 'Label'
COL_TIME = 'Time'
COL_TIMESTAMP = 'Timestamp'


def user_data_dir(file_name):
    r"""
    Get OS specific data directory path for LabelingApp.
    Typical user data directories are:
        macOS:    ~/Library/Application Support/LabelingApp
        Unix:     ~/.local/share/LabelingApp   # or in $XDG_DATA_HOME, if defined
        Win 10:   C:\Users\<username>\AppData\Roaming\LabelingApp
    For Unix, we follow the XDG spec and support $XDG_DATA_HOME if defined.
    :param file_name: file to be fetched from the data dir
    :return: full path to the user-specific data dir
    """
    # get os specific path
    if sys.platform.startswith("win"):
        os_path = getenv("APPDATA")
    elif sys.platform.startswith("darwin"):
        os_path = "~/Library/Application Support"
    else:
        # linux
        os_path = getenv("XDG_DATA_HOME", "~/.local/share")

    # join with LabelingApp dir
    path = Path(os_path) / "LabelingApp"

    return path.expanduser() / file_name


class GUI(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        register_matplotlib_converters()

        # Error handling
        # To avoid creating multiple error boxes
        self.err_box = None

        self.settings: Optional[ProjectSettingsDialog] = None

        self.app_config_file = user_data_dir(APP_CONFIG_FILE)
        self.app_config = {}
        self.show_welcome_dialog()

        # GUI components
        self.video = Video(self)
        self.sensor_data_file = SensorDataFile(self)
        self.plot = Plot(self)
        self.camera = Camera(self)

        # Create video key shortcuts
        self.shortcut_plus_10s = QShortcut(Qt.Key_Right, self)
        self.shortcut_minus_10s = QShortcut(Qt.Key_Left, self)
        self.shortcut_pause = QShortcut(Qt.Key_Space, self)

        # Connect all the buttons, spin boxes, combo boxes and line edits to their appropriate helper functions.
        self.pushButton_play.clicked.connect(self.video.toggle_play)
        self.pushButton_mute.clicked.connect(self.video.toggle_mute)
        self.shortcut_pause.activated.connect(self.video.toggle_play)
        self.shortcut_plus_10s.activated.connect(self.video.fast_forward_10s)
        self.shortcut_minus_10s.activated.connect(self.video.rewind_10s)
        self.actionOpen_Project.triggered.connect(self.open_existing_project_dialog)
        self.actionNew_Project.triggered.connect(self.open_new_project_dialog)
        self.actionOpen_Video.triggered.connect(self.video.prompt_file)
        self.actionOpen_Sensor_Data.triggered.connect(self.sensor_data_file.prompt_file)
        self.pushButton_delete_formula.clicked.connect(self.plot.delete_formula)

        self.actionCamera_Settings.triggered.connect(self.open_select_camera_dialog)
        self.actionLabel_Settings.triggered.connect(self.open_label_settings_dialog)
        # self.actionSensors.triggered.connect(self.open_sensor_dialog)
        self.actionSensors.triggered.connect(self.open_select_sensor_dialog)

        self.actionSensor_models.triggered.connect(self.open_sensor_model_dialog)
        self.actionSubjects.triggered.connect(self.open_subject_dialog)
        self.actionSubject_Mapping.triggered.connect(self.open_subject_sensor_map_dialog)
        self.actionProject_Settings.triggered.connect(self.open_project_settings_dialog)
        self.actionExit.triggered.connect(qApp.quit)

        self.lineEdit_function_regex.returnPressed.connect(self.plot.new_plot)
        self.doubleSpinBox_video_offset.valueChanged.connect(self.change_offset)
        self.doubleSpinBox_video_offset.setMaximum(43200)  # 12 hours range
        self.doubleSpinBox_video_offset.setMinimum(-43200)
        self.doubleSpinBox_speed.valueChanged.connect(self.video.change_speed)
        self.doubleSpinBox_plot_width.valueChanged.connect(self.plot.change_plot_width)
        self.doubleSpinBox_plot_height.valueChanged.connect(self.plot.change_plot_height)
        self.comboBox_functions.activated.connect(self.plot.change_plot)
        self.actionExport_Sensor_Data.triggered.connect(self.open_export)
        self.actionMachine_Learning.triggered.connect(self.open_machine_learning_dialog)

        # Initialize the libraries that are needed to plot the sensor data, and add them to the GUI
        self.figure = matplotlib.pyplot.figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.resize(self.canvas.width(), 200)
        self.verticalLayout_plot.addWidget(self.canvas)
        self.canvas.mpl_connect('button_press_event', self.plot.onclick)
        self.canvas.mpl_connect('button_release_event', self.plot.onrelease)

        # Connect the QMediaPlayer to the right widget
        # self.videoWidget_player.mediaPlayer = QtWidgetsQmediaPlayer()
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
        self.subject_mapping = SensorUsageManager(self.settings)

        # Machine learning fields
        self.ml_dataframe = None
        self.ml_classifier_engine = GaussianNB()
        self.ml_used_columns = []
        self.ml_classifier = Classifier(self.ml_classifier_engine)

        # Manager for offset DB operations
        self.offset_manager = OffsetManager(self.settings)

        # Open the last opened files
        self.video.open_previous_file()
        self.sensor_data_file.open_previous_file()


        self.label_project_name_value.setText(self.settings.get_setting('project_name'))

    def std_err_post(self, msg):
        """
        This method receives stderr text strings as a pyqtSlot.
        """
        if self.err_box is None:
            self.err_box = QMessageBox()
            # Both OK and window delete fire the 'finished' signal
            self.err_box.finished.connect(self.clear)
        # A single error is sent as a string of separate stderr .write() messages,
        # so concatenate them.
        self.err_box.setText(self.err_box.text() + msg)
        # .show() is used here because .exec() or .exec_() create multiple
        # MessageBoxes.
        self.err_box.show()

    def clear(self):
        # QMessageBox doesn't seem to be actually destroyed when closed, just hidden.
        # This is true even if destroy() is called or if the Qt.WA_DeleteOnClose
        # attribute is set.  Clear text for next time.
        self.err_box.setText('')

    def show_welcome_dialog(self):
        """"
        Open the welcome dialog. The welcome dialog first checks if a project was already used during previous session.
        """
        dialog = Welcome(self)  # pass self to access new and open project dialogs

        if dialog.settings is None:
            dialog.exec()

        if self.settings is None and dialog.settings:  # A project was used during previous session
            self.settings = dialog.settings
        if self.settings is None:  # error, this should not happen
            exit(0)

    def open_new_project_dialog(self):
        """
        Open the new project name dialog.
        """
        new_project_dialog = NewProject()
        new_project_dialog.exec()
        project_name = new_project_dialog.project_name

        if project_name:
            project_dir = QFileDialog.getExistingDirectory(
                self,
                "Select new project directory... A folder will be created",
                options=QFileDialog.ShowDirsOnly
            )

            if project_dir:
                # Add project name to project directory
                project_dir = Path(project_dir).joinpath(project_name)

                self.settings = ProjectSettingsDialog(project_dir)
                self.settings.set_setting('project_name', project_name)

                self.settings.exec()

                # Create database
                try:
                    conn = sqlite3.connect(project_dir.joinpath(PROJECT_DATABASE_FILE).as_posix())
                    create_database(conn)
                except sqlite3.Error as e:
                    print(e)

                # Reset video and sensordata
                self.reset_gui_components()

                # Save project in app config
                self.app_config.setdefault(PROJECTS, []).append({
                    PROJECT_NAME: project_name,
                    PROJECT_DIR: str(project_dir)
                })
                self.app_config[PREVIOUS_PROJECT_DIR] = str(project_dir)
                self.save_app_config()

    def save_app_config(self):
        with self.app_config_file.open('w') as f:
            json.dump(self.app_config, f)

    def open_existing_project_dialog(self):
        """
        Open dialog for selecting an existing project.

        """
        if self.settings is not None:
            old_dir = str(self.settings.project_dir)
        else:
            old_dir = ""

        project_dir = QFileDialog.getExistingDirectory(
            self,
            "Select existing project directory...",
            old_dir,
            options=QFileDialog.ShowDirsOnly
        )

        if project_dir:
            self.settings = ProjectSettingsDialog(Path(project_dir))
            # Reset gui components
            self.reset_gui_components()
            # Set project dir as most recent project dir
            self.app_config[PREVIOUS_PROJECT_DIR] = project_dir
            self.save_app_config()

            # self.close()

    def reset_gui_components(self):
        """
        When opening an existing or starting a new project, the gui components need to be reset to the new project
        to connect the correct DB's
        :return:
        """

        self.mediaPlayer.setMedia(QMediaContent())

        if hasattr(self, 'camera'):
            self.camera.__init__(self)
        else:
            self.camera = None

        if hasattr(self, 'plot'):
            # self.plot.reset()
            self.plot.__init__(self)
        else:
            self.plot = None

        if hasattr(self, 'video'):
            self.video.__init__(self)
            self.video.open_previous_file()

        else:
            self.video = None

        if hasattr(self, 'sensor_data_file'):
            self.sensor_data_file.__init__(self)
            self.sensor_data_file.open_previous_file()
        else:
            self.sensor_data_file = None

        self.label_project_name_value.setText(self.settings.get_setting('project_name'))
        #  TODO: Reset dataplot, labels, spinboxes...

    def change_offset(self, offset: float):
        """
        Updates the offset in the database.
        """
        date = self.sensor_data_file.utc_dt.date()

        if self.sensor_data_file.sensor_id is not None:
            self.offset_manager.set_offset(self.camera.camera_id,
                                           self.sensor_data_file.sensor_id,
                                           offset,
                                           date)

    def update_camera_sensor_offset(self):
        if self.sensor_data_file.sensor_id is not None and self.camera.camera_id is not None:
            offset = self.offset_manager.get_offset(self.camera.camera_id,
                                                    self.sensor_data_file.sensor_id,
                                                    self.sensor_data_file.utc_dt.date())

            self.doubleSpinBox_video_offset.setValue(offset)

    def open_label_dialog(self):
        """
        Opens the label dialog window.
        """
        if not self.sensor_data_file.sensor_data:
            QMessageBox.information(self, "Warning", "You need to import sensor data first.", QMessageBox.Ok)
        else:
            dialog = LabelSpecs(self.sensor_data_file.id_,
                                self.plot.label_manager,
                                self.plot.label_type_manager)
            dialog.exec()
            dialog.show()

            if dialog.is_accepted:
                self.add_label_highlight(dialog.selected_label.start,
                                         dialog.selected_label.end,
                                         dialog.selected_label.label)

    def open_select_camera_dialog(self):
        """
        Opens the select camera dialog window.
        """
        dialog = SelectCameraDialog(self)
        if self.video.file_name is not None:
            dialog.setWindowTitle(self.video.file_name)

        dialog.exec()
        dialog.show()

        if dialog.selected_camera_id is not None:
            self.video.update_camera(dialog.selected_camera_id)
            self.camera.change_camera(dialog.selected_camera_id)

    def open_label_settings_dialog(self):
        """
        Opens the label settings_dict dialog window.
        """
        dialog = LabelSettingsDialog(
            self.plot.label_type_manager,
            self.settings
        )
        dialog.exec()
        dialog.show()

        # Upon window close
        if dialog.settings_changed:
            self.plot.draw_graph()

    def open_subject_dialog(self):
        """
        Open the subject mapping dialog window.
        """
        dialog = SubjectDialog(self.settings)
        dialog.exec()
        dialog.show()

    def open_sensor_dialog(self):
        """
        Open the sensor dialog window.
        """
        dialog = SensorDialog(self.settings)
        dialog.exec()
        dialog.show()

    def open_select_sensor_dialog(self, model_id=None):
        """
        Open the select sensor dialog window.
        """
        dialog = SelectSensorDialog(self, model_id)
        if self.sensor_data_file.file_name is not None:
            dialog.setWindowTitle(self.sensor_data_file.file_name)

        dialog.exec()
        dialog.show()

        if dialog.selected_sensor_id is not None:
            self.sensor_data_file.update_sensor(dialog.selected_sensor_id)
            return dialog.selected_sensor_name
        else:
            return None

    def open_sensor_model_dialog(self):
        """
        Open the sensor model dialog.
        """
        dialog = SensorModelDialog(self.settings)
        dialog.exec()
        dialog.show()

    def open_subject_sensor_map_dialog(self):
        dialog = SubjectSensorMapDialog(self.settings)
        dialog.exec()
        dialog.show()

    def open_export(self):
        """
        Open the export dialog window, and if a subject and a file location and name are chosen, export the data
        accordingly.
        """
        dialog = ExportDialog(
            self.settings,
            self.sensor_data_file.utc_dt
        )
        dialog.exec()
        dialog.show()

    def open_project_settings_dialog(self):
        if self.app_config.get(PREVIOUS_PROJECT_DIR):
            prev_project_dir = Path(self.app_config.get(PREVIOUS_PROJECT_DIR))

            # Check if previous project directory exists
            if prev_project_dir.is_dir():
                self.settings = ProjectSettingsDialog(prev_project_dir)
                self.settings.exec()
                if self.settings.settings_changed:
                    self.reset_gui_components()

    def open_machine_learning_dialog(self):
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
                if self.sensor_data_file.sensor_id is None:
                    raise Exception('self.sensor_id is None')

                self.label_data.set_sensor_id(self.sensor_data_file.sensor_id)

            # show a window to tell the user that the classifier is running
            working_msg = QDialog()
            working_msg.setWindowTitle("Loading...")
            working_msg.resize(200, 0)
            working_msg.open()

            # run the classifier
            self.ml_dataframe = self.sensor_data_file.sensor_data.__copy__()
            self.ml_dataframe.add_timestamp_column(COL_TIME, COL_TIMESTAMP)
            labels = self.plot.label_manager.get_labels_by_file_and_date(self.sensor_data_file.sensor_id,
                                                                         self.sensor_data_file.utc_dt.date())
            self.ml_dataframe.add_labels_ml(labels, COL_LABEL, COL_TIMESTAMP)
            raw_data = self.ml_dataframe.get_data()

            # Remove data points where label is unknown
            raw_data = raw_data[raw_data[COL_LABEL] != 'unknown']

            self.ml_dataframe = wd.windowing(raw_data, self.ml_used_columns, COL_LABEL, COL_TIMESTAMP, **funcs)
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
                start = (start_dt - self.sensor_data_file.utc_dt).total_seconds()
                end = (end_dt - self.sensor_data_file.utc_dt).total_seconds()

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
                response = msg.exec()

                # user has given a response, stop the loop and remove highlight
                self.loop = None
                span.remove()
                text.remove()

                # user clicked the "Stop suggestions" button
                if msg.clickedButton() == stop_button:
                    break

                # user accepted the current suggestion, add it to the database and make a new highlight
                if response == QMessageBox.Yes:
                    self.plot.label_manager.add_label(start_dt, end_dt, label, self.sensor_data_file.sensor_id)
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
