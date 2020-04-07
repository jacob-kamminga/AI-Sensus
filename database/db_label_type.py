import sqlite3
from typing import List, Tuple, Dict

SQL_CREATE_TABLE_LABEL_TYPE = \
    "create table label_type\
(\
    id          INTEGER not null\
        constraint label_type_pk\
            primary key autoincrement,\
    activity    TEXT    not null,\
    color       TEXT    not null,\
    description TEXT\
);\
\
create unique index label_type_activity_uindex\
    on label_type (activity);"\

SQL_DELETE_LABEL_TYPE = \
    "DELETE FROM label_type " \
    "WHERE activity = ?"

SQL_INSERT_LABEL_TYPE = \
    "INSERT INTO label_type(activity, color, description) VALUES (?, ?, ?)"

SQL_SELECT_ALL_LABEL_TYPES = \
    "SELECT * FROM label_type"

SQL_UPDATE_ACTIVITY = \
    "UPDATE label_type " \
    "SET activity = ? " \
    "WHERE id = ?"

SQL_UPDATE_DESCRIPTION = \
    "UPDATE label_type " \
    "SET description = ? " \
    "WHERE id = ?"

SQL_UPDATE_COLOR = \
    "UPDATE label_type " \
    "SET color = ? " \
    "WHERE id = ?"


class LabelTypeManager:

    def __init__(self, project_name: str):
        """
        :param project_name: The name of the current project
        """
        self.project_name = project_name
        self._conn = sqlite3.connect('projects/' + project_name + '/project_data.db',
                                     detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self._conn.row_factory = sqlite3.Row
        self._cur = self._conn.cursor()

    def create_table(self) -> None:
        """Method for creating the necessary label tables in the database."""
        self._cur.execute(SQL_CREATE_TABLE_LABEL_TYPE)
        self._conn.commit()

    def add_label_type(self, activity: str, color: str, description: str) -> bool:
        """
        Creates a new label type.

        :param activity: The name of the new label type
        :param color: The color of the new label
        :param description: The description of the label
        :return: boolean indication if the label type was added successfully
        """
        try:
            self._cur.execute(SQL_INSERT_LABEL_TYPE, (activity, color, description))
            self._conn.commit()
            return True
        except sqlite3.Error:
            return False

    def delete_label_type(self, name: str) -> None:
        """
        Delete a label type from the database.

        :param name: The name of the label activity type to delete
        """
        self._cur.execute(SQL_DELETE_LABEL_TYPE, (name,))
        self._conn.commit()

    def get_all_label_types(self) -> List[sqlite3.Row]:
        """
        Returns all label types.

        :return: List of tuples (label name, label color, label description) of all label types
        """
        self._cur.execute(SQL_SELECT_ALL_LABEL_TYPES)
        return self._cur.fetchall()

    def update_activity(self, id_: int, activity: str) -> None:
        """
        Updates the name of an existing label type. This also updates the name of all the labels that were made using
        the old name.

        :param id_: The ID of the label type to update
        :param activity: The new activity name
        """
        self._cur.execute(SQL_UPDATE_ACTIVITY, (activity, id_))
        self._conn.commit()

    def update_color(self, id_: int, color: str) -> None:
        """
        Updates the color of an existing label type.

        :param id_: The ID of the label type to update
        :param color: The new color
        """
        self._cur.execute(SQL_UPDATE_COLOR, (color, id_))
        self._conn.commit()

    def update_description(self, id_: int, description: str) -> None:
        """
        Updates the description of an existing label type.

        :param id_: The ID of the label type to update
        :param description: The new description
        """
        self._cur.execute(SQL_UPDATE_DESCRIPTION, (description, id_))
        self._conn.commit()
