import os
from pathlib import Path

import pandas as pd
import pytz
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot, QObject
from PyQt5.QtWidgets import QMessageBox, QApplication

import date_utils
from controllers.sensor_controller import get_labels
from database.models import SensorDataFile, SubjectMapping, Subject
from gui.designer.progress_bar import Ui_Dialog
from numpy import array_split

import datetime as dt


class ExportProgressDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, gui, subject_ids: [int], start_dt: dt.datetime, end_dt: dt.datetime, test_file_dir: Path = None):
        super().__init__()
        self.setupUi(self)

        self.gui = gui

        jobs = []
        cancelled_exports = 0

        for subject_id in subject_ids:
            subject_name = Subject.get_by_id(subject_id).name
            subject_mappings = (SubjectMapping
                                .select(SubjectMapping.sensor)
                                .where((SubjectMapping.subject == subject_id) &
                                       (
                                               SubjectMapping.start_datetime.between(start_dt, end_dt) |
                                               SubjectMapping.end_datetime.between(start_dt, end_dt) |
                                               (start_dt >= SubjectMapping.start_datetime) & (
                                                       start_dt <= SubjectMapping.end_datetime) |
                                               (end_dt >= SubjectMapping.start_datetime) & (
                                                       end_dt <= SubjectMapping.end_datetime)
                                       )
                                       ))

            print(f"Found {len(subject_mappings)} subject mappings for subject_id {subject_id}.")

            if len(subject_mappings) == 0:
                local_timezone = pytz.timezone(self.gui.project_controller.get_setting('timezone'))
                start_local = date_utils.utc_to_local(start_dt, local_timezone)
                end_local = date_utils.utc_to_local(end_dt, local_timezone)
                QMessageBox(
                    QMessageBox.Warning,
                    f"No labels within selected timespan for subject \"{subject_name}\".",
                    f"There are no labels found between {start_local.strftime('%d-%m-%Y %H:%M:%S')} "
                    f"and {end_local.strftime('%d-%m-%Y %H:%M:%S')}.",
                    QMessageBox.Ok
                ).exec()
                cancelled_exports += 1
                continue

            for subject_mapping in subject_mappings:
                sensor_id = subject_mapping.sensor.id
                if self.gui.testing and test_file_dir is not None:
                    file_path = test_file_dir
                else:
                    file_path = self.gui.sensor_controller.prompt_save_location(subject_name + "_" + str(sensor_id))

                if file_path == "":  # The save prompt was closed by the user.
                    raise RuntimeError("No path was chosen. User may have exited manually.")

                # Retrieve all SensorDataFile that have this sensor associated with it.
                sdf_query = (SensorDataFile
                             .select(SensorDataFile.id)
                             .where((SensorDataFile.sensor == sensor_id) &
                                    SensorDataFile.datetime.between(start_dt, end_dt)))

                files = []
                print(f"Found {len(sdf_query)} files.")
                for sdf in sdf_query:
                    QApplication.processEvents()
                    labels = get_labels(sdf.id, start_dt, end_dt)  # DB
                    sensor_data = self.gui.sensor_controller.get_sensor_data(sdf.id)  # DB

                    if sensor_data is None:
                        raise Exception('Sensor data not found')

                    if not sensor_data.add_abs_dt_col(use_utc=True):
                        continue

                    sensor_data.filter_between_dates(start_dt, end_dt)
                    sensor_data.add_labels(labels)

                    files.append(sensor_data)

                # sdf_query = [file, file, file] = [(labels, sensor_data), (labels, sensor_data), (labels, sensor_data)]
                jobs.append((file_path, files, sensor_id))

        if len(jobs) > 0:
            self.worker = ExportWorker(jobs, list(self.gui.sensor_controller.df.columns), start_dt, end_dt)
            self.thread = QThread()
            self.worker.progress.connect(self.changeProgress)
            self.worker.text.connect(self.changeText)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.thread.finished.connect(self.worker.deleteLater)
            self.worker.finished.connect(self.done_)
            self.pushButton_cancel.clicked.connect(self.abort_export)
        elif not cancelled_exports == len(subject_ids):
            # Only raise an error if a job isn't queued even though there should be a job.
            raise RuntimeError("No jobs are queued.")
        else:
            return

        self.thread.start()

    def abort_export(self):
        res = QMessageBox.warning(self, "Abort", "Are you sure you want to cancel the export?",
                                  QMessageBox.Ok | QMessageBox.Cancel)
        if res == QMessageBox.Ok:
            self.worker.abort()

            # It may take some time before the thread picks up on the signal.
            while not self.worker.aborted:
                self.thread.sleep(1)

            self.thread.exit()
            self.close()

    @pyqtSlot(str)
    def changeText(self, text):
        self.processLabel.setText(text)

    @pyqtSlot(int)
    def changeProgress(self, percentage):
        self.progressBar.setProperty("value", percentage + 1)
        if percentage == 100:
            self.close()

    @pyqtSlot()
    def done_(self):
        QMessageBox.information(self, "Export", "Export completed successfully!")


class ExportWorker(QObject):
    finished = pyqtSignal()
    text = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, jobs, column_names, start_dt, end_dt):
        super().__init__()
        self.aborted = False
        self.paused = False
        self.jobs = jobs
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.column_names = column_names

    @pyqtSlot()
    def run(self):
        """Export the dataframe to a CSV file in chunks.

        This loop separates the dataframe in 100 roughly equal parts and appends each part to the
        previous parts, so that a progress update can be given in the form of a progress bar. This
        is particularly useful for dataframes that encompass large amounts of time."""
        print("Running...")
        for file_path, files, sensor_id in self.jobs:

            file_path = Path(file_path)

            self.text.emit(f"Collecting data for {file_path.as_posix()}")
            df = pd.DataFrame()
            # df.to_csv(file_path)  # Write out the columns, which will get lost after the split

            for sensor_data in files:
                # TODO: Indefinite loading bar / loop over deze call plaatsen.

                df = df.append(sensor_data.get_data())

            # Because exporting uses append mode, the existing file has to be deleted first in case of
            # the reuse of file name.
            try:
                if file_path.is_file():
                    file_path.unlink()

            except FileNotFoundError:  # Export was cancelled on file location prompt.
                continue

            except PermissionError:
                QMessageBox.critical("Could not write to file",
                                     "You do not have the permission to write to this file location. If the file "
                                     "already exists, this may mean the file is currently open, so it cannot be "
                                     "overwritten.")

            df_split = array_split(df, 100)  # Divide into 100 (roughly) equal chunks.

            # debug = getattr(sys, 'gettrace', None)() is not None  # Check if the program is running in debug mode.
            # if debug:
            #     print("Slowing down export progress bar for visualisation...")

            try:
                self.text.emit(f"Writing to {file_path}...")

                # with file_path.open(mode='w') as file:
                #     file.write(",".join(list(df.columns)))

                for i in range(100):
                    # if debug:  # Slows down the progress bar to check if it works correctly.
                    #     for j in range(100):
                    #         pass

                    if self.aborted:
                        self.text.emit("Aborting...")
                        self.close()
                        return
                    if not self.paused:
                        QApplication.processEvents()
                        # Append each chunk to output_path CSV using mode='a' (append).
                        df_split[i].to_csv(file_path, mode='a', header=(i == 0), index=False)
                        self.progress.emit(i + 1)

            except Exception as e:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Error!")
                msg.setText("An error occurred during export: " + str(e))
                msg.setStandardButtons(QMessageBox.Ok)
                return

        self.finished.emit()

    def abort(self):
        self.aborted = True
        self.text.emit("Aborting...")
