from PyQt5 import QtWidgets

from constants import *
from gui.designer.new_sensor_model_date import Ui_Dialog
from gui.dialogs.new_sensor_model_id_dialog import SensorModelIdDialog
from gui.dialogs.project_settings_dialog import ProjectSettingsDialog


class SensorModelDateDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, settings: ProjectSettingsDialog, model: {}, model_id=None, test_file=None, parent=None):
        super().__init__()
        self.setupUi(self)
        self.settings = settings
        self.model_id = model_id
        self.test_file = test_file
        self.parent = parent

        self.model = model
        self.fill_existing_data()

        # Load comboBoxes
        self.comboBox_relative_absolute.addItems({
            ABSOLUTE_TIME_ITEM, RELATIVE_TIME_ITEM})
        self.comboBox_timestamp_unit.addItems({  # Units supported by pandas.to_timedelta()
            'days', 'hours', 'minutes', 'seconds', 'milliseconds', 'microseconds', 'nanoseconds',
            FORMAT_STRING_ITEM
        })
        self.comboBox_timestamp_unit.setCurrentText('seconds')

        # Connect UI elements
        self.pushButton_previous.pressed.connect(self.open_previous_dialog)
        self.pushButton_next.pressed.connect(self.open_next_dialog)
        self.checkBox_datetime_metadata.stateChanged.connect(self.toggle_date_time_group)
        self.comboBox_timestamp_unit.currentTextChanged.connect(self.toggle_formatted_string_edit)

    def fill_existing_data(self):
        if self.model[DATE_ROW] is not None and self.model[DATE_ROW] != -1:
            self.spinBox_date_row.setValue(self.model[DATE_ROW] + 1)
            self.checkBox_datetime_metadata.setChecked(True)
            self.groupBox_date_time_row.setEnabled(True)

        if self.model[TIME_ROW] is not None and self.model[TIME_ROW] != -1:
            self.spinBox_time_row.setValue(self.model[TIME_ROW] + 1)

        if self.model[TIMESTAMP_COLUMN]:
            self.spinBox_timestamp_column.setValue(self.model[TIMESTAMP_COLUMN] + 1)

        if self.model[RELATIVE_ABSOLUTE]:
            self.comboBox_relative_absolute.setCurrentText(self.model[RELATIVE_ABSOLUTE])

        if self.model[TIMESTAMP_UNIT]:
            self.comboBox_timestamp_unit.setCurrentText(self.model[TIMESTAMP_UNIT])

        if self.model[FORMAT_STRING]:
            self.lineEdit_timestamp_formatstring.setText(self.model[FORMAT_STRING])

    def open_next_dialog(self):
        # Handle date time group
        if self.checkBox_datetime_metadata.isChecked():
            self.model[DATE_ROW] = self.spinBox_date_row.value() - 1
            self.model[TIME_ROW] = self.spinBox_time_row.value() - 1
        else:
            self.model[DATE_ROW] = -1
            self.model[TIME_ROW] = -1

        # Handle timestamp column group
        self.model[TIMESTAMP_COLUMN] = self.spinBox_timestamp_column.value() - 1
        self.model[RELATIVE_ABSOLUTE] = self.comboBox_relative_absolute.currentText()
        self.model[TIMESTAMP_UNIT] = self.comboBox_timestamp_unit.currentText()
        self.model[FORMAT_STRING] = self.lineEdit_timestamp_formatstring.text()

        dialog = SensorModelIdDialog(
            self.settings,
            self.model,
            model_id=self.model_id,
            test_file=self.test_file,
            parent=self.parent
        )
        self.close()
        dialog.exec()

    def open_previous_dialog(self):
        from gui.dialogs.new_sensor_model_name_dialog import SensorModelNameDialog

        dialog = SensorModelNameDialog(
            self.settings,
            self.model,
            model_id=self.model_id,
            test_file=self.test_file,
            parent=self.parent
        )
        self.close()
        dialog.exec()

    def toggle_date_time_group(self):
        self.groupBox_date_time_row.setEnabled(self.checkBox_datetime_metadata.isChecked())

    def toggle_formatted_string_edit(self):
        state = self.comboBox_timestamp_unit.currentText() == FORMAT_STRING_ITEM
        self.lineEdit_timestamp_formatstring.setEnabled(state)
        self.label_timestamp_formatstring.setEnabled(state)
