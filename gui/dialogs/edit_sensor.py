import pytz
from PyQt5 import QtWidgets

from database.sensor_manager import SensorManager
from gui.designer.edit_sensor import Ui_Dialog

INDEX_MAP_ID = 0
INDEX_MAP_SUBJECT = 1
INDEX_MAP_SENSOR = 2
INDEX_MAP_START = 3
INDEX_MAP_END = 4

DT_FORMAT = '%Y-%m-%d %H:%M:%S'


class EditSensorDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(
            self,
            sensor_manager: SensorManager,
            sensor_id: int,
            sensor_name: str
    ):
        super().__init__()
        self.setupUi(self)

        self.sensor_manager = sensor_manager
        self.sensor_id = sensor_id
        self.sensor_name = sensor_name

        self.sensor_edited = False
        self.old_timezone = None
        self.new_timezone = None

        # Fill the combobox with timezones
        self.comboBox_timezone.addItems(pytz.common_timezones)

        # Fill the fields with the sensor that is currently selected
        self.load_sensor()

        self.buttonBox.accepted.connect(self.save_to_db)

    def load_sensor(self):
        timezone = self.sensor_manager.get_timezone_by_id(self.sensor_id)  # TODO: Fix bug when opening sensor data file

        self.label_sensor_id_val.setText(self.sensor_name)
        self.old_timezone = timezone
        self.comboBox_timezone.setCurrentText(timezone)

    def save_to_db(self):
        self.new_timezone = self.comboBox_timezone.currentText()

        if self.new_timezone != self.old_timezone:
            self.sensor_manager.update_timezone_by_id(self.sensor_id, self.new_timezone)
            self.sensor_edited = True
