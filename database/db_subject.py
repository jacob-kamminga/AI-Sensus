import sqlite3
from typing import List

from database import settings

SQL_CREATE_TABLE = "create table subject\
(\
    id         INTEGER     not null\
        constraint subject_pk\
            primary key autoincrement,\
    name       VARCHAR(50) not null,\
    color      VARCHAR(50),\
    size       VARCHAR(50),\
    extra_info TEXT\
);\
\
create unique index subject_name_uindex\
    on subject (name);"

SQL_INSERT_SUBJECT = "INSERT INTO subject (name, color, size, extra_info) VALUES (?, ?, ?, ?)"
SQL_SELECT_SUBJECT_BY_NAME = "SELECT name, color, size, extra_info FROM subject"
SQL_SELECT_SUBJECTS = "SELECT name, color, size, extra_info FROM subject"
SQL_SELECT_SUBJECT_NAMES = "SELECT name FROM subject"


class SubjectManager:

    def __init__(self, project_name: str):
        self._conn = sqlite3.connect('projects/' + project_name + '/project_data.db',
                                     detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self._cur = self._conn.cursor()
        self.settings = settings.Settings(project_name)

    def create_table(self) -> None:
        self._cur.execute(SQL_CREATE_TABLE)
        self._conn.commit()

    def add_subject(self, name, color, size, extra_info) -> None:
        self._cur.execute(SQL_INSERT_SUBJECT, (name, color, size, extra_info))
        self._conn.commit()

    def get_subject_by_name(self, name):
        self._cur.execute(SQL_SELECT_SUBJECT_BY_NAME, name)
        self._cur.fetchall()

    def get_subjects(self) -> List[str]:
        self._cur.execute(SQL_SELECT_SUBJECTS)
        return self._cur.fetchall()

    def get_subject_names(self) -> List[str]:
        self._cur.execute(SQL_SELECT_SUBJECT_NAMES)
        return self._cur.fetchall()
