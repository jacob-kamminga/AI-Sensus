from PyQt5 import QtWidgets
from gui.designer_machine_learning import Ui_Dialog


class MachineLearningDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, columns):
        super().__init__()
        self.setupUi(self)
        self.is_accepted = False
        self.column_dict = dict()
        for column in columns:
            self.column_dict[column] = False
        self.runButton.clicked.connect(self.activate)
        self.cancelButton.clicked.connect(self.close)
        self.checkBox.toggled.connect(self.add_column)
        self.comboBox.currentTextChanged.connect(self.switch_column)
        self.comboBox.addItems(columns)

    def activate(self):
        self.is_accepted = True
        self.accept()

    def add_column(self, event):
        self.column_dict[self.comboBox.currentText()] = event

    def switch_column(self):
        self.checkBox.setChecked(self.column_dict[self.comboBox.currentText()])
