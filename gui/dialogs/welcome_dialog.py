import json
from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import QDialog


from gui.designer.welcome import Ui_Dialog
from gui.dialogs.project_settings_dialog import ProjectSettingsDialog


class Welcome(QDialog, Ui_Dialog):

    def __init__(self, gui):
        super().__init__()
        self.setupUi(self)
        self.gui = gui

        # self.settings: Optional[ProjectSettingsDialog] = None
        # self.load_settings()

        self.pushButton_new_project.pressed.connect(gui.open_new_project_dialog)
        self.pushButton_new_project.released.connect(self.close)
        self.pushButton_load_project.pressed.connect(gui.open_existing_project_dialog)
        self.pushButton_load_project.released.connect(self.close)



    # def save_app_config(self):
    #     with self.app_config_file.open('w') as f:
    #         json.dump(self.app_config, f)
