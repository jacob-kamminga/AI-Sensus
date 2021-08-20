import json
import sys
from datetime import datetime
from datetime import timedelta
from os import getenv
from pathlib import Path
from typing import Optional

import matplotlib.animation
import matplotlib.pyplot as plt
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QShortcut, QFileDialog, qApp, QDialog
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
import numpy as np
from pandas.plotting import register_matplotlib_converters
from sklearn.naive_bayes import GaussianNB

from constants import PREVIOUS_PROJECT_DIR, PROJECTS, PROJECT_NAME, PROJECT_DIR, APP_CONFIG_FILE, PROJECT_CONFIG_FILE
from data_export import windowing as wd
from database.models import Offset, LabelType
from gui.designer.gui import Ui_MainWindow
from gui.dialogs.export_dialog import ExportDialog
from gui.dialogs.label_dialog import LabelDialog
from gui.dialogs.label_settings_dialog import LabelSettingsDialog
from gui.dialogs.machine_learning_dialog import MachineLearningDialog
from gui.dialogs.new_project_dialog import NewProjectDialog
from gui.dialogs.project_settings_dialog import ProjectSettingsDialog
from gui.dialogs.select_camera_dialog import SelectCameraDialog
from gui.dialogs.select_sensor_dialog import SelectSensorDialog
from gui.dialogs.sensor_model_dialog import SensorModelDialog
from gui.dialogs.sensor_usage_dialog import SensorUsageDialog
from gui.dialogs.subject_dialog import SubjectDialog
from gui.dialogs.visual_analysis_dialog import VisualAnalysisDialog
from gui.dialogs.welcome_dialog import WelcomeDialog
from controllers.camera_controller import CameraController
from controllers.plot_controller import PlotController
from controllers.sensor_controller import SensorController
from controllers.video_controller import VideoController
from controllers.project_controller import ProjectController
from controllers.annotation_controller import AnnotationController
from controllers.app_controller import AppController
from machine_learning.classifier import Classifier, make_predictions

COL_LABEL = 'Label'
COL_TIME = 'Time'
COL_TIMESTAMP = 'Timestamp'


