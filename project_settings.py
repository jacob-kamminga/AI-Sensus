import json
from pathlib import Path
from typing import Any

from constants import PROJECT_CONFIG_FILE, PREVIOUS_SENSOR_DATA_FILE, PLOT_HEIGHT_FACTOR, PROJECT_DATABASE_FILE

INIT_PROJECT_CONFIG = {
    'subj_map': {},
    'next_col': 0,
    'formulas': {},
    'label_opacity': 50,
    'plot_width': 20,
    PLOT_HEIGHT_FACTOR: 1.0,
    PREVIOUS_SENSOR_DATA_FILE: ""
}


class ProjectSettings:

    settings_dict = {}

    def __init__(self, project_dir: Path):
        """
        :param project_dir: The path of the current project
        """
        self.project_dir = project_dir
        self.config_file = project_dir.joinpath(PROJECT_CONFIG_FILE)
        self.database_file = project_dir.joinpath(PROJECT_DATABASE_FILE)
        self.settings_dict = {}

        if not self.config_file.is_file():
            self.create_new_project()
        else:
            self.load_config()

    def create_new_project(self):
        """
        Creates a new project folder, and the necessary project files.
        """
        if not self.project_dir.is_dir():
            self.project_dir.mkdir(parents=True, exist_ok=True)

        # Create new settings_dict dictionary
        self.settings_dict = INIT_PROJECT_CONFIG
        self.save()

    def load_config(self) -> {}:
        """Loads the saved setting dictionary back into this class from a file"""
        with self.config_file.open('r') as f:
            self.settings_dict = json.load(f)

    def save(self) -> None:
        """Saves the current settings_dict dictionary to a file"""
        with self.config_file.open('w') as f:
            json.dump(self.settings_dict, f)

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
