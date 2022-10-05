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
from PyQt5.QtWidgets import QFileDialog, QMessageBox, qApp
from peewee import DoesNotExist, JOIN, PeeweeException

from constants import PREVIOUS_SENSOR_DATA_FILE
from data_import.sensor_data import SensorData
from database.models import SensorDataFile, SensorModel, Sensor, Camera, Offset, Label, LabelType, SubjectMapping, Subject
from date_utils import naive_to_utc
import datetime


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

    def open_previous_file(self) -> None:
        """
        Open the sensor data file when loading the project.
        """
        previous_path = self.project_controller.get_setting(PREVIOUS_SENSOR_DATA_FILE)

        if previous_path:
            previous_path = Path(previous_path)

            if previous_path.is_file():
                self.file_path = previous_path
                self.open_file()

                if hasattr(self.gui, 'video_controller') and self.gui.video_controller.project_dt is not None:
                    self.gui.video_controller.set_position(0)

    def prompt_file(self) -> None:
        """
        Open a file dialog that lets the user select a file.
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
        self.open_file(Path(self.file_path))
        self.gui.plot_controller.draw_graph()

    @staticmethod
    def add_sensor(name: str, sensor_model: SensorModel, timezone: pytz.timezone = None) -> Sensor:
        """
        Add a new sensor, created from a name, sensor model object and a timezone.

        :param name: The sensor name
        :param sensor_model: The SensorModel object specifying the format of the sensor data
        :param timezone: The timezone in which the sensor was located when used

        :return: The new sensor instance
        """
        sensor = Sensor(name=name, model=sensor_model, timezone=timezone)
        sensor.save()
        return sensor

    @staticmethod
    def edit_sensor(sensor: Sensor, timezone: pytz.UTC) -> bool:
        """
        Edit and save a sensor in the database.

        :param sensor: The sensor to be edited
        :param timezone: The timezone that the sensor should have

        :return: True if the timezone was set and the sensor was saved, False otherwise.
        """
        try:
            sensor.timezone = timezone
            sensor.save()
            return True
        except PeeweeException:
            return False

    def delete_sensor(self, sensor: Sensor):
        """
        `Stub`\n
        Delete the sensor, making sure the database objects that use this sensor are handled properly.

        :param sensor: The sensor to be deleted.

        :return: True if the sensor could be deleted, False otherwise.
        """

        # Subject mappings, offsets and sensor data files all have references to a sensor.

        pass

    @staticmethod
    def edit_subject_mapping(self,
            subject_mapping: SubjectMapping,
            subject: Subject,
            sensor: Sensor,
            start_dt: dt.datetime,
            end_dt: dt.datetime) -> bool:

        """
        Edit and save a sensor usage in the database.

        :param subject_mapping: The subject mapping instance to be edited
        :param subject: The new subject for the mapping
        :param sensor: The new sensor the subject is mapped to
        :param start_dt: Start time of the mapping
        :param end_dt: End time of the mapping

        :return: True if the mapping was succesful and could be saved, False otherwise.
        """
        subject_mapping.subject = subject
        subject_mapping.sensor = sensor
        subject_mapping.start_datetime = naive_to_utc(start_dt, self.project_timezone)
        subject_mapping.end_datetime = naive_to_utc(end_dt, self.project_timezone)

        try:
            subject_mapping.save()
            return True
        except PeeweeException:
            return False

    @staticmethod
    def delete_subject_mapping(subject_mapping: SubjectMapping) -> bool:
        """
        Delete a subject mapping instance.

        :param subject_mapping: The subject mapping instance to be deleted.

        :returns: True if the subject mapping could be deleted, False otherwise.
        """
        try:
            subject_mapping.delete_instance()
            return True
        except:
            return False

    def open_sensor_model_dialog(self):
        # TODO: Move this out.
        from gui.dialogs.sensor_model_dialog import SensorModelDialog
        dialog = SensorModelDialog(self)
        dialog.exec()
        return dialog.selected_model_id

    @staticmethod
    def save_sensor_model(sensor_model: SensorModel) -> bool:
        """
        Save a sensor model instance to the database.

        :param sensor_model: The sensor model that should be saved.

        :return: True if the sensor model could be saved, False otherwise.
        """
        try:
            sensor_model.save()
            return True
        except:
            return False

    @staticmethod
    def delete_sensor_model(sensor_model: SensorModel) -> bool:
        """ Delete a sensor model instance.

        :param sensor_model: The sensor model that should be deleted.
        :returns: True if the sensor model could be deleted, False otherwise.
        """
        try:
            sensor_model.delete_instance()
            return True
        except:
            return False

    def get_or_create_sdf(self, file_path) -> SensorDataFile:
        """
        Get or create the SensorDataFile object from the database that corresponds to `file_path`.

        :param file_path: The file path of the sensor data file on the user's system.
        :return: An existing or new SensorDataFile object
        """
        self.file_name = file_path.name
        self.file_path = file_path

        self.file_name = ntpath.basename(self.file_path.as_posix())
        self.file_id_hash = self.create_file_id(self.file_path)

        # Get or create the sensor data file model instance
        sdf = SensorDataFile.get_or_create(
            file_id_hash=self.file_id_hash,
            defaults={
                'file_name': self.file_name,
                'file_path': self.file_path,
                'sensor': -1,
            }
        )[0]

        return sdf

    def open_file(self, file_path: Path = None) -> None:
        """
        Open the file specified and load the sensor data from the file.
        """

        if file_path is not None:
            self.file_path = file_path

        if self.file_path and self.file_path.is_file():

            self.gui.label_sensor_data_filename.setText(f"Loading \"{self.file_path.name}\"...")
            qApp.processEvents()  # Force GUI to refresh to show loading text before loading the sensor data file.

            # Store the selected file path in the configuration
            self.project_controller.set_setting(PREVIOUS_SENSOR_DATA_FILE, self.file_path.as_posix())

            self.sensor_data_file = self.get_or_create_sdf(self.file_path)

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
                                .where(SensorModel.id == self.sensor_data_file.sensor.model_id)
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
                from gui.dialogs.edit_sensor_dialog import EditSensorDialog
                dialog = EditSensorDialog(self, sensor)
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
            self.gui.update_camera_sensor_offset()
            self.gui.plot_controller.init_graph()
            self.gui.plot_controller.draw_graph()
            self.gui.video_controller.sync_with_sensor_data()
            self.gui.label_sensor_data_filename.setText(self.file_path.as_posix())

    def init_functions(self) -> None:
        """
        Add every column in the DataFrame to the possible Data Series that can be plotted, except for time,
        and plot the first one.
        """
        self.gui.comboBox_functions.clear()

        data_cols = self.df.columns.tolist()
        del data_cols[self.sensor_data.sensor_model.timestamp_column]

        for col in data_cols:
            self.gui.comboBox_functions.addItem(col)

        last_used_col = self.sensor_data_file.last_used_column

        if last_used_col is not None and self.gui.plot_controller.set_current_plot(last_used_col):
            self.gui.comboBox_functions.setCurrentText(last_used_col)
        else:
            self.gui.plot_controller.set_current_plot(self.gui.comboBox_functions.currentText())

    def save_last_used_column(self, function_name) -> None:
        """
        Store the last function that was used in the sensor data file object for later reference.

        :param function_name: The function name to be saved.
        """
        self.sensor_data_file.last_used_column = function_name
        self.sensor_data_file.save()

    def update_camera_text(self) -> None:
        """
        `DEPRECATED`\n
        Update the video offset value in the GUI spinbox.
        """
        camera_name = self.gui.label_camera_name_value.text()

        if camera_name:
            offset = (Offset
                      .select(Offset.offset)
                      .join(Camera, Sensor)
                      .where((Camera.name == camera_name) &
                             (Sensor.id == self.sensor_data_file.sensor) &
                             (Offset.added == self.utc_dt.date())))

            self.gui.doubleSpinBox_video_offset.setValue(offset.offset)

    def update_sensor(self, sensor_id: int) -> None:
        """
        Change the sensor of the current sensor data file.

        :param sensor_id: The id of the new sensor
        """
        if self.sensor_data_file is not None:
            self.sensor_data_file.sensor = sensor_id
            self.sensor_data_file.save()

    def change_offset(self, offset: float) -> None:
        """
        Updates the time offset in the database.

        :param offset: The new offset for this camera and sensor.
        """

        if self.sensor_data_file.sensor is not None:
            date = self.sensor_data_file.datetime.date()
            camera = self.gui.camera_controller.camera

            if camera is not None:
                (Offset
                 .replace(camera=self.gui.camera_controller.camera.id,
                          sensor=self.sensor_data_file.sensor,
                          offset=offset,
                          added=date)
                 .execute())
            else:
                self.gui.doubleSpinBox_video_offset.setValue(0)

    @staticmethod
    def create_file_id(file_path, block_size=256):
        """
        Function that takes a file and returns the first 10 characters of a hash of
        10 times block size in the middle of the file.

        :param file_path: File path as string
        :param block_size:
        :return: Hash of 10 blocks of 128 bits of size as string plus file size as string.
        """

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
        """
        Get the sensor data from the sensor data file.

        :param sensor_data_file_id: The id of the sensor data file instance containing the desired data

        :return: A new SensorData instance containing the desired data
        """
        file_path = self.get_file_path(sensor_data_file_id)

        query = (SensorDataFile
                 .select()
                 .join(Sensor, JOIN.LEFT_OUTER)
                 .join(SensorModel, JOIN.LEFT_OUTER)
                 .where(SensorDataFile.id == sensor_data_file_id)
                 .get()
                 )

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

        :param sensor_data_file_id: The sensor data file for which the path should be checked.

        :returns: The existing file path if it exists, or a new file path as specified by the user
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

    def prompt_save_location(self, name_suggestion: str) -> str:
        """
        Request the user to specify a location to save the file.

        :param name_suggestion: an auto-generated suggestion for the file name based on project settings

        :return: The selected file path
        """
        # Open QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(self.gui, "Save file",
                                                   self.project_controller.project_dir.as_posix() + "\\" +
                                                   name_suggestion + ".csv")

        return file_path


def get_labels(sdf_id: int, start_dt: dt.datetime, end_dt: dt.datetime) -> list:
    """
    Get all the labels linked to the desired sensor data file within the specified interval.

    :param sdf_id: The SensorDataFile id from which the labels should be retrieved.
    :param start_dt: The start time of the interval
    :param end_dt: The end time of the interval
    :return: A list of dictionaries, each representing one annotation, containing the start time, end time, and activity
    of that label
    """

    # The original query, where only the labels for sdf_id==1 were retrieved, even is sdf_id was actually 2.

    # labels = (Label
    #           .select(Label.start_time, Label.end_time, LabelType.activity)
    #           .join(LabelType)
    #           .where(Label.sensor_data_file == sdf_id & (Label.start_time.between(start_dt, end_dt) |
    #                   Label.end_time.between(start_dt, end_dt))))

    # labels = (Label
    #           .select(Label.start_time, Label.end_time, LabelType.activity)
    #           .join(LabelType)
    #           .where(Label.sensor_data_file == ([bool(2)] & [Not None] |
    #                   Label.end_time.between(start_dt, end_dt))))

    # labels = (Label
    #           .select(Label.start_time, Label.end_time, LabelType.activity)
    #           .join(LabelType)
    #           .where(Label.sensor_data_file == [True] |
    #                   Label.end_time.between(start_dt, end_dt))))

    # labels = (Label
    #           .select(Label.start_time, Label.end_time, LabelType.activity)
    #           .join(LabelType)
    #           .where(Label.sensor_data_file == 1 |
    #                   Label.end_time.between(start_dt, end_dt))))

    # GEBRUIK HAAKJES!!!

    labels = (Label
              .select(Label.start_time, Label.end_time, LabelType.activity)
              .join(LabelType)
              .where((Label.sensor_data_file == sdf_id) &
                     (Label.start_time.between(start_dt, end_dt) |
                      Label.end_time.between(start_dt, end_dt))))

    return [{'start': label.start_time,
             'end': label.end_time,
             'activity': label.label_type.activity} for label in labels]
