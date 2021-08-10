import datetime as dt
import hashlib
import ntpath
import os
from pathlib import Path
from typing import Optional

# import PyQt5
import pandas as pd
import pytz
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from peewee import DoesNotExist, JOIN

from constants import PREVIOUS_SENSOR_DATA_FILE
from data_import.sensor_data import SensorData
from database.models import SensorDataFile, SensorModel, Sensor, Camera, Offset, Subject, SensorUsage, Label, LabelType
from gui.dialogs.edit_sensor_dialog import EditSensorDialog
from gui.dialogs.export_progress_dialog import ExportProgressDialog
from gui.dialogs.project_settings_dialog import ProjectSettingsDialog
from gui.dialogs.sensor_model_dialog import SensorModelDialog


class SensorController:
    """
    Contains methods for manipulating sensor data.
    """

    def __init__(self, gui):
        self.gui = gui
        self.file_path: Optional[Path] = None
        self.project_controller = gui.project_controller
        self.file_name = None

        self.file_id_hash = None
        """" The hashed ID, used to recognize the file independent from location on disk """
        self.sensor_name: Optional[str] = None
        """ The name of the sensor associated with this sensor datafile"""
        self.sensor_data: Optional[SensorData] = None
        """ The data_import.SensorData object. """
        self.df: Optional[pd.DataFrame] = None
        """ The pandas DataFrame. """
        self.utc_dt: Optional[dt.datetime] = None
        """ The datetime of the sensor data. """
        self.model_id: Optional[int] = None
        """ The model ID. """
        self.sensor_data_file = None

    def open_previous_file(self):
        previous_path = self.project_controller.get_setting(PREVIOUS_SENSOR_DATA_FILE)

        if previous_path:
            previous_path = Path(previous_path)

            if previous_path.is_file():
                self.file_path = previous_path
                self.open_file()

                if hasattr(self.gui, 'video_controller') and self.gui.video_controller.project_dt is not None:
                    self.gui.video_controller.set_position(0)

    def prompt_file(self):
        """
        Opens a file dialog that lets the user select a file.
        """
        path = self.project_controller.get_setting(PREVIOUS_SENSOR_DATA_FILE)

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
        dialog = SensorModelDialog()
        dialog.exec()
        return dialog.selected_model_id

    def open_file(self):
        """
        Opens the file specified by self.file_path and sets the sensor data.
        """
        if self.file_path and self.file_path.is_file():
            # Store the selected file path in the configuration
            self.project_controller.set_setting(PREVIOUS_SENSOR_DATA_FILE, self.file_path.as_posix())

            self.file_name = ntpath.basename(self.file_path.as_posix())
            self.file_id_hash = self.create_file_id(self.file_path)

            # Get or create the sensor data file model instance
            self.sensor_data_file = SensorDataFile.get_or_create(
                file_id_hash=self.file_id_hash,
                defaults={
                    'file_name': self.file_name,
                    'file_path': self.file_path,
                    'sensor': -1,
                }
            )[0]

            if type(self.sensor_data_file.datetime) == str:
                self.sensor_data_file.datetime = dt.datetime.strptime(self.sensor_data_file.datetime,
                                                                      "%Y-%m-%d %H:%M:%S.%f%z")

            # Reset the dictionary that maps function names to functions
            self.gui.plot_controller.formula_dict = dict()

            # Retrieve the sensor model ID from the database
            try:
                sensor_model = (SensorModel
                                .select(SensorModel.id)
                                .join(Sensor, JOIN.LEFT_OUTER)
                                .where(SensorModel.id == self.sensor_data_file.sensor.id)
                                .get())
                sensor_model_id = sensor_model.id

            # If not found, open a dialog where the user can select the sensor model
            except DoesNotExist:
                msg = QMessageBox()
                msg.setWindowTitle("No sensor model selected")
                msg.setIcon(QMessageBox.Warning)
                msg.setText("While loading the (previously) selected sensor data file, no associated sensor model "
                            "was found. Sensor data file:\n"
                            f" {self.file_path}.\n\n"
                            "Do you want to create/select one now?")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msg.setEscapeButton(QMessageBox.No)
                msg.setDefaultButton(QMessageBox.Yes)

                return_val = msg.exec()
                if return_val == QMessageBox.Yes:
                    sensor_model_id = self.open_sensor_model_dialog()
                else:
                    return

            if sensor_model_id is None:
                return

            # Retrieve the SensorData object that parses the sensor data file
            self.sensor_data = SensorData(self.project_controller, self.file_path, sensor_model_id)
            # Try to load sensor name from either metadata or DB
            if self.sensor_data.metadata.sensor_name:
                sensor_name = self.sensor_data.metadata.sensor_name
            else:
                # Check if sensor data has been loaded before and name is known in DB
                try:
                    sensor_name = Sensor.get_by_id(self.sensor_data_file.sensor).name
                except DoesNotExist:
                    sensor_name = None
                    QMessageBox.warning(self.gui, "No associated sensor found",
                                        "There is currently no sensor associated with the sensor data file. "
                                        "Please select the sensor that should be associated with the "
                                        f"sensor data file \"{self.sensor_data_file.file_path}\"")

            # When sensor ID (name) cannot be parsed it has to be manually linked to datafile by user
            while sensor_name is None:
                self.gui.open_select_sensor_dialog()
                sensor_name = self.sensor_data_file.sensor.name
                # Verify that user indeed selected a sensor ID
                if sensor_name is None:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Warning")
                    msg.setText("A sensor ID must be selected")
                    msg.setInformativeText("The selected sensor model states that sensor identifier (ID) cannot "
                                           "be parsed from sensor datafile. Please select sensor ID manually.")
                    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                    response = msg.exec()
                    if response == QMessageBox.Cancel:
                        return

            sensor = Sensor.get_or_create(name=sensor_name, defaults={'model': sensor_model_id})[0]

            while sensor.timezone is None:
                # Prompt user for timezone of sensor
                dialog = EditSensorDialog(sensor)
                dialog.exec()

            self.sensor_data.metadata.sensor_timezone = pytz.timezone(sensor.timezone)

            self.sensor_data_file.sensor = sensor

            # Parse the sensor data from the file
            self.sensor_data.parse()

            # Retrieve the formulas that are associated with this sensor data file, and store them in the dictionary
            stored_formulas = self.project_controller.get_setting('formulas')

            for formula_name in stored_formulas:
                try:
                    self.sensor_data.add_column_from_func(formula_name, stored_formulas[formula_name])
                    self.gui.plot_controller.formula_dict[formula_name] = stored_formulas[formula_name]
                except Exception as e:
                    print(e)

            # Parse the utc datetime of the sensor data from metadata when possible
            # self.sensor_data.metadata.parse_datetime()
            # self.gui.setCursor(.WaitCursor)
            # Add absolute time column to dataframe
            if not self.sensor_data.add_abs_dt_col():
                return
            # Save the starting time of the sensor data in a DateTime object
            self.sensor_data_file.datetime = self.sensor_data.metadata.utc_dt.replace(tzinfo=None)

            # Retrieve the DataFrame with all the raw sensor data
            self.df = self.sensor_data.get_data()

            # Update file path in DB if it has changed
            if self.sensor_data_file.file_path != self.file_path.as_posix():
                self.sensor_data_file.file_path = self.file_path.as_posix()
                self.sensor_data_file.save()

            # self.gui.setCursor(QtGui.QCursor(0))
            self.init_functions()
            self.draw_graph()
            # self.update_camera_text()
            try:
                self.gui.label_sensor_data_filename.setText(
                    self.file_path.parts[-3] + "/" + self.file_path.parts[-2] + "/" + self.file_path.parts[-1]
                )
            except:
                pass
            self.gui.update_camera_sensor_offset()
            self.gui.video_controller.sync_with_sensor_data()

    def init_functions(self):
        # TODO: Move to plot_controller.py
        # Add every column in the DataFrame to the possible Data Series that can be plotted, except for time,
        # and plot the first one
        self.gui.comboBox_functions.clear()

        data_cols = self.df.columns.tolist()
        del data_cols[self.sensor_data.sensor_model.timestamp_column]

        for col in data_cols:
            self.gui.comboBox_functions.addItem(col)

        last_used_col = self.sensor_data_file.last_used_column

        if last_used_col and self.gui.plot_controller.set_current_plot(last_used_col):
            self.gui.comboBox_functions.setCurrentText(last_used_col)
        else:
            self.gui.plot_controller.set_current_plot(self.gui.comboBox_functions.currentText())

    def save_last_used_column(self, col_name):
        self.sensor_data_file.last_used_column = col_name
        self.sensor_data_file.save()

    def draw_graph(self):
        # TODO: Move to plot_controller.py

        # Reset the figure and add a new subplot to it
        self.gui.figure.clear()
        self.gui.plot_controller.data_plot = self.gui.figure.add_subplot(1, 1, 1)
        if self.gui.plot_controller.current_plot is None:
            QMessageBox.warning(self.gui, "No, or an incompatible, function selected",
                                "Cannot plot the function that is currently selected. "
                                "Please select a different function.")
            return
        self.gui.plot_controller.draw_graph()

        x_window_start = self.gui.plot_controller.x_min - (self.gui.plot_controller.plot_width / 2)
        x_window_end = self.gui.plot_controller.x_min + (self.gui.plot_controller.plot_width / 2)

        if self.project_controller.get_setting("plot_height_factor") is None:
            self.gui.plot_controller.plot_height_factor = 1.0
            self.project_controller.set_setting("plot_height_factor", self.gui.plot_controller.plot_height_factor)

        # Set the axis of the data plot
        self.gui.plot_controller.data_plot.axis([
            x_window_start,
            x_window_end,
            self.gui.plot_controller.y_min - (
                    (self.gui.plot_controller.plot_height_factor - 1) * self.gui.plot_controller.y_min),
            self.gui.plot_controller.y_max + (
                    (self.gui.plot_controller.plot_height_factor - 1) * self.gui.plot_controller.y_max)
        ])

        # Start the timer that makes the graph scroll smoothly
        self.gui.timer.timeout.connect(self.gui.plot_controller.update_plot_axis)
        self.gui.timer.start(25)

        # Draw the graph, set the value of the offset spinbox in the GUI to the correct value
        self.gui.canvas.draw()

    def update_camera_text(self):
        # TODO: MVC
        camera_name = self.gui.label_camera_name_value.text()

        if camera_name:
            offset = (Offset
                      .select(Offset.offset)
                      .join(Camera, Sensor)
                      .where((Camera.name == camera_name) &
                             (Sensor.id == self.sensor_data_file.sensor) &
                             (Offset.added == self.utc_dt.date())))

            self.gui.doubleSpinBox_video_offset.setValue(offset.offset)

    def update_sensor(self, sensor_id: int):
        if self.sensor_data_file is not None:
            self.sensor_data_file.sensor = sensor_id
            self.sensor_data_file.save()

    def create_file_id(self, file_path, block_size=256):
        # Function that takes a file and returns the first 10 characters of a hash of
        # 10 times block size in the middle of the file
        # Input: File path as string
        # Output: Hash of 10 blocks of 128 bits of size as string plus file size as string
        file_size = os.path.getsize(file_path)
        start_index = int(file_size / 2)
        with file_path.open(mode='r') as f:
            f.seek(start_index)
            n = 1
            md5 = hashlib.md5()
            while True:
                data = f.read(block_size)
                n += 1
                if n == 10:
                    break
                md5.update(data.encode('utf-8'))
        return '{}{}'.format(md5.hexdigest()[0:9], str(file_size))

    def get_sensor_data(self, sensor_data_file_id: int) -> SensorData:
        file_path = self.get_file_path(sensor_data_file_id)

        query = (SensorDataFile
                 .select()
                 .join(Sensor, JOIN.LEFT_OUTER)
                 .join(SensorModel, JOIN.LEFT_OUTER)
                 .where(SensorDataFile.id == sensor_data_file_id)
                 .get()
                 )
        print(query)
        model_id = query.sensor.model.id
        sensor_id = SensorDataFile.get_by_id(sensor_data_file_id).sensor.id

        if model_id >= 0 and sensor_id >= 0:
            sensor_timezone = pytz.timezone(Sensor.get_by_id(sensor_id).timezone)
            sensor_data = SensorData(self.project_controller, Path(file_path), model_id)
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
        file_path = SensorDataFile.get_by_id(sensor_data_file_id).file_path

        # Check whether the file path is still valid
        if os.path.isfile(file_path):
            return file_path
        else:
            # Invalid:
            # Prompt the user for the correct file path
            file_name = SensorDataFile.get_by_id(sensor_data_file_id).file_name
            new_file_path = self.prompt_file_location(file_name, file_path)

            # Update path in database
            sdf = SensorDataFile.get(SensorDataFile.file_name == file_name)
            sdf.file_path = file_path
            sdf.save()

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
        new_path, _ = dialog.getOpenFileName(self.gui, "Open Sensor Data", base_path, filter="csv (*.csv)")

        return new_path

    def prompt_save_location(self, name_suggestion: str):
        # Open QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(self.gui, "Save file",
                                                   self.project_controller.project_dir.as_posix() + "\\" +
                                                   name_suggestion + ".csv")

        return file_path

    def export(self, subject_ids: [int], start_dt: dt.datetime, end_dt: dt.datetime,
               start_dt_local: dt.datetime, end_dt_local: dt.datetime):

        for subject_id in subject_ids:
            subject_name = Subject.get_by_id(subject_id).name
            sensor_query = (SensorUsage
                            .select(SensorUsage.sensor)
                            .where((SensorUsage.subject == subject_id) &
                                   (
                                           SensorUsage.start_datetime.between(start_dt, end_dt) |
                                           SensorUsage.end_datetime.between(start_dt, end_dt) |
                                           (start_dt >= SensorUsage.start_datetime) & (
                                                   start_dt <= SensorUsage.end_datetime) |
                                           (end_dt >= SensorUsage.start_datetime) & (end_dt <= SensorUsage.end_datetime)
                                   )
                                   ))

            if len(sensor_query) == 0:
                QMessageBox(
                    QMessageBox.Warning,
                    "No labels within selected timespan.",
                    f"There are no labels found between {start_dt_local.strftime('%d-%m-%Y %H:%M:%S')} "
                    f"and {end_dt_local.strftime('%d-%m-%Y %H:%M:%S')}.",
                    QMessageBox.Ok
                ).exec()
                return

            for sensor_usage in sensor_query:
                sensor_id = sensor_usage.sensor.id

                sdf_query = (SensorDataFile
                             .select(SensorDataFile.id)
                             .where((SensorDataFile.sensor == sensor_id) &
                                    SensorDataFile.datetime.between(start_dt, end_dt)))

                # TODO: Verify if this should be here: this will make a file with a unique subject-sensorid combination.
                df: pd.DataFrame = pd.DataFrame()

                for file in sdf_query:
                    file_id = file.id
                    labels = get_labels(file_id, start_dt, end_dt)
                    sensor_data = self.get_sensor_data(file_id)

                    if sensor_data is None:
                        raise Exception('Sensor data not found')

                    if not sensor_data.add_abs_dt_col(use_utc=True):
                        return

                    sensor_data.filter_between_dates(start_dt, end_dt)
                    sensor_data.add_labels(labels)

                    # TODO: Indefinite loading bar / loop over deze call plaatsen.
                    data = sensor_data.get_data()
                    df = df.append(data)

                file_path = self.gui.sensor_controller.prompt_save_location(subject_name + "_" + str(sensor_id))

                # Because exporting uses append mode, the existing file has to be deleted first in case of
                # the reuse of file name.
                try:
                    if Path.exists(Path(file_path)):
                        os.remove(file_path)
                except FileNotFoundError:  # Export was cancelled on file location prompt.
                    continue

                # Since the actual writing to disk happens inside the dialog, this is currently not MVC compliant.
                export_dialog = ExportProgressDialog(df, file_path)
                export_dialog.exec()


def get_labels(sensor_data_file_id: int, start_dt: dt.datetime, end_dt: dt.datetime):
    labels = (Label
              .select(Label.start_time, Label.end_time, LabelType.activity)
              .join(LabelType)
              .where(Label.sensor_data_file == sensor_data_file_id &
                     (Label.start_time.between(start_dt, end_dt) |
                      Label.end_time.between(start_dt, end_dt))))
    return [{'start': label.start_time.replace(tzinfo=pytz.utc),
             'end': label.end_time.replace(tzinfo=pytz.utc),
             'activity': label.label_type.activity} for label in labels]
