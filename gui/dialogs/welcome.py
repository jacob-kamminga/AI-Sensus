import json
import sqlite3

from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import QDialog, QFileDialog

from constants import APP_CONFIG_FILE, PREVIOUS_PROJECT_DIR, PROJECTS, PROJECT_NAME, PROJECT_DIR, PROJECT_DATABASE_FILE
from database.create_database import create_database
from gui.designer.welcome import Ui_Dialog
from gui.dialogs.new_project import NewProject
from project_settings import ProjectSettings


INIT_APP_CONFIG = {
    PREVIOUS_PROJECT_DIR: "",
    PROJECTS: []
}


class Welcome(QDialog, Ui_Dialog):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.settings: Optional[ProjectSettings] = None
        self.app_config_file = Path.cwd().joinpath(APP_CONFIG_FILE)
        self.app_config = {}

        self.load_settings()

        self.pushButton_new_project.pressed.connect(self.open_new_project_dialog)
        self.pushButton_load_project.pressed.connect(self.open_existing_project_dialog)

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

    def open_new_project_dialog(self):
        """
        Open the new project name dialog.
        """
        new_project_dialog = NewProject()
        new_project_dialog.exec()
        project_name = new_project_dialog.project_name

        if project_name:
            project_dir = QFileDialog.getExistingDirectory(
                self,
                "Select new project directory...",
                options=QFileDialog.ShowDirsOnly
            )

            if project_dir:
                self.settings = ProjectSettings(Path(project_dir))

                # Create database
                try:
                    conn = sqlite3.connect(Path(project_dir).joinpath(PROJECT_DATABASE_FILE).as_posix())
                    create_database(conn)
                except sqlite3.Error as e:
                    print(e)

                # Save project in app config
                self.app_config.setdefault(PROJECTS, []).append({
                    PROJECT_NAME: project_name,
                    PROJECT_DIR: project_dir
                })
                self.app_config[PREVIOUS_PROJECT_DIR] = project_dir
                self.save_app_config()

                self.close()

    def open_existing_project_dialog(self):
        """
        Open dialog for selecting an existing project.
        """
        project_dir = QFileDialog.getExistingDirectory(
            self,
            "Select existing project directory...",
            options=QFileDialog.ShowDirsOnly
        )

        if project_dir:
            self.settings = ProjectSettings(Path(project_dir))

            # Set project dir as most recent project dir
            self.app_config[PREVIOUS_PROJECT_DIR] = project_dir
            self.save_app_config()

            self.close()

    def save_app_config(self):
        with self.app_config_file.open('w') as f:
            json.dump(self.app_config, f)
