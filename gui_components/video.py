import os
from datetime import timedelta

import pytz
from PyQt5 import QtGui
from PyQt5.QtCore import QUrl, QDir
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import QFileDialog

import video_metadata
from utils import get_hms_sum, ms_to_hms


class Video:

    def __init__(self, gui):
        self.gui = gui
        self.settings = gui.settings
        self.file_path = None

        self.datetime = None
        self.position = None
        self.camera = None
        self.timezone = pytz.utc  # TODO: Ask for timezone setting when opening video (specified for camera)
        self.offset = None

    def open_previous_file(self):
        previous_path = self.settings.get_setting('last_videofile')

        if previous_path is not None:
            if os.path.isfile(previous_path):
                self.file_path = previous_path
                self.open_video()

    def prompt_video(self):
        # Check if last used path is known
        path = '' if self.settings.get_setting('last_videofile') is None \
            else self.settings.get_setting('last_videofile')

        if not os.path.isfile(path):
            path = path.rsplit('/', 1)[0]
            if not os.path.isdir(path):
                path = QDir.homePath()

        # Get the user input from a dialog window
        self.file_path, _ = QFileDialog.getOpenFileName(self.gui, "Open Video", path)

        self.open_video()

    def open_video(self):
        """
        A function that allows a user to open a video in the QMediaPlayer via the menu bar.
        :return:
        """
        # Connect the QMediaPlayer to the right widget
        self.gui.mediaPlayer.setVideoOutput(self.gui.videoWidget_player)

        # Connect some events that QMediaPlayer generates to their appropriate helper functions
        self.gui.mediaPlayer.positionChanged.connect(self.position_changed)
        self.gui.mediaPlayer.durationChanged.connect(self.duration_changed)

        # Connect the usage of the slider to its appropriate helper function
        self.gui.horizontalSlider_time.sliderMoved.connect(self.set_position)
        self.gui.horizontalSlider_time.setEnabled(False)

        if self.file_path != '':
            # Save the path for next time
            self.settings.set_setting('last_videofile', self.file_path)

            # Store the video start time
            self.datetime = video_metadata.parse_video_begin_time(self.file_path, self.timezone)

            # Play the video in the QMediaPlayer and activate the associated widgets
            self.gui.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.file_path)))
            self.gui.mediaPlayer.play()
            self.gui.pushButton_play.setEnabled(True)
            self.gui.horizontalSlider_time.setEnabled(True)
            self.play()

            self.sync_with_sensor_data()

        # TODO: open camera settings before opening video

    def update_labels_datetime(self):
        video_hms = self.datetime.strftime('%H:%M:%S')
        video_date = self.datetime.strftime('%d-%B-%Y')

        if self.position is not None:
            current_video_time = get_hms_sum(video_hms, ms_to_hms(self.position))
            current_video_date = (self.datetime + timedelta(milliseconds=self.position)).strftime('%d-%B-%Y')
            self.gui.label_video_time.setText(current_video_time)
            self.gui.label_video_date.setText(current_video_date)
        else:
            self.gui.label_video_time.setText(video_hms)
            self.gui.label_video_date.setText(video_date)

    def sync_with_sensor_data(self):
        """
        Set the video time equal to the start of the sensor data.
        """
        if self.datetime is not None and self.gui.plot.x_min_dt is not None:
            self.offset = self.gui.plot.x_min_dt - self.datetime
            offset_ms = self.offset / timedelta(milliseconds=1)

            self.gui.mediaPlayer.setPosition(offset_ms)

    def position_changed(self, new_position):
        """
        Every time QMediaPlayer generates the event that indicates that the video output has changed (which is
        continually if you play a video), this function updates the slider.
        :param new_position: The position of the video.
        """
        if self.gui.loop is not None and new_position >= self.gui.loop[1]:
            self.position = self.gui.loop[0] if self.gui.loop[0] >= 0 else 0
            self.gui.mediaPlayer.setPosition(new_position)
        else:
            self.position = new_position

        self.gui.horizontalSlider_time.setValue(self.position)
        self.gui.label_duration.setText(ms_to_hms(self.position))
        self.update_labels_datetime()

    def duration_changed(self, duration):
        """
        Every time the duration of the video in QMediaPlayer changes (which should be every time you open a new
        video), this function updates the range of the slider.

        :param duration: The duration of the (new) video.
        """
        self.gui.horizontalSlider_time.setRange(0, duration)

    # Media player controls

    def play(self):
        """
        Makes sure the play button pauses or plays the video, and switches the pause/play icons.
        """
        if self.gui.mediaPlayer.media().isNull():
            return
        if self.gui.mediaPlayer.state() == QMediaPlayer.PlayingState:
            icon = QtGui.QIcon()
            self.gui.mediaPlayer.pause()
            icon.addPixmap(QtGui.QPixmap("resources/1600.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.gui.pushButton_play.setIcon(icon)
        else:
            icon = QtGui.QIcon()
            self.gui.mediaPlayer.play()
            icon.addPixmap(QtGui.QPixmap("resources/pause-512.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.gui.pushButton_play.setIcon(icon)

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

    def set_position(self, position):
        """
        Every time the user uses the slider, this function updates the QMediaPlayer position.
        :param position: The position as indicated by the slider.
        """
        self.gui.mediaPlayer.setPosition(position)

    # Camera

    def set_timezone(self, timezone: pytz.timezone):
        self.timezone = timezone

        if self.file_path is not None:
            self.datetime = video_metadata.parse_video_begin_time(self.file_path, self.timezone)
            self.update_labels_datetime()
