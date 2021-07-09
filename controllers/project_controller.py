import json
from typing import Any

from constants import PROJECT_CONFIG_FILE, PREVIOUS_SENSOR_DATA_FILE, PLOT_HEIGHT_FACTOR, PROJECT_DATABASE_FILE
from database.models import db, Label, LabelType, Camera, Video, Sensor, SensorModel, SensorDataFile, \
    SensorUsage, Subject, Offset

INIT_PROJECT_CONFIG = {
    'subj_map': {},
    'next_col': 0,
    'formulas': {},
    'label_opacity': 50,
    'plot_width': 20,
    'timezone': 'UTC',
    PLOT_HEIGHT_FACTOR: 1.0,
    PREVIOUS_SENSOR_DATA_FILE: ""
}


class ProjectController:

    def __init__(self, isTestProject: bool = False):
        self.isTestProject = isTestProject
        self.project_dir = None
        self.config_file = None
        self.database_file = None
        self.settings_dict = {}
        self.settings_changed = False

    def load(self, project_dir, new_project=False):
        if project_dir is not None:
            self.project_dir = project_dir
            self.config_file = project_dir.joinpath(PROJECT_CONFIG_FILE)
            self.database_file = project_dir.joinpath(PROJECT_DATABASE_FILE)

            self.settings_dict = {}
            self.settings_changed = False
        if new_project or not self.config_file.is_file():
            self.create_new_project()
        else:
            self.load_config()

        self.init_db()

    def init_db(self):
        db.init(self.database_file)
        db.connect()
        db.create_tables(
            [Label, LabelType, Camera, Video, Sensor, SensorModel, SensorDataFile, SensorUsage, Subject,
             Offset])

    def create_new_project(self):
        """
        Creates a new project folder, and the necessary project files.
        """
        if not self.project_dir.is_dir():
            self.project_dir.mkdir(parents=True, exist_ok=True)

        # Create new settings_dict dictionary
        self.settings_dict = INIT_PROJECT_CONFIG
        self.save()

    def load_config(self):
        """Loads the saved setting dictionary back into this class from a file"""
        with self.config_file.open(mode='r') as f:
            self.settings_dict = json.load(f)
            # self.load_timezone()

    def save(self) -> None:
        """Saves the current settings_dict dictionary to a file"""
        with self.config_file.open(mode='w') as f:
            json.dump(self.settings_dict, f)
        self.settings_changed = True

    def set_setting(self, setting: str, new_value: Any) -> None:
        """
        Adds or changes a setting with the given name.

        :param setting: The setting to change
        :param new_value: The value the setting should get
        """
        self.settings_dict[setting] = new_value
        self.save()

    def get_setting(self, setting: str) -> Any:
        """
        Returns the value of a given setting.

        :param setting: The setting to retrieve
        :return: The value of the setting, or None if the setting is unknown
        """
        return self.settings_dict.get(setting)
