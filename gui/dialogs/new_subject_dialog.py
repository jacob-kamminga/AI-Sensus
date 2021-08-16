from PyQt5 import QtWidgets

from database.models import Subject
from gui.designer.new_subject import Ui_Dialog

SUBJECT_NAME_INDEX = 0
SUBJECT_COLOR_INDEX = 1
SUBJECT_SIZE_INDEX = 2
SUBJECT_EXTRA_INFO_INDEX = 3


class NewSubjectDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.new_subject_name = None
        self.new_subject_color = None
        self.new_subject_size = None
        self.new_subject_extra_info = None

        self.is_name_unique = True

        # Hide the duplicate name warning label
        self.label_warning_duplicate_name.setVisible(False)

        # Get the current names to check uniqueness
        self.existing_names = Subject.select(Subject.name)

        # Check whether the entered name already exists (violates UNIQUE constraint)
        self.lineEdit_name.textChanged.connect(self.check_unique)
        # Add the new subject when the 'Ok' button is pressed
        self.buttonBox.accepted.connect(self.add)

    def add(self):
        if self.is_name_unique:
            self.new_subject_name = self.lineEdit_name.text()
            self.new_subject_color = self.lineEdit_color.text()
            self.new_subject_size = self.lineEdit_size.text()
            self.new_subject_extra_info = self.plainTextEdit_extra_info.toPlainText()

            self.gui.annotation_controller.add_subject(self.new_subject_name, self.new_subject_color,
                                                       self.new_subject_size, self.new_subject_extra_info)

    def check_unique(self, name):
        if name in self.existing_names:
            self.is_name_unique = False
            self.label_warning_duplicate_name.setVisible(True)
            self.buttonBox.setDisabled(True)
        else:
            self.is_name_unique = True
            self.label_warning_duplicate_name.setVisible(False)
            self.buttonBox.setEnabled(True)
