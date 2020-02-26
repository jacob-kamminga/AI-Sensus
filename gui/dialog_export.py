from PyQt5 import QtWidgets
from gui.designer_export import Ui_Dialog


class ExportDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.is_accepted = False
        self.accepted.connect(self.export)

    def export(self):
        self.is_accepted = True
