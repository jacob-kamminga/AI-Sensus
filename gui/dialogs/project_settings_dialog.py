import pytz
from PyQt5.QtWidgets import QDialog
from gui.designer.project_settings import Ui_Dialog

class ProjectSettingsDialog(QDialog, Ui_Dialog):

    def __init__(self, gui):
        super().__init__()
        self.setupUi(self)
        self.project_controller = gui.project_controller

        self.comboBox_timezone.addItems(pytz.common_timezones)
        self.comboBox_timezone.setCurrentText(self.project_controller.get_setting('timezone'))
        self.buttonBox.accepted.connect(self.save_timezone)
        self.timezone_changed = False
        self.old_timezone = self.comboBox_timezone.currentText()

    def save_timezone(self):
        current_timezone = self.comboBox_timezone.currentText()
        print(self.old_timezone, current_timezone)
        self.timezone_changed = (self.old_timezone != current_timezone)
        if self.timezone_changed:
            self.project_controller.set_setting('timezone', current_timezone)
