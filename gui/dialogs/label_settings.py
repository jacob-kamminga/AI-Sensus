from PyQt5 import QtWidgets

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

            self.label_type_dict[activity] = {"id": id_,
                                              "color": color,
                                              "description": description}
            self.color_dict[activity] = color

        self.comboBox_label.addItems(self.label_type_dict.keys())

        if len(self.label_type_dict) > 0:
            current_label = self.comboBox_label.currentText()
            current_color = self.color_dict[current_label]
            self.comboBox_color.setCurrentText(current_color)

        self.accepted.connect(self.add_label)
        self.pushButton.clicked.connect(self.delete_label)
        self.comboBox_label.currentTextChanged.connect(self.label_changed)
        self.comboBox_color.currentTextChanged.connect(self.color_changed)
        self.doubleSpinBox_opacity.valueChanged.connect(self.opacity_changed)

    def add_label(self):
        self.settings_changed = True

        if self.lineEdit_new_label.text():
            self.label_type_manager.add_label_type(
                self.lineEdit_new_label.text(),
                self.comboBox_new_label_color.currentText(),
                ""
            )

    def delete_label(self):
        # TODO: Fix this function
        self.settings_changed = True
        self.label_type_manager.delete_label_type(self.comboBox_label.currentText())
        self.comboBox_label.clear()

        for label in self.label_type_manager.get_all_label_types():
            self.comboBox_label.addItem(label[0])
            self.color_dict[label[0]] = label[1]

        if self.label_type_manager.get_all_label_types():
            self.comboBox_color.setCurrentText(self.label_manager.get_label_types()[0][1])

    def label_changed(self, text):
        if self.color_dict and self.comboBox_label.count():
            self.comboBox_color.setCurrentText(self.color_dict[text])

    def color_changed(self, color):
        self.settings_changed = True
        
        if self.comboBox_label.currentText():
            self.label_type_manager.update_color(self.comboBox_label.currentText(), color)
            self.color_dict[self.comboBox_label.currentText()] = color

    def opacity_changed(self, value):
        self.settings_changed = True
        self.settings.set_setting("label_opacity", value)
