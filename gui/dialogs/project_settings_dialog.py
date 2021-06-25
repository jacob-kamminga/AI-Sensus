import json
from pathlib import Path
from typing import Any

import pytz
from PyQt5.QtWidgets import QDialog

from constants import PREVIOUS_SENSOR_DATA_FILE, PLOT_HEIGHT_FACTOR
from gui.designer.project_settings import Ui_Dialog

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


class ProjectSettingsDialog(QDialog, Ui_Dialog):

    def __init__(self, gui):
        super().__init__()
        self.setupUi(self)
        self.project_controller = gui.project_controller

        self.comboBox_timezone.addItems(pytz.common_timezones)
        self.comboBox_timezone.setCurrentText("UTC")
        self.comboBox_timezone.currentTextChanged.connect(self.save_timezone)
        self.buttonBox.accepted.connect(self.project_controller.save)

    def create_new_project(self):
        self.project_controller.create_new_project()
        self.load_timezone()

    def load_timezone(self):
        self.comboBox_timezone.setCurrentText(self.project_controller.get_setting('timezone'))

    def save_timezone(self, timezone):
        self.project_controller.set_setting('timezone', timezone)
