from datetime import timedelta


def get_hms_sum(time1, time2): # TODO replace this function. It causes errors in multiple occassions.
    """
    Takes the strings of two times in the HH:MM:SS format, and returns a string of the sum of the two times.

    :param time1: The string of the first time of the addition.
    :param time2: The string of the second time of the addition.
    :return: The result of the addition of the two times, again as a string in the HH:MM:SS format.
    """
    if time1 and time2:
        return str(timedelta(hours=int(time1[0:2]), minutes=int(time1[3:5]), seconds=int(time1[6:8])) +
                   timedelta(hours=int(time2[0:2]), minutes=int(time2[3:5]), seconds=int(time2[6:8])))

    return ''


def ms_to_hms(millis):
    """
    Translates a certain amount of milliseconds to a readable HH:MM:SS string.

    :param millis: The number of milliseconds that corresponds to the position of the video.
    :return: A readable string that corresponds to duration in the format HH:MM:SS.
    """
    delta = timedelta(milliseconds=millis)
    seconds = delta.seconds
    hours = seconds // 3600
    minutes = (seconds // 60) - (hours * 60)

    hours, minutes, seconds = str(hours).zfill(2), str(minutes).zfill(2), str(seconds).zfill(2)
    return f"{hours}:{minutes}:{seconds}"
