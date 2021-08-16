from PyQt5.QtWidgets import QDialog
from gui.designer.welcome import Ui_Dialog


class WelcomeDialog(QDialog, Ui_Dialog):

    def __init__(self, gui):
        super().__init__()
        self.setupUi(self)
        self.gui = gui

        self.pushButton_new_project.pressed.connect(gui.open_new_project_dialog)
        self.pushButton_new_project.released.connect(self.close)
        self.pushButton_load_project.pressed.connect(gui.open_existing_project_dialog)
        self.pushButton_load_project.released.connect(self.close)
