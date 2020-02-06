import sqlite3

SQL_CREATE_TABLE = "create table sensor \
( \
  id          INTEGER not null \
    constraint sensor_pk \
      primary key autoincrement, \
  sensor_name TEXT    not null \
); \
 \
create unique index sensor_sensor_id_uindex \
  on sensor (sensor_name);"

SQL_INSERT_SENSOR = "INSERT INTO sensor(sensor_name) VALUES (?)"
SQL_SELECT_ID = "SELECT id FROM sensor WHERE sensor_name = ?"
SQL_SELECT_SENSOR_NAME = "SELECT sensor_name FROM sensor WHERE id = ?"


class SensorManager:

    def __init__(self, project_name: str):
        """
        :param project_name: The name of the current project
        """
        self.project_name = project_name
        self._conn = sqlite3.connect('projects/' + project_name + '/project_data.db',
                                     detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self._cur = self._conn.cursor()

    def create_table(self) -> bool:
        """Method for creating the necessary label tables in the database."""
        try:
            c = self._conn.cursor()
            c.execute(SQL_CREATE_TABLE)
            self._conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_id(self, sensor_name: str) -> int:
        try:
            self._cur.execute(SQL_SELECT_ID, (sensor_name,))
            return self._cur.fetchone()[0]
        except sqlite3.Error:
            return -1

    def get_sensor_name(self, id_: int) -> str:
        try:
            self._cur.execute(SQL_SELECT_ID, (id_,))
            return self._cur.fetchone()[0]
        except sqlite3.Error:
            return ""

    def insert_sensor(self, sensor_name: str) -> int:
        try:
            self._cur.execute(SQL_INSERT_SENSOR, (sensor_name,))
            self._conn.commit()
            return self.get_id(sensor_name)
        except sqlite3.Error:
            return -1
