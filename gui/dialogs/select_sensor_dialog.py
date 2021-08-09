from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

from database.models import SensorDataFile, Sensor
from gui.designer.select_sensor import Ui_Dialog
from gui.dialogs.edit_sensor_dialog import EditSensorDialog
from gui.dialogs.sensor_model_dialog import SensorModelDialog
from peewee import OperationalError, DoesNotExist

SENSOR_ID_INDEX = 0
SENSOR_NAME_INDEX = 1
SENSOR_TIMEZONE_INDEX = 3


class SelectSensorDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, gui):
        super().__init__()
        self.setupUi(self)

        self.sensor_controller = gui.sensor_controller
        self.selected_sensor_id = None
        self.selected_sensor_name = None
        self.sensor_model_id = None

        # Fill sensor dictionary and add sensor names to combobox
        self.sensor_dict = dict()
        if self.sensor_controller is not None:
            if self.sensor_controller.sensor_data is not None:
                self.load_sensors(self.sensor_controller.sensor_data.metadata.sensor_name)
            else:
                self.load_sensors()

        # Connect UI elements
        self.pushButton_new_sensor.setEnabled(False)
        self.pushButton_new_sensor.clicked.connect(self.add_sensor)
        self.pushButton_use_sensor.clicked.connect(self.use_sensor)
        self.pushButton_edit_sensor.clicked.connect(self.edit_sensor)
        self.pushButton_cancel_select_sensor.clicked.connect(self.close)
        self.pushButton_delete_sensor.clicked.connect(self.delete_sensor)
        self.lineEdit_new_sensor_name.textChanged.connect(self.toggle_add_sensor_pushbutton)

    def add_sensor(self):
        new_sensor_name = self.lineEdit_new_sensor_name.text()
        if new_sensor_name != '':
            # Get the id of the current SensorModel, i.e. the SensorModel that is associated with the current
            # SensorDataFile.
            try:
                sdf = SensorDataFile.get(SensorDataFile.file_id_hash == self.sensor_controller.file_id_hash)
                self.sensor_model_id = sdf.sensor.model.id
            except DoesNotExist:
                # Something went wrong in finding the right SensorModel, so prompt the user to fix it manually.
                dialog = SensorModelDialog()
                dialog.exec()
                dialog.show()
                self.sensor_model_id = dialog.selected_model_id
                if self.sensor_model_id is None:
                    print('[select_sensor_dialog.py]: self.sensor_model_id is None')
                    # TODO: Show warning to user

            # Prompt user for timezone of sensor
            sensor = Sensor(name=new_sensor_name, model=self.sensor_model_id)
            dialog = EditSensorDialog(sensor)
            dialog.exec()

            if dialog.saved:
                self.comboBox_sensor.addItem(new_sensor_name)
                self.comboBox_sensor.setCurrentText(new_sensor_name)
                self.lineEdit_new_sensor_name.clear()

    def use_sensor(self):
        self.selected_sensor_name = self.comboBox_sensor.currentText()

        if self.selected_sensor_name:
            self.selected_sensor_id = Sensor.get(Sensor.name == self.selected_sensor_name).id
            self.close()

    def edit_sensor(self):
        sensor_name = self.comboBox_sensor.currentText()
        if sensor_name:
            sensor = Sensor.get(Sensor.name == sensor_name)
            dialog = EditSensorDialog(sensor)
            dialog.exec()

            self.load_sensors(sensor_name)

    def load_sensors(self, selected_sensor_name=None):
        self.comboBox_sensor.clear()
        sensors = Sensor.select()

        try:
            for sensor in sensors:
                self.comboBox_sensor.addItem(sensor.name)
        except OperationalError as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Different version error")
            msg.setText("Error: " + str(e))
            msg.setInformativeText("Please use the app version that was also used to create this project.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return False

        # Select current sensor in combobox
        if selected_sensor_name:
            self.comboBox_sensor.setCurrentText(selected_sensor_name)

    def delete_sensor(self):
        selected_sensor_name = self.comboBox_sensor.currentText()

        if selected_sensor_name:
            res = QMessageBox(
                QMessageBox.Warning,
                'Heads up!',
                'Are you sure you want to delete ' + selected_sensor_name + '?',
                QMessageBox.Ok | QMessageBox.Cancel
            ).exec()
# todo delete selected sensor
            # if res == QMessageBox.Ok:
            #     sensor_id = self.sensor_data_file.sensor_manager.get_sensor_id(selected_sensor_name)
            #     # First delete all videos that assigned this sensor to it
            #     self.video_manager.delete_video(sensor_id)
            #     # Delete sensor
            #     self.sensor_data_file.sensor_manager.delete_sensor(sensor_id)
            #     self.comboBox_sensor.removeItem(self.comboBox_sensor.findText(selected_sensor_name))

    def toggle_add_sensor_pushbutton(self):
        if self.lineEdit_new_sensor_name.text() == '':
            self.pushButton_new_sensor.setEnabled(False)
        else:
            self.pushButton_new_sensor.setEnabled(True)
