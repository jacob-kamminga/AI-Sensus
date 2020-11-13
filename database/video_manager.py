import datetime as dt
import sqlite3
from typing import List, Tuple

from exceptions import VideoDoesNotExist
from gui.dialogs.project_settings import ProjectSettingsDialog

SQL_CREATE_TABLE = "create table video\
(\
  id        INTEGER not null\
    constraint video_file_pk\
      primary key autoincrement,\
  file_name TEXT    not null,\
  file_path TEXT,\
  datetime  TIMESTAMP,\
  camera_id INTEGER not null\
    references camera\
);\
\
create unique index video_file_file_name_uindex\
  on video (file_name);"

SQL_DELETE_VIDEO_FILENAME = "DELETE FROM video WHERE file_name = ?"
SQL_DELETE_VIDEO_CAMERA_ID = "DELETE FROM video WHERE camera_id = ?"

SQL_INSERT_VIDEO = "INSERT INTO video(file_name, file_path, camera_id, datetime) VALUES (?, ?, ?, ?)"


SQL_SELECT_ALL_VIDEOS = "SELECT file_name, datetime, camera_id FROM video"
SQL_SELECT_CAMERA = "SELECT camera_id FROM video WHERE video.file_name = ?"
SQL_SELECT_ID = "SELECT id FROM video WHERE file_name = ?"

SQL_UPDATE_CAMERA = "UPDATE video SET camera_id = ? WHERE id = ?"
SQL_UPDATE_DATETIME = "UPDATE video SET datetime = ? WHERE id = ?"
SQL_UPDATE_FILE_PATH = "UPDATE video SET file_path = ? WHERE file_name = ?"


class VideoManager:

    def __init__(self, settings: ProjectSettingsDialog):
        self._conn = sqlite3.connect(
            settings.database_file.as_posix(),
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        # Enable Sqlite foreign key support
        self._conn.execute("PRAGMA foreign_keys = 1")

        self._cur = self._conn.cursor()

    def create_table(self) -> None:
        """Creates the video table in the database."""
        self._cur.execute(SQL_CREATE_TABLE)
        self._conn.commit()

    def get_video_id(self, file_name: str) -> int:
        self._cur.execute(SQL_SELECT_ID, (file_name,))
        id_ = self._cur.fetchone()

        if id_ is None:
            return -1
        else:
            return id_[0]

    def insert_video(self, file_name: str, file_path: str, camera_id: int, datetime: dt.datetime) -> None:
        """
        Adds a video to the table.

        :param file_name: The file name of the video
        :param file_path: The file path of the video
        :param camera_id: The ID of the camera that the video was recorded on
        :param datetime: The datetime of the start of the video
        """
        self._cur.execute(SQL_INSERT_VIDEO, (file_name, file_path, camera_id, datetime))
        self._conn.commit()

    def delete_video(self, video_id) -> None:
        """
        Deletes a video from the database.

        :param video_id: Either the filename or camera_id
        """
        if isinstance(video_id, str):
            # Delete based on filename
            self._cur.execute(SQL_DELETE_VIDEO_FILENAME, (video_id,))
        elif isinstance(video_id, int):
            # Delete based on camera_id
            self._cur.execute(SQL_DELETE_VIDEO_CAMERA_ID, (video_id,))
        else:
            return
        self._conn.commit()

    def get_all_videos(self) -> List[Tuple[str, str]]:
        """
        Returns all videos.

        :return: List of tuples (file_name, datetime, camera_id) of all videos
        """
        self._cur.execute(SQL_SELECT_ALL_VIDEOS)
        return self._cur.fetchall()

    def get_camera(self, file_name: str) -> int:
        """
        Returns the camera ID of the camera associated with the video, if it exists.

        :param file_name: The file name of the video
        :return: The camera ID of the camera if it exists, else -1
        """
        self._cur.execute(SQL_SELECT_CAMERA, (file_name,))
        result = self._cur.fetchone()

        if result is None:
            raise VideoDoesNotExist()

        return result[0]

    def update_camera(self, video_id: int, camera_id: int):
        """
        Updates the associated camera of a video.

        :param video_id: The ID of the video
        :param camera_id: The camera ID of the camera associated with the video
        """
        self._cur.execute(SQL_UPDATE_CAMERA, (camera_id, video_id))
        self._conn.commit()

    def update_datetime(self, video_id: int, datetime: dt.datetime):
        """
        Update the datetime of a video.

        :param video_id: The video ID
        :param datetime: The new datetime
        """
        self._cur.execute(SQL_UPDATE_DATETIME, (datetime, video_id))
        self._conn.commit()

    def update_file_path(self, file_name: str, file_path: str):
        """
        Update the file path of a video.

        :param file_name: The file name of the video
        :param file_path: The file path of the video
        """
        self._cur.execute(SQL_UPDATE_FILE_PATH, (file_path, file_name))
        self._conn.commit()