class GUI(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Error handling
        # To avoid creating multiple error boxes
        self.err_box = None

        self.app_controller = AppController(self)

        self.project_controller = ProjectController(self)
        if self.app_controller.prev_project_dir is not None:
           self.project_controller.load(self.app_controller.prev_project_dir, new_project=False)

        # update_db_structure(self.settings)  # function of self.settings has been moved to project_controller

    def init_project(self):
        # GUI components
        register_matplotlib_converters()

        self.video_controller = VideoController(self)
        self.sensor_controller = SensorController(self)
        self.plot_controller = PlotController(self)
        self.camera_controller = CameraController(self)
        self.annotation_controller = AnnotationController(self)

        # Create video key shortcuts
        self.shortcut_plus_10s = QShortcut(Qt.Key_Right, self)
        self.shortcut_minus_10s = QShortcut(Qt.Key_Left, self)
        self.shortcut_pause = QShortcut(Qt.Key_Space, self)
        # Variables for label shortcuts
        self.current_key_pressed = None

        # Connect all the buttons, spin boxes, combo boxes and line edits to their appropriate helper functions.
        self.pushButton_play.clicked.connect(self.video_controller.toggle_play)
        self.pushButton_mute.clicked.connect(self.video_controller.toggle_mute)
        self.shortcut_pause.activated.connect(self.video_controller.toggle_play)
        self.shortcut_plus_10s.activated.connect(self.video_controller.fast_forward_10s)
        self.shortcut_minus_10s.activated.connect(self.video_controller.rewind_10s)
        self.actionOpen_Project.triggered.connect(self.open_existing_project_dialog)
        self.actionNew_Project.triggered.connect(self.open_new_project_dialog)
        self.actionOpen_Video.triggered.connect(self.video_controller.prompt_file)
        self.actionOpen_Sensor_Data.triggered.connect(self.sensor_controller.prompt_file)
        self.pushButton_delete_formula.clicked.connect(self.plot_controller.delete_formula)

        self.actionCamera_Settings.triggered.connect(self.open_select_camera_dialog)
        self.actionLabel_Settings.triggered.connect(self.open_label_settings_dialog)
        self.actionSensors.triggered.connect(self.open_select_sensor_dialog)
        self.actionVIsual_Inspection.triggered.connect(self.open_visual_inspection_dialog)

        self.actionSensor_models.triggered.connect(self.open_sensor_model_dialog)
        self.actionSubjects.triggered.connect(self.open_subject_dialog)
        self.actionSubject_Mapping.triggered.connect(self.open_sensor_usage_dialog)
        self.actionProject_Settings.triggered.connect(self.open_project_settings_dialog)
        self.actionExit.triggered.connect(qApp.quit)

        self.lineEdit_function_regex.returnPressed.connect(self.plot_controller.new_plot)
        self.doubleSpinBox_video_offset.valueChanged.connect(self.sensor_controller.change_offset)
        self.doubleSpinBox_video_offset.setMaximum(43200)  # 12 hours range
        self.doubleSpinBox_video_offset.setMinimum(-43200)
        self.doubleSpinBox_speed.valueChanged.connect(self.video_controller.change_speed)
        self.doubleSpinBox_plot_width.valueChanged.connect(self.plot_controller.change_plot_width)
        self.doubleSpinBox_plot_height.valueChanged.connect(self.plot_controller.change_plot_height)
        self.comboBox_functions.activated.connect(self.plot_controller.change_plot)
        self.actionExport_Sensor_Data.triggered.connect(self.open_export)
        # self.actionMachine_Learning.triggered.connect(self.open_machine_learning_dialog)

        # Initialize the libraries that are needed to plot the sensor data, and add them to the GUI
        self.figure = matplotlib.pyplot.figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.resize(self.canvas.width(), 200)
        self.verticalLayout_plot.addWidget(self.canvas)
        self.canvas.mpl_connect('button_press_event', self.plot_controller.onclick)
        self.canvas.mpl_connect('button_release_event', self.plot_controller.onrelease)

        # Connect the QMediaPlayer to the right widget
        # self.videoWidget_player.mediaPlayer = QtWidgetsQmediaPlayer()
        self.mediaPlayer.setVideoOutput(self.videoWidget_player)

        # Connect some events that QMediaPlayer generates to their appropriate helper functions
        self.mediaPlayer.positionChanged.connect(self.video_controller.position_changed)
        self.mediaPlayer.durationChanged.connect(self.video_controller.duration_changed)

        # Connect the usage of the slider to its appropriate helper function
        self.horizontalSlider_time.sliderMoved.connect(self.video_controller.set_position)
        self.horizontalSlider_time.setEnabled(False)

        # Initialize a timer that makes sure that the sensor data plays smoothly
        self.timer = QtCore.QTimer(self)

        # Variable that stores start and stop time of a loop that the video-player should play
        self.loop = None

        # Load the stored width that the data-plot should have
        self.doubleSpinBox_plot_width.setValue(self.plot_controller.plot_width)
        self.doubleSpinBox_plot_height.setValue(self.plot_controller.plot_height_factor)

        # Machine learning fields
        self.ml_dataframe = None
        self.ml_classifier_engine = GaussianNB()
        self.ml_used_columns = []
        self.ml_classifier = Classifier(self.ml_classifier_engine)

        # Open the last opened files
        self.video_controller.open_previous_file()
        self.sensor_controller.open_previous_file()

        project_name = self.project_controller.get_setting('project_name')
        self.label_project_name_value.setText(project_name)
        self.setWindowTitle("AI Sensus - " + project_name)


    def std_err_post(self, msg):
        """
        This method receives stderr text strings as a pyqtSlot.
        """
        if self.err_box is None:
            self.err_box = QMessageBox()
            # Both OK and window delete fire the 'finished' signal
            self.err_box.finished.connect(self.clear_err_box)

        # A single error is sent as a string of separate stderr .write() messages,
        # so concatenate them.
        self.err_box.setText(self.err_box.text() + msg)

        # .show() is used here because .exec() or .exec_() create multiple
        # MessageBoxes.
        self.err_box.show()

    def clear_err_box(self):
        # QMessageBox doesn't seem to be actually destroyed when closed, just hidden.
        # This is true even if destroy() is called or if the Qt.WA_DeleteOnClose
        # attribute is set.  Clear text for next time.
        self.err_box.setText('')

    def show_welcome_dialog(self):
        """"
        Open the welcome dialog. The welcome dialog first checks if a project was already used during previous session.
        """
        while self.project_controller.project_dir is None:  # Config was just created, so no previous project was found.
            welcome_dialog = WelcomeDialog(self)  # pass self to access new and open project dialogs
            welcome_dialog.exec()

    def open_new_project_dialog(self):
        """
        Open the new project name dialog.
        """
        new_project_dialog = NewProjectDialog()
        new_project_dialog.exec()
        self.project_controller.create_new_project(new_project_dialog.project_name)

        # Reset video and sensordata
        self.reset_gui_components()

        dialog = ProjectSettingsDialog(self)
        dialog.exec()

    def open_existing_project_dialog(self):
        """
        Open dialog for selecting an existing project.

        """
        if self.project_controller.project_dir is not None:
            old_dir = str(self.project_controller.project_dir)
        else:
            old_dir = ""

        project_exists = False
        while not project_exists:
            project_dir = QFileDialog.getExistingDirectory(
                self,
                "Select existing project directory...",
                old_dir,
                options=QFileDialog.ShowDirsOnly
            )

            if project_dir != '':
                config_file_dir = Path(project_dir).joinpath(PROJECT_CONFIG_FILE)

                if not config_file_dir.is_file():
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Not a project folder")
                    msg.setText("The selected directory is not an existing project. If you want to use the files in this "
                                "folder please create a new project an load the files in.")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec()
                else:
                    project_exists = True
            else:  # Pressed Cancel.
                return

        self.project_controller.open_existing_project(project_dir)
        self.reset_gui_components()

    def reset_gui_components(self):
        """
        When opening an existing or starting a new project, the GUI components need to be reset. This may also be
        required after the timezone settings change.
        """
        self.mediaPlayer.setMedia(QMediaContent())

        self.label_project_name_value.clear()
        self.label_video_date_value.clear()
        self.label_video_time_value.clear()
        self.label_camera_name_value.clear()
        self.label_active_label_value.clear()
        self.comboBox_functions.clear()
        self.label_current_function_value.clear()
        self.label_video_filename.clear()
        self.label_sensor_data_filename.clear()

        if hasattr(self, 'camera_controller'):
            self.camera_controller.__init__(self)
        else:
            self.camera_controller = None

        if hasattr(self, 'figure'):
            self.figure.clear()
            self.canvas.draw()

        if hasattr(self, 'plot_controller'):
            # self.plot.reset()
            self.plot_controller.__init__(self)
        else:
            self.plot_controller = None

        if hasattr(self, 'video_controller'):
            self.video_controller.__init__(self)
            self.video_controller.open_previous_file()

        else:
            self.video_controller = None

        if hasattr(self, 'sensor_controller'):
            self.sensor_controller.__init__(self)
            self.sensor_controller.open_previous_file()
            self.update_camera_sensor_offset()
        else:
            self.sensor_controller = None

        project_name = self.project_controller.get_setting('project_name')
        self.label_project_name_value.setText(project_name)
        self.setWindowTitle("AI Sensus - " + project_name)

    def update_camera_sensor_offset(self):
        if self.sensor_controller is not None \
                and self.sensor_controller.sensor_data_file is not None \
                and self.camera_controller.camera is not None:
            try:
                # TODO: When sensor model is not loaded properly, self.sensor_controller.sensor_data_file.datetime is a datetime STRING, not a datetime object.
                offset = Offset.get(Offset.camera == self.camera_controller.camera.id,
                                    Offset.sensor == self.sensor_controller.sensor_data_file.sensor,
                                    Offset.added == self.sensor_controller.sensor_data_file.datetime.date())
                self.doubleSpinBox_video_offset.setValue(offset.offset)
            except Offset.DoesNotExist:
                pass

    def open_label_dialog(self):
        """
        Opens the label dialog window.
        """
        if not self.sensor_controller.sensor_data:
            QMessageBox.Warning(self, "No sensor data found", "You need to import sensor data first.")
        else:
            dialog = LabelDialog(self.sensor_controller.sensor_data_file.id,
                                 self.sensor_controller.sensor_data.metadata.sensor_timezone)
            dialog.exec()

            if dialog.is_accepted:
                self.add_label_highlight(dialog.label.start, dialog.label.end, dialog.label.label)

    def open_select_camera_dialog(self):
        """
        Opens the select camera dialog window.
        """
        dialog = SelectCameraDialog(self)
        if self.video_controller.file_name is not None:
            dialog.setWindowTitle(self.video_controller.file_name)

        dialog.exec()

        current_camera = self.camera_controller.camera
        if current_camera is not None:
            if self.video_controller.file_name is not None:
                self.video_controller.update_camera(current_camera.id)
            self.camera_controller.change_camera(current_camera.id)

    def open_label_settings_dialog(self):
        """
        Opens the label settings_dict dialog window.
        """
        dialog = LabelSettingsDialog(self)
        dialog.exec()

        # Upon window close
        if dialog.settings_changed:
            self.plot_controller.draw_graph()

    def open_subject_dialog(self):
        """
        Open the subject mapping dialog window.
        """
        dialog = SubjectDialog(self.annotation_controller)
        dialog.exec()

    def open_select_sensor_dialog(self):
        """
        Open the select sensor dialog window.
        """
        if self.sensor_controller is not None and self.sensor_controller.file_name is not None:
            dialog = SelectSensorDialog(self.sensor_controller)
            dialog.setWindowTitle(self.sensor_controller.file_name)
            dialog.exec()

            if dialog.selected_sensor_id is not None:
                self.sensor_controller.update_sensor(dialog.selected_sensor_id)


    def open_sensor_model_dialog(self):
        """
        Open the sensor model dialog.
        """
        dialog = SensorModelDialog(self.sensor_controller)
        dialog.exec()

    def open_sensor_usage_dialog(self):
        dialog = SensorUsageDialog(self.project_controller, self.sensor_controller)
        dialog.exec()

    def open_export(self):
        """
        Open the export dialog window, and if a subject and a file location and name are chosen, export the data
        accordingly.
        """
        dialog = ExportDialog(self)
        dialog.exec()

    def open_project_settings_dialog(self):
        dialog = ProjectSettingsDialog(self)
        dialog.exec()
        if dialog.timezone_changed:
            self.reset_gui_components()

    def open_visual_inspection_dialog(self):
        """
        Plot all sensor data per subject per activity for visual inspection of annotated data.
        :return:
        """
        if self.sensor_controller is not None:
            file_date = self.sensor_controller.utc_dt
        else:
            file_date = None

        dialog = VisualAnalysisDialog(
            self.project_controller,
            file_date
        )
        dialog.exec()

    def keyPressEvent(self, event) -> None:
        self.current_key_pressed = event.text()
        try:
            if hasattr(self, 'plot_controller'):
                self.label_active_label_value.setText(
                    LabelType.get(LabelType.keyboard_shortcut == self.current_key_pressed).activity)
        except:
            pass

    def keyReleaseEvent(self, event):
        self.current_key_pressed = None
        self.label_active_label_value.clear()

    def temp_debug_set_position(self, position):
        self.label_active_label.setText(str(position))
        self.label_active_label_value.setText(str(self.mediaPlayer.position()))

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
            # Save current position in the video
            original_position = self.mediaPlayer.position()

            at_least_1_column = False
            # For each selected column, add new column names to the lists for machine learning
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

            # Show a window to tell the user that the classifier is running
            working_msg = QDialog()
            working_msg.setWindowTitle("Loading...")
            working_msg.resize(200, 0)
            working_msg.open()

            # Run the classifier
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

            # Close the info window
            working_msg.close()

            self.video.play()

            for prediction in make_predictions(res):
                label, start_dt, end_dt = prediction['label'], datetime.fromisoformat(prediction['begin']), \
                                          datetime.fromisoformat(prediction['end'])
                # Convert datetime times to time in seconds, which is used on the x-axis of the data-plot
                start = (start_dt - self.sensor_data_file.utc_dt).total_seconds()
                end = (end_dt - self.sensor_data_file.utc_dt).total_seconds()

                # Add highlight to data-plot and play video in a loop
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

                # Ask user to accept or reject the suggested label
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
    # Unused?
    """
    Returns a datetime object after adding the specified number of seconds to it.

    :param date_time: The datetime object
    :param seconds: The number of seconds to add
    :return: A datetime object with the number of seconds added to it
    """
    return date_time + timedelta(seconds=seconds)
