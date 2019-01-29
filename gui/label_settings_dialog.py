from PyQt5 import QtWidgets

from gui.designer_labelsettings import Ui_Dialog
from datastorage.labelstorage import LabelManager
from datastorage.settings import Settings


class LabelSettingsDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, label_manager: LabelManager, settings: Settings):
        super().__init__()
        self.setupUi(self)
        self.label_manager = label_manager
        self.settings = settings
        self.accepted.connect(self.add_label)
        self.settings_changed = False
        self.pushButton.clicked.connect(self.delete_label)
        self.comboBox.currentTextChanged.connect(self.label_changed)
        self.comboBox_2.currentTextChanged.connect(self.color_changed)
        self.opacity_box.valueChanged.connect(self.opacity_changed)
        opacity = settings.get_setting("label_opacity")
        colors = ['blue', 'deepskyblue', 'cyan', 'green', 'lime', 'red', 'yellow', 'orange', 'magenta', 'grey', 'black']
        self.comboBox_2.addItems(colors)
        self.comboBox_3.addItems(colors)
        self.opacity_box.setValue(opacity)
        self.color_dict = dict()
        for label in self.label_manager.get_label_types():
            self.comboBox.addItem(label[0])
            self.color_dict[label[0]] = label[1]
        if self.label_manager.get_label_types():
            self.comboBox_2.setCurrentText(self.label_manager.get_label_types()[0][1])

    def add_label(self):
        self.settings_changed = True
        if self.lineEdit.text():
            self.label_manager.add_label_type(self.lineEdit.text(), self.comboBox_3.currentText(), '')

    def delete_label(self):
        self.settings_changed = True
        self.label_manager.delete_label_type(self.comboBox.currentText())
        self.comboBox.clear()
        for label in self.label_manager.get_label_types():
            self.comboBox.addItem(label[0])
            self.color_dict[label[0]] = label[1]
        if self.label_manager.get_label_types():
            self.comboBox_2.setCurrentText(self.label_manager.get_label_types()[0][1])

    def label_changed(self, text):
        if self.color_dict and self.comboBox.count():
            self.comboBox_2.setCurrentText(self.color_dict[text])

    def color_changed(self, color):
        self.settings_changed = True
        if self.comboBox.currentText():
            self.label_manager.update_label_color(self.comboBox.currentText(), color)
            self.color_dict[self.comboBox.currentText()] = color

    def opacity_changed(self, value):
        self.settings_changed = True
        self.settings.set_setting("label_opacity", value)
