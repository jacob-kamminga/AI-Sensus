import json
import sys
from os import getenv
from pathlib import Path
from PyQt5.QtWidgets import QMessageBox
from constants import APP_CONFIG_FILE, PREVIOUS_PROJECT_DIR, PROJECTS, PROJECT_NAME, PROJECT_DIR
from controllers.project_controller import INIT_APP_CONFIG


def user_data_dir(file_name):
    r"""
    Get OS specific data directory path for LabelingApp.
    Typical user data directories are:
        macOS:    ~/Library/Application Support/LabelingApp
        Unix:     ~/.local/share/LabelingApp   # or in $XDG_DATA_HOME, if defined
        Win 10:   C:\Users\<username>\AppData\Roaming\LabelingApp
    For Unix, we follow the XDG spec and support $XDG_DATA_HOME if defined.
    :param file_name: file to be fetched from the data dir
    :return: full path to the user-specific data dir
    """
    # get os specific path
    if sys.platform.startswith("win"):
        os_path = getenv("APPDATA")
    elif sys.platform.startswith("darwin"):
        os_path = "~/Library/Application Support"
    else:
        # linux
        os_path = getenv("XDG_DATA_HOME", "~/.local/share")

    # join with LabelingApp dir
    path = Path(os_path) / "Labeling App MVC"

    return path.expanduser() / file_name


class AppController:

    def __init__(self, gui, app_config_file):
        self.gui = gui
        self.project_name = None
        self.project_dir = None
        self.prev_project_dir = None

        self.app_config_file = app_config_file if app_config_file is not None else user_data_dir(APP_CONFIG_FILE)
        self.app_config = {}

        try:
            self.load_settings()
        except CorruptAppConfigError:
            self.app_config_file.unlink()  # Delete app_config.json so that it can be recreated properly.
            self.load_settings()
        except MissingProjectDirectoryError as e:
            QMessageBox.critical(self.gui, "Project directory is missing",
                                 f"The directory \"{e.directory}\" could not be found. If you deleted the directory, "
                                 f"you can ignore this.")

    def save_app_config(self):
        """Write the app configuration dictionary in JSON format to the user directory."""
        with self.app_config_file.open('w') as f:
            json.dump(self.app_config, f)

    def save_project_in_app_config(self):
        """
        Save the project name and directory to the app configuration file. These should both be set to the appropriate
        values in the project controller.
        """
        self.app_config.setdefault(PROJECTS, []).append({
            PROJECT_NAME: self.gui.project_controller.project_name,
            PROJECT_DIR: str(self.gui.project_controller.project_dir)
        })
        self.app_config[PREVIOUS_PROJECT_DIR] = str(self.gui.project_controller.project_dir)
        self.save_app_config()

    def load_settings(self):
        """
        Try to retrieve the previous project path, and open the project in that path if possible.
        """

        if self.app_config_file.is_file():  # Check if app config file exists.
            with self.app_config_file.open() as f:
                self.app_config = json.load(f)

                # If the app config contains no information, raise CorruptAppConfigError
                if self.app_config == INIT_APP_CONFIG:
                    raise CorruptAppConfigError()

            # Check if previous project directory exists.
            prev_project_dir = Path(self.app_config.get(PREVIOUS_PROJECT_DIR))

            if prev_project_dir.is_dir():
                self.prev_project_dir = prev_project_dir
            else:
                raise MissingProjectDirectoryError(prev_project_dir)
        else:  # If there is no app_config.json in the user directory, create one.
            self.create_app_config()

    def create_app_config(self):
        """Create the app configuration file in the user directory."""
        # Create empty application config file
        self.app_config_file.parent.mkdir(exist_ok=True)
        self.app_config_file.touch()

        with self.app_config_file.open('w') as f:
            json.dump(INIT_APP_CONFIG, f)


class MissingProjectDirectoryError(Exception):
    """
    This error is raised when the previous project directory is missing.
    """
    def __init__(self, directory):
        self.directory = directory


class CorruptAppConfigError(Exception):
    """
    This error is raised when the app_config.json's content is equal to INIT_APP_CONFIG.
    In other words, there is no information there, but it has been initialised. This means a project was in the process
    of being created, but was interrupted.
    """
    pass
