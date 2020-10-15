import json
from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import QDialog

from constants import PREVIOUS_PROJECT_DIR, PROJECTS
from gui.designer.welcome import Ui_Dialog
from project_settings import ProjectSettingsDialog

INIT_APP_CONFIG = {
    PREVIOUS_PROJECT_DIR: "",
    PROJECTS: []
}


class Welcome(QDialog, Ui_Dialog):

    def __init__(self, gui):
        super().__init__()
        self.setupUi(self)
        self.gui = gui

        self.settings: Optional[ProjectSettingsDialog] = None
        self.load_settings()

        self.pushButton_new_project.pressed.connect(gui.open_new_project_dialog)
        self.pushButton_new_project.released.connect(self.close)
        self.pushButton_load_project.pressed.connect(gui.open_existing_project_dialog)
        self.pushButton_load_project.released.connect(self.close)

    def load_settings(self):
        # Check if application config file exists
        if self.gui.app_config_file.is_file():
            with self.gui.app_config_file.open() as f:
                self.gui.app_config = json.load(f)

            if self.gui.app_config.get(PREVIOUS_PROJECT_DIR):
                prev_project_dir = Path(self.gui.app_config.get(PREVIOUS_PROJECT_DIR))

                # Check if previous project directory exists
                if prev_project_dir.is_dir():
                    self.settings = ProjectSettingsDialog(prev_project_dir)

        else:
            # Create empty application config file
            self.gui.app_config_file.touch()

            with self.gui.app_config_file.open('w') as f:
                json.dump(INIT_APP_CONFIG, f)

    # def save_app_config(self):
    #     with self.app_config_file.open('w') as f:
    #         json.dump(self.app_config, f)
