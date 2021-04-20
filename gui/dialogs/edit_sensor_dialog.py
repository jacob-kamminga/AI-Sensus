import pytz
from PyQt5 import QtWidgets

from database.models import Sensor
from gui.designer.edit_sensor import Ui_Dialog

INDEX_MAP_ID = 0
INDEX_MAP_SUBJECT = 1
INDEX_MAP_SENSOR = 2
INDEX_MAP_START = 3
INDEX_MAP_END = 4

DT_FORMAT = '%Y-%m-%d %H:%M:%S'


class EditSensorDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, sensor: Sensor):
        super().__init__()
        self.setupUi(self)

        self.sensor = sensor
        self.saved = False

        # Fill the combobox with timezones
        self.comboBox_timezone.addItems(pytz.common_timezones)

        # Fill the fields with the sensor that is currently selected
        self.load_sensor()

        self.buttonBox.accepted.connect(self.save_to_db)

    def load_sensor(self):
        self.label_sensor_id_val.setText(self.sensor.name)
        self.comboBox_timezone.setCurrentText(self.sensor.timezone)

    def save_to_db(self):
        selected_timezone = self.comboBox_timezone.currentText()

        if selected_timezone != self.sensor.timezone:
            self.sensor.timezone = selected_timezone
            rows_modified = self.sensor.save()
            self.saved = rows_modified > 0
