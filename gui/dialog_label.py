import datetime as dt
from typing import Optional

from PyQt5 import QtWidgets

from database.db_label import LabelManager
from database.db_label_type import LabelTypeManager
from gui.designer_labelspecs import Ui_LabelSpecs


class LabelSpecs(QtWidgets.QDialog, Ui_LabelSpecs):

    def __init__(self, sensor_data_file: int, label_manager: LabelManager, label_type_manager: LabelTypeManager):
        super().__init__()
        self.setupUi(self)

        self.sensor_data_file = sensor_data_file
        self.label_manager = label_manager
        self.label_type_manager = label_type_manager

        self.label_type_dict = dict()

        for row in self.label_type_manager.get_all_label_types():
            self.label_type_dict[row["activity"]] = {"id": row["id"],
                                                     "color": row["color"],
                                                     "description": row["description"]}

        self.selected_label = Label()
        self.is_accepted = False

        # Connect methods to listeners
        self.dateTimeEdit_start.dateTimeChanged.connect(self.start_changed)
        self.dateTimeEdit_end.dateTimeChanged.connect(self.stop_changed)
        self.accepted.connect(self.add_label_to_db)
        self.comboBox_labels.currentTextChanged.connect(self.update_label_type)

        self.comboBox_labels.addItems(self.label_type_dict.keys())

    def start_changed(self, value):
        self.selected_label.start = value.toPyDateTime()

    def stop_changed(self, value):
        self.selected_label.end = value.toPyDateTime()

    def update_label_type(self, activity: str):
        self.selected_label.type = self.label_type_dict[activity]["id"]

    def add_label_to_db(self):
        if self.selected_label.type is not None:
            self.label_manager.add_label(self.selected_label.start,
                                         self.selected_label.end,
                                         self.selected_label.type,
                                         self.sensor_data_file)
            self.is_accepted = True


class Label:

    def __init__(self):
        self.type: Optional[int] = None
        self.start: Optional[dt.datetime] = None
        self.end: Optional[dt.datetime] = None
