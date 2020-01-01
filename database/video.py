import sqlite3
from typing import List, Tuple

import datetime as dt

SQL_CREATE_TABLE = "create table video \
( \
  id        INTEGER not null \
    constraint video_file_pk \
      primary key autoincrement, \
  file_name TEXT    not null, \
  datetime  TIMESTAMP, \
  camera_id INTEGER not null \
    references camera \
); \
 \
create unique index video_file_file_name_uindex \
  on video (file_name);"

SQL_REPLACE_VIDEO = "REPLACE INTO video(file_name, camera_id) VALUES (?, ?)"
SQL_DELETE_VIDEO = "DELETE FROM video WHERE file_name = ?"
SQL_SELECT_ALL_VIDEOS = "SELECT file_name, datetime, camera_id FROM video"
SQL_SELECT_CAMERA = "SELECT camera_id FROM video WHERE video.file_name = ?"
SQL_UPDATE_CAMERA = "UPDATE video SET camera_id = ? WHERE file_name = ?"
SQL_UPDATE_DATETIME = "UPDATE video SET datetime = ? WHERE id = ?"


class VideoManager:

    def __init__(self, project_name: str):
        self._conn = sqlite3.connect('projects/' + project_name + '/project_data.db',
                                     detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self._cur = self._conn.cursor()

    def create_table(self) -> None:
        """Creates the video table in the database."""
        self._cur.execute(SQL_CREATE_TABLE)
        self._conn.commit()

    def replace_video(self, file_name: str, camera_id: int) -> None:
        """
        Adds a video to the table.

        :param file_name: The name of the new camera
        :param camera_id: The ID of the camera that the video was recorded on
        """
        self._cur.execute(SQL_REPLACE_VIDEO, (file_name, camera_id))
        self._conn.commit()

    def delete_video(self, file_name: str) -> None:
        """
        Deletes a video from the database.

        :param file_name: The file name of the video
        """
        self._cur.execute(SQL_DELETE_VIDEO, (file_name,))
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
            return -1
        else:
            return result[0]

    def update_camera(self, file_name: str, camera_id: int):
        """
        Updates the associated camera of a video.

        :param file_name: The file name of the video
        :param camera_id: The camera ID of the camera associated with the video
        """
        self._cur.execute(SQL_UPDATE_CAMERA, (camera_id, file_name))
        self._conn.commit()

    def update_datetime(self, video_id: int, datetime: dt.datetime):
        self._cur.execute(SQL_UPDATE_DATETIME, (datetime, video_id))
        self._conn.commit()
