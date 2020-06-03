from PyQt5 import QtWidgets

from database.db_sensor import SensorManager
from gui.designer_edit_sensor import Ui_Dialog

INDEX_MAP_ID = 0
INDEX_MAP_SUBJECT = 1
INDEX_MAP_SENSOR = 2
INDEX_MAP_START = 3
INDEX_MAP_END = 4

DT_FORMAT = '%Y-%m-%d %H:%M:%S'


class EditSensorDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self,
                 sensor_manager: SensorManager,
                 sensors_dict: dict,
                 sensor_id: int):
        super().__init__()
        self.setupUi(self)

        self.sensor_manager = sensor_manager
        self.sensors_dict = sensors_dict
        self.sensor_id = sensor_id

        self.sensor_edited = False
        self.old_sensor_name = None

        self.set_current_sensor()

        self.buttonBox.accepted.connect(self.edit)

    def set_current_sensor(self):
        sensor_name = self.sensors_dict[self.sensor_id]
        self.label_old_id_val.setText(sensor_name)
        self.old_sensor_name = sensor_name

    def edit(self):
        sensor_name = self.lineEdit_new_id_val.text()

        if sensor_name != self.old_sensor_name:
            self.sensor_manager.update_name_by_id(self.sensor_id, sensor_name)
            self.sensor_edited = True
