from datetime import timedelta


def get_hms_sum(time1, time2):
    """
    Takes the strings of two times in the HH:MM:SS format, and returns a string of the sum of the two times.

    :param time1: The string of the first time of the addition.
    :param time2: The string of the second time of the addition.
    :return: The result of the addition of the two times, again as a string in the HH:MM:SS format.
    """
    return str(timedelta(hours=int(time1[0:2]), minutes=int(time1[3:5]), seconds=int(time1[6:8])) + timedelta(hours=int(
        time2[0:2]), minutes=int(time2[3:5]), seconds=int(time2[6:8])))


def ms_to_hms(duration):
    """
    Translates a certain amount of milliseconds to a readable HH:MM:SS string.

    :param duration: The number of milliseconds that corresponds to the position of the video.
    :return: A readable string that corresponds to duration in the format HH:MM:SS.
    """
    seconds = (duration // 1000) % 60
    seconds_str = "0" + str(seconds) if seconds < 10 else str(seconds)
    minutes = (duration // (1000 * 60)) % 60
    minutes_str = "0" + str(minutes) if minutes < 10 else str(minutes)
    hours = duration // (1000 * 60 * 60)
    hours_str = "0" + str(hours) if hours < 10 else str(hours)

    return hours_str + ":" + minutes_str + ":" + seconds_str
