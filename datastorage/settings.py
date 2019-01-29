import os
import pickle
from typing import Any


settings_file_name = "settings.pkl"


def new_project(project_name: str) -> None:
    """
    Creates a new project folder, and the necessary project files.

    :param project_name: The name of the new project
    """
    if not os.path.exists('projects/' + project_name):
        from datastorage.labelstorage import LabelManager
        from datastorage.subjectmapping import SubjectManager
        os.mkdir('projects/' + project_name)
        Settings(project_name, True)
        LabelManager(project_name).create_tables()
        SubjectManager(project_name).create_table()


class Settings:

    settings_dict = {}

    def __init__(self, project_name: str, is_new_project: bool=False):
        """
        :param project_name: The name of the current project
        :param is_new_project: Boolean indicating if a new settings file should be generated
        """
        self.project_name = project_name
        if is_new_project:
            self.set_setting("subj_map", {})  # mapping from column name chosen by user and column name in database
            self.set_setting("next_col", 0)   # next index to use in the database column for subject mapping
            self.set_setting("formulas", {})  # user-made formulas. mapping from function name to regular expression
            self.set_setting("label_opacity", 50)  # opacity of the label highlights
            self.set_setting("plot_width", 20)  # the width of the data plot in seconds
        else:
            self.load()

    def load(self) -> None:
        """Loads the saved setting dictionary back into this class from a file"""
        f = open(self._get_path(), 'rb')
        self.settings_dict = pickle.load(f)
        f.close()

    def save(self) -> None:
        """Saves the current settings dictionary to a file"""
        f = open(self._get_path(), 'wb')
        pickle.dump(self.settings_dict, f)
        f.close()

    def set_setting(self, setting_name: str, new_value: Any) -> None:
        """
        Adds or changes a setting with the given name.

        :param setting_name: The name of the setting that should be changed
        :param new_value: The value the setting should get
        """
        self.settings_dict[setting_name] = new_value
        self.save()

    def get_setting(self, setting_name: str) -> Any:
        """
        Returns the value of a given setting.

        :param setting_name: The name of the setting
        :return: The value of the setting, or None if the setting is unknown
        """
        return self.settings_dict.get(setting_name, None)

    def _get_path(self) -> str:
        """
        Returns the path to the settings file relative to the root directory

        :return: The path to the settings file
        """
        return 'projects/' + self.project_name + '/' + settings_file_name
