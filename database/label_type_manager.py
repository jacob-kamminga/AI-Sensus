import sqlite3
from typing import List

from gui.dialogs.project_settings import ProjectSettingsDialog

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
    "INSERT INTO label_type(activity, color, description, keyboard_shortcut) VALUES (?, ?, ?, ?)"

SQL_SELECT_ALL_LABEL_TYPES = \
    "SELECT * FROM label_type"

SQL_SELECT_KEYBOARD_SHORTCUT = \
    "SELECT keyboard_shortcut FROM label_type " \
    "WHERE activity = ?"

SQL_SELECT_ACTIVITY_BY_KEYBOARD_SHORTCUT = \
    "SELECT activity FROM label_type " \
    "WHERE keyboard_shortcut = ?"

SQL_SELECT_ID_BY_KEYBOARD_SHORTCUT = \
    "SELECT id FROM label_type " \
    "WHERE keyboard_shortcut = ?"

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
    "WHERE activity = ?"

SQL_UPDATE_KEYBOARD_SHORTCUT = \
    "UPDATE label_type " \
    "SET keyboard_shortcut = ? " \
    "WHERE activity = ?"

SQL_REMOVE_KEYBOARD_SHORTCUT = \
    "UPDATE label_type " \
    "SET keyboard_shortcut = NULL " \
    "WHERE activity = ?"

class LabelTypeManager:

    def __init__(self, settings: ProjectSettingsDialog):
        self._conn = sqlite3.connect(
            settings.database_file.as_posix(),
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        # Enable Sqlite foreign key support
        self._conn.execute("PRAGMA foreign_keys = 1")

        self._conn.row_factory = sqlite3.Row
        self._cur = self._conn.cursor()

    # def create_table(self) -> None:
    #     """Method for creating the necessary label tables in the database."""
    #     self._cur.execute(SQL_CREATE_TABLE_LABEL_TYPE)
    #     self._conn.commit()

    def add_label_type(self, activity: str, color: str, description: str, keyboard_shortcut: str) -> bool:
        """
        Creates a new label type.

        :param keyboard_shortcut: Optional keyboard shortcut
        :param activity: The name of the new label type
        :param color: The color of the new label
        :param description: The description of the label
        :return: boolean indication if the label type was added successfully
        """
        try:
            self._cur.execute(SQL_INSERT_LABEL_TYPE, (activity, color, description, keyboard_shortcut))
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

    def update_color(self, activity: str, color: str) -> None:
        """
        Updates the color of an existing label type.

        :param id_: The ID of the label type to update
        :param color: The new color
        """
        self._cur.execute(SQL_UPDATE_COLOR, (color, activity))
        self._conn.commit()

    def update_description(self, id_: int, description: str) -> None:
        """
        Updates the description of an existing label type.

        :param id_: The ID of the label type to update
        :param description: The new description
        """
        self._cur.execute(SQL_UPDATE_DESCRIPTION, (description, id_))
        self._conn.commit()

    def update_keyboard_shortcut(self, activity: str, keyboard_shortcut: str) -> None:
        """
        Updates the description of an existing label type.

        :param activity:
        :param keyboard_shortcut: The keyboard shortcut
        """
        self._cur.execute(SQL_UPDATE_KEYBOARD_SHORTCUT, (keyboard_shortcut, activity))
        self._conn.commit()

    def get_keyboard_shortcut(self, activity: str):
        self._cur.execute(SQL_SELECT_KEYBOARD_SHORTCUT, (activity,))
        return self._cur.fetchone()[0]

    def get_activity_by_keyboard_shortcut(self, keyboard_shortcut):
        self._cur.execute(SQL_SELECT_ACTIVITY_BY_KEYBOARD_SHORTCUT, (keyboard_shortcut,))
        return self._cur.fetchone()[0]

    def remove_keyboard_shortcut(self, activity: str):
        self._cur.execute(SQL_REMOVE_KEYBOARD_SHORTCUT, (activity,))
        self._conn.commit()

    def get_id_by_keyboard_shortcut(self, keyboard_shortcut):
        self._cur.execute(SQL_SELECT_ID_BY_KEYBOARD_SHORTCUT, (keyboard_shortcut,))
        return self._cur.fetchone()[0]
