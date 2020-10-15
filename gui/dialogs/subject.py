from pathlib import Path

from PyQt5 import QtWidgets

from database.subject_manager import SubjectManager
from gui.designer.subject import Ui_Dialog
from gui.dialogs.new_subject import NewSubjectDialog
from project_settings import ProjectSettingsDialog

SUBJECT_NAME_INDEX = 1
SUBJECT_COLOR_INDEX = 2
SUBJECT_SIZE_INDEX = 3
SUBJECT_EXTRA_INFO_INDEX = 4


class SubjectDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, settings: ProjectSettingsDialog):
        super().__init__()
        self.setupUi(self)

        self.subject_manager = SubjectManager(settings)
        self.subjects = dict()

        # Fill the subjects dictionary
        for subject in self.subject_manager.get_all_subjects():
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
        self.pushButton_add_subject.clicked.connect(self.open_new_subject_dialog)

    def fill_subject_combobox(self):
        self.comboBox.addItems(self.subjects.keys())

    def fill_subject_info(self, subject_name: str):
        if subject_name != "" and self.subjects:
            self.label_name_val.setText(subject_name)
            self.label_color_val.setText(self.subjects[subject_name]['color'])
            self.label_size_val.setText(self.subjects[subject_name]['size'])
            self.plainTextEdit_extra_info.setPlainText(self.subjects[subject_name]['extra_info'])

    def open_new_subject_dialog(self):
        """
        Opens the new subject dialog window.
        """
        dialog = NewSubjectDialog(self.subject_manager)
        dialog.exec()
        dialog.show()

        name = dialog.new_subject_name
        color = dialog.new_subject_color
        size = dialog.new_subject_size
        extra_info = dialog.new_subject_extra_info

        if dialog.accepted and dialog.new_subject_name is not None:
            # Add new subject to subject dictionary
            self.subjects[name] = {'color': color, 'size': size, 'extra_info': extra_info}

            # Add new subject to combobox
            self.comboBox.addItem(dialog.new_subject_name)

            # Select the new subject
            self.comboBox.setCurrentText(name)
            self.fill_subject_info(name)
