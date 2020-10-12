import datetime
import os
import subprocess
from datetime import timedelta

import pytz

from date_utils import naive_to_utc

VIDEO_DT_FORMAT = '%Y-%m-%dT%H:%M:%S.000000Z\n'


class FileNotFoundException(Exception):
    pass


def parse_video_frame_rate(file_path):
    """
    Parses the frame rate of video files.

    :param file_path: The path of the video
    :return: float: The frame rate of the video, rounded to 2 decimals
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundException(file_path)

    # https://trac.ffmpeg.org/wiki/FFprobeTips
    args = 'ffprobe -v error -select_streams v:0 -show_entries stream=avg_frame_rate -of ' \
           'default=noprint_wrappers=1:nokey=1 "{}"'.format(file_path)

    ffprobe_output = subprocess.check_output(args).decode('utf-8')

    numerator = ffprobe_output.split('/')[0]
    denominator = ffprobe_output.split('/')[1]
    frame_rate = float(numerator) / float(denominator)
    output = round(frame_rate, 2)

    return output


def parse_video_duration(file_path):
    """
    Parses the duration of video files.

    :param file_path: The path of the video
    :return: float: The duration of the video
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundException(file_path)

    args = 'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{}"'.format(file_path)
    ffprobe_output = subprocess.check_output(args).decode('utf-8')

    return float(ffprobe_output)


def parse_video_begin_time(file_path, timezone=pytz.utc) -> datetime.datetime:
    """
    Parses the start time of video files.

    :param file_path: The path of the video
    :param timezone: The timezone that should be used
    :return: datetime: The begin UTC datetime of the video (without tzinfo)
    """
    if file_path is None or not os.path.isfile(file_path):
        raise FileNotFoundException(file_path)

    args = 'ffprobe -v error -select_streams v:0 -show_entries stream_tags=creation_time ' \
           '-of default=noprint_wrappers=1:nokey=1 "{}"'.format(file_path)
    ffprobe_output = subprocess.check_output(args).decode('utf-8')

    naive_dt = datetime.datetime.strptime(ffprobe_output, VIDEO_DT_FORMAT)
    return naive_to_utc(naive_dt, timezone)


def datetime_with_tz_to_string(utc_dt, format_str, timezone=pytz.utc):
    """
    Formats a localized datetime string to another format

    :param utc_dt: The UTC datetime
    :param timezone: The timezone to convert the datetime to
    :param format_str: The datetime format string
    :return: The formatted datetime string
    """
    return timezone.fromutc(utc_dt).strftime(format_str)


def get_video_end_time(file_path):
    """
    Calculates the stop time of a video file.

    :param file_path: The path of the video
    :return: float: The stop time of the video
    """
    start_time = parse_video_begin_time(file_path)
    duration = parse_video_duration(file_path)
    stop_time = start_time + timedelta(seconds=float(duration))

    return stop_time


def rename_video_to_begin_time(file_path):
    """
    Renames a file to its start time.

    :param file_path: The path of the video
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundException(file_path)

    split_path = file_path.rsplit('/', 1)
    directory = split_path[0]
    file = split_path[1]
    file_extension = file.rsplit('.', 1)[1]

    creation_time = parse_video_begin_time(file_path)
    creation_time_string = datetime_with_tz_to_string(creation_time, '%Y%m%d_%H-%M-%S')

    os.rename(file_path, '{}/{}.{}'.format(directory, creation_time_string, file_extension))
