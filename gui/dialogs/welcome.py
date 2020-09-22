import json

from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import QDialog, QFileDialog

from constants import APP_CONFIG_FILE, PREVIOUS_PROJECT_DIR, PROJECTS
from gui.designer.welcome import Ui_Dialog

from gui.dialogs.new_project import NewProject
from project_settings import ProjectSettings

INIT_APP_CONFIG = {
    PREVIOUS_PROJECT_DIR: "",
    PROJECTS: []
}


class Welcome(QDialog, Ui_Dialog):

    def __init__(self, gui):
        super().__init__()
        self.setupUi(self)

        self.settings: Optional[ProjectSettings] = None
        # self.app_config_file = Path.cwd().joinpath(APP_CONFIG_FILE)
        # self.app_config = {}
        self.app_config_file = gui.app_config_file
        self.app_config = gui.app_config

        self.load_settings()

        self.pushButton_new_project.pressed.connect(gui.open_new_project_dialog)
        self.pushButton_new_project.released.connect(self.close)
        self.pushButton_load_project.pressed.connect(gui.open_existing_project_dialog)
        self.pushButton_load_project.released.connect(self.close)

    def load_settings(self):
        # Check if application config file exists
        if self.app_config_file.is_file():
            with self.app_config_file.open() as f:
                self.app_config = json.load(f)

            if self.app_config.get(PREVIOUS_PROJECT_DIR):
                prev_project_dir = Path(self.app_config.get(PREVIOUS_PROJECT_DIR))

                # Check if previous project directory exists
                if prev_project_dir.is_dir():
                    self.settings = ProjectSettings(prev_project_dir)

        else:
            # Create empty application config file
            self.app_config_file.touch()

            with self.app_config_file.open('w') as f:
                json.dump(INIT_APP_CONFIG, f)

    # def save_app_config(self):
    #     with self.app_config_file.open('w') as f:
    #         json.dump(self.app_config, f)
