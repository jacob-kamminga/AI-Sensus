from peewee import IntegrityError

import peewee
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

from controllers.annotation_controller import NonUniqueShortcutException, NonUniqueActivityNameException
from database.models import LabelType, Label
from gui.designer.label_settings import Ui_Dialog


class LabelSettingsDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, gui):
        super().__init__()
        self.setupUi(self)
        self.gui = gui

        self.settings_changed = False

        opacity = gui.project_controller.get_setting("label_opacity")
        colors = ['blue', 'deepskyblue', 'cyan', 'green', 'lime', 'red', 'yellow', 'orange', 'magenta', 'grey', 'black']

        self.comboBox_color.addItems(colors)
        self.comboBox_new_label_color.addItems(colors)
        self.doubleSpinBox_opacity.setValue(opacity)

        self.label_type_dict = dict()
        self.color_dict = dict()

        for label_type in LabelType.select().dicts():
            id_ = label_type["id"]
            activity = label_type["activity"]
            color = label_type["color"]
            description = label_type["description"]
            keyboard_shortcut = label_type["keyboard_shortcut"]

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
            current_keyboard_shortcut = LabelType.get(LabelType.activity == current_label).keyboard_shortcut
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
        new_keyboard_shortcut = self.lineEdit_new_keyboard_shortcut.text().strip()

        if new_activity and new_color:
            try:
                self.gui.annotation_controller.save_label_to_db(new_activity, new_color, new_keyboard_shortcut)

            except NonUniqueShortcutException as e:
                QMessageBox.warning(self, "Shortcut already assigned",
                                    f"The shortcut \'{e.shortcut}\' is already assigned to "
                                    f"the activity \"{e.activity}\".")
                return
            except NonUniqueActivityNameException as e:
                QMessageBox.warning(self, "Activity name already assigned",
                                    f"The activity \"{e.activity}\" already exists.")
                return

            self.label_type_dict[new_activity] = {"id": LabelType.get(LabelType.activity == new_activity).id,
                                                  "color": new_color,
                                                  "description": "",
                                                  "keyboard_shortcut": new_keyboard_shortcut}
            self.color_dict[new_activity] = new_color
            self.comboBox_label.clear()
            self.comboBox_label.addItems(self.label_type_dict.keys())
            self.lineEdit_new_keyboard_shortcut.clear()

    def delete_label(self):
        activity = self.comboBox_label.currentText()
        if QMessageBox.warning(self,
                               'Heads up!',
                               'Removing the label will remove all annotations associated with it. '
                               f'Are you sure you want to delete the label \"{activity}\"?',
                               QMessageBox.Ok | QMessageBox.Cancel
                               ) == QMessageBox.Cancel:
            return

        self.settings_changed = True
        self.gui.annotation_controller.remove_label(activity)

        self.comboBox_label.clear()
        self.label_type_dict.pop(activity)
        self.comboBox_label.addItems(self.label_type_dict.keys())
        self.settings_changed = True

    def label_changed(self, activity):
        if self.color_dict and self.comboBox_label.count():
            self.comboBox_color.setCurrentText(self.color_dict[activity])
            self.lineEdit_keyboard_shortcut.setText(LabelType.get(LabelType.activity == activity).keyboard_shortcut)

    def color_changed(self, color):
        self.settings_changed = True
        activity = self.comboBox_label.currentText()

        if activity is not None:
            label_type = LabelType.get(LabelType.activity == activity)
            label_type.color = color
            label_type.save()
            self.color_dict[activity] = color

    def opacity_changed(self, value):
        self.settings_changed = True
        self.gui.project_controller.set_setting("label_opacity", value)

    def keyboard_shortcut_changed(self, keyboard_shortcut) -> None:
        '''
        Called when an existing activity's keyboard shortcut is changed in the label setting dialog.
        This method ensures that removal of the existing shortcut is handled properly.

        :param keyboard_shortcut: the character that has replaced the existing shortcut.
        :return:
        '''
        self.settings_changed = True
        activity = self.comboBox_label.currentText()

        if activity != '':
            keyboard_shortcut = keyboard_shortcut.strip()  # A space will become None and so isn't a valid shortcut.
            try:
                if keyboard_shortcut == "":
                    keyboard_shortcut = None
                label_type = LabelType.get(LabelType.activity == activity)
                label_type.keyboard_shortcut = keyboard_shortcut
                label_type.save()
            except IntegrityError:
                # This will be thrown whenever no shortcut is given, since all activities without a shortcut will
                # all have the SAME shortcut: "None", which is non-unique, thus raising an IntegrityError.
                if keyboard_shortcut is None:
                    return
                else:
                    activity_with_shortcut = LabelType.get(LabelType.keyboard_shortcut == keyboard_shortcut).activity
                    QMessageBox.warning(self, "Shortcut already assigned",
                                        f"The shortcut \'{keyboard_shortcut}\' is already assigned to "
                                        f"the activity \"{activity_with_shortcut}\".")
                    self.lineEdit_keyboard_shortcut.clear()
