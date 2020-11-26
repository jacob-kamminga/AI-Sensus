from sqlite3 import IntegrityError

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

from database.label_type_manager import LabelTypeManager
from gui.designer.label_settings import Ui_Dialog
from gui.dialogs.project_settings import ProjectSettingsDialog


class LabelSettingsDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, label_type_manager: LabelTypeManager, settings: ProjectSettingsDialog):
        super().__init__()
        self.setupUi(self)
        self.label_type_manager = label_type_manager
        self.settings = settings

        self.settings_changed = False

        opacity = settings.get_setting("label_opacity")
        colors = ['blue', 'deepskyblue', 'cyan', 'green', 'lime', 'red', 'yellow', 'orange', 'magenta', 'grey', 'black']

        self.comboBox_color.addItems(colors)
        self.comboBox_new_label_color.addItems(colors)
        self.doubleSpinBox_opacity.setValue(opacity)

        self.label_type_dict = dict()
        self.color_dict = dict()

        for row in self.label_type_manager.get_all_label_types():
            id_ = row["id"]
            activity = row["activity"]
            color = row["color"]
            description = row["description"]
            keyboard_shortcut = row["keyboard_shortcut"]

            self.label_type_dict[activity] = {"id": id_,
                                              "color": color,
                                              "description": description,
                                              "keyboard_shortcut": keyboard_shortcut}
            self.color_dict[activity] = color

        self.comboBox_label.addItems(self.label_type_dict.keys())

        if len(self.label_type_dict) > 0:
            current_label = self.comboBox_label.currentText()
            current_color = self.color_dict[current_label]
            self.comboBox_color.setCurrentText(current_color)
            current_keyboard_shortcut = self.label_type_manager.get_keyboard_shortcut(current_label)
            self.lineEdit_keyboard_shortcut.setText(current_keyboard_shortcut)

        self.pushButton_add_label.clicked.connect(self.add_label)
        self.pushButton_delete_label.clicked.connect(self.delete_label)
        self.comboBox_label.currentTextChanged.connect(self.label_changed)
        self.comboBox_color.currentTextChanged.connect(self.color_changed)
        self.lineEdit_keyboard_shortcut.textChanged.connect(self.keyboard_shortcut_changed)
        self.doubleSpinBox_opacity.valueChanged.connect(self.opacity_changed)

    def add_label(self):
        self.settings_changed = True
        new_activity = self.lineEdit_new_label.text()
        new_color = self.comboBox_new_label_color.currentText()
        new_new_keyboard_shortcut = self.lineEdit_new_keyboard_shortcut.text().strip(' ')

        if self.lineEdit_new_label.text():
            try:
                self.label_type_manager.add_label_type(new_activity, new_color, "", new_new_keyboard_shortcut)

            except IntegrityError:
                QMessageBox.warning(self, "Name or shortcut already assigned", "Names and shortcuts must be unique")
                return
            except:
                QMessageBox.warning(self, "Unknown error", "Label was not added")
                return

            self.label_type_dict[new_activity] = {"id": self.label_type_manager.get_id_by_activity(new_activity),
                                                  "color": new_color,
                                                  "description": "",
                                                  "keyboard_shortcut": new_new_keyboard_shortcut}
            self.color_dict[new_activity] = new_color
            self.comboBox_label.clear()
            self.comboBox_label.addItems(self.label_type_dict.keys())
            self.lineEdit_new_keyboard_shortcut.clear()

    def delete_label(self):
        remove_item = self.comboBox_label.currentText()
        if QMessageBox.warning(self,
                               'Heads up!',
                               'Removing the label will remove all annotations associated with it. '
                               'Are you sure you want to delete ' + remove_item + '?',
                               QMessageBox.Ok | QMessageBox.Cancel
                               ) == QMessageBox.Cancel:
            return

        self.settings_changed = True
        self.label_type_manager.delete_label_type(remove_item)
        self.comboBox_label.clear()
        self.label_type_dict.pop(remove_item)
        self.comboBox_label.addItems(self.label_type_dict.keys())
        self.settings_changed = True

    def label_changed(self, text):
        if self.color_dict and self.comboBox_label.count():
            self.comboBox_color.setCurrentText(self.color_dict[text])
        self.lineEdit_keyboard_shortcut.setText(self.label_type_manager.get_keyboard_shortcut(text))

    def color_changed(self, color):
        self.settings_changed = True
        
        if self.comboBox_label.currentText():
            self.label_type_manager.update_color(self.comboBox_label.currentText(), color)
            self.color_dict[self.comboBox_label.currentText()] = color

    def opacity_changed(self, value):
        self.settings_changed = True
        self.settings.set_setting("label_opacity", value)

    def keyboard_shortcut_changed(self, value):
        self.settings_changed = True
        value = value.strip(' ')
        try:
            if value == "":
                value = None
                # self.label_type_manager.remove_keyboard_shortcut(self.comboBox_label.currentText())
            self.label_type_manager.update_keyboard_shortcut(self.comboBox_label.currentText(), value)
        except IntegrityError:
            if value == "":
                return
            existing_mapping = self.label_type_manager.get_activity_by_keyboard_shortcut(value)
            QMessageBox.warning(self, "Shortcut already assigned",
                                "This shortcut is already assigned to: "+existing_mapping)
            self.lineEdit_keyboard_shortcut.clear()


