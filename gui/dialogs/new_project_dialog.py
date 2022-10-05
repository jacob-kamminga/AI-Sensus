from PyQt5.QtWidgets import QDialog, QErrorMessage, QMessageBox

from gui.designer.new_project_name import Ui_Dialog


class NewProjectDialog(QDialog, Ui_Dialog):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.project_name = None

    def accept(self):
        """Called when pressing OK on the Project Name dialog"""
        self.project_name = self.lineEdit_name.text()

        if self.project_name != '':
            super().accept()
        else:
            QMessageBox(
                QMessageBox.Warning,
                'Project name missing',
                'Project name cannot be empty.',
                QMessageBox.Ok
            ).exec()
