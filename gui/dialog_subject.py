from PyQt5 import QtWidgets

from database.db_subject import SubjectManager
from gui.designer_subject import Ui_Subject_Dialog

SUBJECT_NAME_INDEX = 0
SUBJECT_COLOR_INDEX = 1
SUBJECT_SIZE_INDEX = 2
SUBJECT_EXTRA_INFO_INDEX = 3


class SubjectDialog(QtWidgets.QDialog, Ui_Subject_Dialog):

    def __init__(self, project_name):
        super().__init__()
        self.setupUi(self)

        self.subject_manager = SubjectManager(project_name)
        self.subjects = dict()

        # Fill the subjects dictionary
        for subject in self.subject_manager.get_subjects():
            name = subject[SUBJECT_NAME_INDEX]
            color = subject[SUBJECT_COLOR_INDEX]
            size = subject[SUBJECT_SIZE_INDEX]
            extra_info = subject[SUBJECT_EXTRA_INFO_INDEX]

            self.subjects[name] = {'color': color, 'size': size, 'extra_info': extra_info}

        # Fill the subject combobox
        self.fill_subject_combobox()

        # Initialize the subject info for the current subject
        self.fill_subject_info(self.comboBox.currentText())

        self.comboBox.currentTextChanged.connect(self.fill_subject_info)

    def fill_subject_combobox(self):
        for subject_name in self.subjects.keys():
            self.comboBox.addItem(subject_name)

    def fill_subject_info(self, subject_name: str):
        self.label_name_val.setText(subject_name)
        self.label_color_val.setText(self.subjects[subject_name]['color'])
        self.label_size_val.setText(self.subjects[subject_name]['size'])
        self.plainTextEdit_extra_info.setPlainText(self.subjects[subject_name]['extra_info'])
