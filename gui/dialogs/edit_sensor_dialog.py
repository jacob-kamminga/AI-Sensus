import pytz
from PyQt5 import QtWidgets

from controllers.sensor_controller import SensorController
from database.models import Sensor
from gui.designer.edit_sensor import Ui_Dialog

INDEX_MAP_ID = 0
INDEX_MAP_SUBJECT = 1
INDEX_MAP_SENSOR = 2
INDEX_MAP_START = 3
INDEX_MAP_END = 4

DT_FORMAT = '%Y-%m-%d %H:%M:%S'


class EditSensorDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, sensor_controller: SensorController, sensor: Sensor):
        super().__init__()
        self.setupUi(self)
        self.init_gui()

        self.sensor_controller = sensor_controller
        self.sensor = sensor
        self.value_changed = False
        self.saved = False

        # Fill the fields with the sensor that is currently selected
        self.load_sensor()

        self.comboBox_timezone.currentIndexChanged.connect(self.on_value_changed)
        self.buttonBox.accepted.connect(self.on_accepted)

    def init_gui(self) -> None:
        """ Initializes the GUI. """
        self.comboBox_timezone.addItems(pytz.common_timezones)

    def load_sensor(self):
        self.label_sensor_id_val.setText(self.sensor.name)
        self.comboBox_timezone.setCurrentText(self.sensor.timezone)

    def on_value_changed(self) -> None:
        self.value_changed = True

    def on_accepted(self):
        if self.value_changed:
            selected_timezone = self.comboBox_timezone.currentText()
            self.saved = self.sensor_controller.edit_sensor(self.sensor, selected_timezone)
