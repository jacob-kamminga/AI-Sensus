from PyQt5.QtWidgets import QDialog, QErrorMessage

from gui.designer.new_project_name import Ui_Dialog


class NewProject(QDialog, Ui_Dialog):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.project_name = None

    def accept(self):
        self.project_name = self.lineEdit_name.text()

        if self.project_name != "":
            super().accept()
        else:
            error_dialog = QErrorMessage()
            error_dialog.showMessage("Project name cannot be empty.")
            error_dialog.exec()
