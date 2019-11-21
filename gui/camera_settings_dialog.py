from PyQt5 import QtWidgets
from gui.designer_camera_settings import Ui_Dialog


class CameraSettingsDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
