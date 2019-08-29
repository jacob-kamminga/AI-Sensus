from datetime import datetime

from PyQt5 import QtWidgets

from datastorage.labelstorage import LabelManager
from gui.designer_labelspecs import Ui_LabelSpecs


class LabelSpecs(QtWidgets.QDialog, Ui_LabelSpecs):

    def __init__(self, project_name, serial_number, label_manager: LabelManager):
        super().__init__()
        # Initialize the generated UI from designer_gui.py.
        self.setupUi(self)

        self.serial_number = serial_number
        self.label = Label()
        self.dateTimeEdit_start.dateTimeChanged.connect(self.start_changed)
        self.dateTimeEdit_end.dateTimeChanged.connect(self.stop_changed)
        self.label_manager = LabelManager(project_name)
        self.accepted.connect(self.send_label)
        self.comboBox_labels.currentTextChanged.connect(self.label_changed)
        self.is_accepted = False
        self.label_manager = label_manager

        if label_manager.get_label_types():
            self.label.label = label_manager.get_label_types()[0][0]

        for label in label_manager.get_label_types():
            self.comboBox_labels.addItem(label[0])

    def start_changed(self, value):
        self.label.start = value.toPyDateTime()

    def stop_changed(self, value):
        self.label.end = value.toPyDateTime()

    def label_changed(self, label):
        self.label.label = label

    def send_label(self):
        if not self.label.label == '':
            self.label_manager.add_label(self.label.start, self.label.end, str(self.label.label), self.serial_number)
            self.is_accepted = True


class Label:

    def __init__(self):
        self.label = ''
        self.start = None
        self.end = None

    def setLabel(self, name: str):
        self.label = name

    def setStart(self, start: datetime):
        self.start = start

    def setEnd(self, end: datetime):
        self.end = end
