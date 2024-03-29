import datetime as dt
import ntpath
import os
from pathlib import Path
from typing import Optional

import pytz
from PyQt5 import QtGui
from PyQt5.QtCore import QUrl, QDir
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from peewee import DoesNotExist

import video_metadata
from database.models import Video
from date_utils import utc_to_local
from gui.dialogs.project_settings_dialog import ProjectSettingsDialog
from utils import ms_to_hms


class VideoController:

    def __init__(self, gui):
        self.gui = gui
        self.project_controller = gui.project_controller
        self.file_name = None
        self.file_path = None

        self.video = None
        self.utc_dt: Optional[dt.datetime] = None
        self.project_dt: Optional[dt.datetime] = None
        self.position = None
        self.timezone = None
        self.init_offset = None
        """The offset between the beginning of the video and the beginning of the sensor data."""

    def open_previous_file(self):
        previous_path = self.project_controller.get_setting('last_videofile')

        if previous_path is not None:
            previous_path = Path(previous_path)
            if previous_path.is_file():
                self.open_file(previous_path)

    def prompt_file(self):
        """
        Opens a file dialog that lets the user select a file.
        """
        # Check if last used path is known
        path = self.project_controller.get_setting('last_videofile')

        if path is None:
            path = ""
        elif not os.path.isfile(path):
            # Split path to obtain the base path
            path = path.rsplit('/', 1)[0]

            if not os.path.isdir(path):
                path = QDir.homePath()

        # Get the user input from a dialog window
        file_path, _ = QFileDialog.getOpenFileName(self.gui, "Open Video", path)
        self.open_file(Path(file_path))

    def open_file(self, file_path: Path = None):
        """
        Opens the video file from `file_path` and creates the Video object in the database.
        """
        if file_path is not None:
            self.file_path = file_path

        if self.file_path is not None and os.path.isfile(self.file_path):
            # Save the path for next time
            self.project_controller.set_setting('last_videofile', str(self.file_path))

            self.file_name = ntpath.basename(self.file_path)

            # Check if a camera has already been set for this video
            try:
                camera_id = Video.get(Video.file_name == self.file_name).camera
                self.gui.camera_controller.change_camera(camera_id)
            except Video.DoesNotExist:  # No camera was found
                self.gui.open_select_camera_dialog()

            if self.gui.camera_controller.camera is not None:
                self.update_datetime()

                try:
                    self.video = Video.get(Video.file_name == self.file_name)
                    self.video.file_path = self.file_path
                    self.video.save()
                except DoesNotExist:
                    # Video not yet in database
                    self.video = Video(file_name=self.file_name, file_path=self.file_path, datetime=self.utc_dt,
                                       camera=self.gui.camera_controller.camera.id)
                    self.video.save()

                self.gui.label_video_filename.setText(self.file_path.as_posix())

                # Play the video in the QMediaPlayer and activate the associated widgets
                self.gui.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(str(self.file_path))))
                self.gui.pushButton_play.setEnabled(True)
                self.gui.horizontalSlider_time.setEnabled(True)

                self.sync_with_sensor_data()
                self.pause()
                self.unmute()

    def update_datetime(self):
        timezone = pytz.timezone(self.gui.camera_controller.camera.timezone)
        self.utc_dt = video_metadata.parse_video_begin_time(self.file_path, timezone) + \
                      dt.timedelta(hours=self.gui.camera_controller.camera.manual_offset)
        self.update_timezone()
        self.update_labels_datetime()

    def update_timezone(self):
        if self.utc_dt is not None:
            self.project_dt = utc_to_local(self.utc_dt, pytz.timezone(self.project_controller.get_setting('timezone')))

    def update_camera(self, camera_id: int):
        if self.video is not None:
            self.video.camera = camera_id
            self.video.save()

        self.update_datetime()
        self.sync_with_sensor_data()
        self.set_position(0)

    def delete_videos_with_camera(self, camera_id: int):
        query = Video.delete().where(Video.camera == camera_id)
        query.execute()

    def update_labels_datetime(self):
        video_hms = self.project_dt.strftime("%H:%M:%S")
        video_date = self.project_dt.strftime("%d-%B-%Y")

        if self.position is not None:
            current_video_time = (self.project_dt + dt.timedelta(milliseconds=self.position)).strftime('%H:%M:%S')
            current_video_date = (self.project_dt + dt.timedelta(milliseconds=self.position)).strftime('%d-%B-%Y')
            self.gui.label_video_time_value.setText(current_video_time)
            self.gui.label_video_date_value.setText(current_video_date)
        else:
            self.gui.label_video_time_value.setText(video_hms)
            self.gui.label_video_date_value.setText(video_date)

    def sync_with_sensor_data(self):
        """
        Synchronizes the start time of the video with the sensor data.
        """
        if self.project_dt is not None and self.gui.plot_controller.x_min_dt is not None:
            # Update plot according to the camera offset value
            self.gui.plot_controller.update_plot_axis()

            self.init_offset = self.gui.plot_controller.x_min_dt - self.project_dt
            init_offset_ms = self.init_offset / dt.timedelta(milliseconds=1)

            # The offset between the video and sensor data should be at most 12 hours
            # Otherwise an overflow can occur in the horizontal slider
            if dt.timedelta(hours=-12) <= self.init_offset <= dt.timedelta(hours=12):
                self.position = init_offset_ms
                self.gui.mediaPlayer.setPosition(self.position)
                self.gui.horizontalSlider_time.setValue(int(self.position))
            else:
                print(f'offset: {self.init_offset}')
                QMessageBox(
                    QMessageBox.Warning,
                    'Sync error',
                    'Cannot synchronize the video with the sensor data. The datetime of the video and sensor data have '
                    'an offset of more than 12 hours',
                    QMessageBox.Ok
                ).exec()

    def position_changed(self, new_position):
        """
        Updates the slider upon a change in the video output.

        Every time QMediaPlayer generates the event that indicates that the video output has changed (which is
        continually if you play a video), this function updates the slider.

        :param new_position: The position of the video.
        """
        if self.gui.loop is not None and new_position >= self.gui.loop[1]:
            self.position = self.gui.loop[0] if self.gui.loop[0] >= 0 else 0
            self.gui.mediaPlayer.setPosition(new_position)
        else:
            self.position = new_position
        # print(new_position)
        # self.gui.label_active_label_value.setText(str(self.gui.mediaPlayer.position()))

        self.gui.horizontalSlider_time.setValue(self.position)
        self.gui.label_duration.setText(ms_to_hms(self.position))
        self.update_labels_datetime()

    def duration_changed(self, duration):
        """
        Updates the range of the slider using the duration of the video.

        Every time the duration of the video in QMediaPlayer changes (which should be every time you open a new
        video), this function updates the range of the slider.

        :param duration: The duration of the video.
        """
        try:
            self.gui.horizontalSlider_time.setRange(0, duration)
            self.gui.horizontalSlider_time.setValue(self.position)
        except:
            print("Could not update the range of the slider")

    # Media player controls

    def play(self):
        """
        Start playback of the video.
        """
        if self.gui.mediaPlayer.media().isNull():
            return
        else:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("resources/pause-512.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

            self.gui.mediaPlayer.play()
            self.gui.pushButton_play.setIcon(icon)

    def pause(self):
        """
        Pause playback of the video.
        """
        if self.gui.mediaPlayer.media().isNull():
            return
        else:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("resources/1600.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

            self.gui.mediaPlayer.pause()
            self.gui.pushButton_play.setIcon(icon)

    def toggle_play(self):
        """
        Toggle playback of the video.
        """
        if self.gui.mediaPlayer.media().isNull():
            return
        elif self.gui.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.pause()
        elif self.gui.mediaPlayer.state() == QMediaPlayer.PausedState:
            self.play()
        elif self.gui.mediaPlayer.state() == QMediaPlayer.StoppedState:
            self.pause()

    def mute(self):
        if self.gui.mediaPlayer.media().isNull():
            return
        else:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("resources/mute.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

            self.gui.mediaPlayer.setMuted(True)
            self.gui.pushButton_mute.setIcon(icon)

    def unmute(self):
        if self.gui.mediaPlayer.media().isNull():
            return
        else:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("resources/unmute.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

            self.gui.mediaPlayer.setMuted(False)
            self.gui.pushButton_mute.setIcon(icon)

    def toggle_mute(self):
        if self.gui.mediaPlayer.media().isNull():
            return
        elif self.gui.mediaPlayer.isMuted():
            self.unmute()
        elif not self.gui.mediaPlayer.isMuted():
            self.mute()

    def fast_forward_10s(self):
        """
        Sets the position of the video player 10 seconds forward
        """
        if not self.gui.mediaPlayer.media().isNull():
            self.gui.mediaPlayer.setPosition(self.gui.mediaPlayer.position() + 10000)

    def rewind_10s(self):
        """
        Sets the position of the video player 10 seconds backward
        """
        if not self.gui.mediaPlayer.media().isNull():
            self.gui.mediaPlayer.setPosition(self.gui.mediaPlayer.position() - 10000)

    def change_speed(self):
        """
        Changes the playback rate of the video.
        """
        self.gui.mediaPlayer.setPlaybackRate(self.gui.doubleSpinBox_speed.value())

    def set_position(self, position=None):
        """
        Every time the user uses the slider, this function updates the QMediaPlayer position.

        :param position: The position as indicated by the slider.
        """
        if self.gui.mediaPlayer.duration() != 0:
            if position is None:
                position = self.gui.horizontalSlider_time.value()
            self.gui.mediaPlayer.setPosition(position)  # todo is this method different for wmv files?
