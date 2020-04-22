"""
Global Labeling App exception and warning classes.
"""


class VideoDoesNotExist(Exception):
    """The video does not exist in the database."""
    pass


class SensorDoesNotExist(Exception):
    """The sensor does not exist in the database."""
    pass


class SensorDataFileDoesNotExist(Exception):
    """The sensor data file does not exist in the database."""
    pass
