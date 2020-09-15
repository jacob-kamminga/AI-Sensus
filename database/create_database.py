from sqlite3 import Connection

CREATE_TABLE_CAMERA = "create table camera\
(\
  name     TEXT    not null,\
  timezone TEXT default 'UTC' not null,\
  id       INTEGER not null\
    constraint cameras_pk\
      primary key autoincrement\
);"

CREATE_UINDEX_CAMERA = \
    "create unique index cameras_name_uindex\
         on camera (name);"

CREATE_TABLE_LABEL = \
    "create table label\
    (\
        id               INTEGER   not null\
            constraint label_pk\
                primary key autoincrement,\
        start_time       TIMESTAMP not null,\
        end_time         TIMESTAMP not null,\
        label_type       INTEGER   not null\
            references label_type\
                on update cascade on delete cascade,\
        sensor_data_file INTEGER   not null\
            references sensor_data_file\
                on update cascade on delete cascade\
    );"

CREATE_UINDEX_LABEL = \
    "create unique index label_start_time_sensor_data_file_id_uindex\
        on label (start_time, sensor_data_file);"

CREATE_TABLE_LABEL_TYPE = \
    "create table label_type\
     (\
         id          INTEGER not null\
             constraint label_type_pk\
                 primary key autoincrement,\
         activity    TEXT    not null,\
         color       TEXT    not null,\
         description TEXT\
     );"

CREATE_UINDEX_LABEL_TYPE = \
    "create unique index label_type_activity_uindex\
        on label_type (activity);"

CREATE_TABLE_OFFSET = \
    "create table offset\
    (\
        camera    INTEGER not null,\
        sensor    INTEGER not null,\
        offset    DOUBLE  not null,\
        added     DATE    not null,\
        constraint offset_pk\
            unique (camera, sensor)\
    );"

CREATE_TABLE_SENSOR_DATA_FILE = \
    "create table sensor_data_file\
    (\
      id        INTEGER not null\
        constraint sensor_data_file_pk\
          primary key autoincrement,\
      file_name TEXT    not null,\
      file_path TEXT,\
      sensor_id INTEGER\
          references sensor,\
      datetime  TIMESTAMP\
    );"

CREATE_UINDEX_SENSOR_DATA_FILE = \
    "create unique index sensor_data_file_file_name_uindex\
         on sensor_data_file (file_name);"

CREATE_TABLE_SENSOR = \
    "create table sensor\
    (\
      id    INTEGER not null\
        constraint sensor_pk\
          primary key autoincrement,\
      name  TEXT    not null,\
      model INTEGER not null\
          references sensor_model\
              on update cascade on delete cascade\
    );"

CREATE_UINDEX_SENSOR = \
    "create unique index sensor_sensor_id_uindex\
         on sensor (name);"

CREATE_TABLE_SENSOR_MODEL = \
    "create table sensor_model\
    (\
        id               INTEGER\
            constraint sensor_model_pk\
                primary key autoincrement,\
        model_name       VARCHAR(50) not null,\
        date_row         INTEGER     not null,\
        time_row         INTEGER     not null,\
        sensor_id_row    INTEGER     not null,\
        sensor_id_column INTEGER,\
        sensor_id_regex  TEXT,\
        headers_row      INTEGER     not null,\
        comment_style    TEXT        not null\
    );"

CREATE_UINDEX_SENSOR_MODEL = \
    "create unique index sensor_model_name_uindex\
         on sensor_model (model_name);"

CREATE_TABLE_SENSOR_USAGE = \
    "create table sensor_usage\
    (\
        id             INTEGER\
            constraint subject_sensor_map_pk\
                primary key,\
        subject_id     INTEGER  not null,\
        sensor_id      INTEGER  not null,\
        start_datetime DATETIME not null,\
        end_datetime   DATETIME not null\
    );"

CREATE_UINDEX_SENSOR_USAGE = \
    "create unique index subject_sensor_map_subject_id_start_datetime_uindex\
         on sensor_usage (subject_id, start_datetime);"

CREATE_TABLE_SUBJECT = \
    "create table subject\
    (\
        id         INTEGER     not null\
            constraint subject_pk\
                primary key autoincrement,\
        name       VARCHAR(50) not null,\
        color      VARCHAR(50),\
        size       VARCHAR(50),\
        extra_info TEXT\
    );"

CREATE_UINDEX_SUBJECT = \
    "create unique index subject_name_uindex\
         on subject (name);"

CREATE_TABLE_VIDEO = \
    "create table video\
    (\
      id        INTEGER not null\
        constraint video_file_pk\
          primary key autoincrement,\
      file_name TEXT    not null,\
      file_path TEXT,\
      datetime  TIMESTAMP,\
      camera_id INTEGER not null\
        references camera\
    );"

CREATE_UINDEX_VIDEO = \
    "create unique index video_file_file_name_uindex\
         on video (file_name);"


def create_database(conn: Connection):
    cur = conn.cursor()
    cur.execute(CREATE_TABLE_CAMERA)
    cur.execute(CREATE_UINDEX_CAMERA)
    cur.execute(CREATE_TABLE_SENSOR_MODEL)
    cur.execute(CREATE_UINDEX_SENSOR_MODEL)
    cur.execute(CREATE_TABLE_SENSOR)
    cur.execute(CREATE_UINDEX_SENSOR)
    cur.execute(CREATE_TABLE_SENSOR_DATA_FILE)
    cur.execute(CREATE_UINDEX_SENSOR_DATA_FILE)
    cur.execute(CREATE_TABLE_VIDEO)
    cur.execute(CREATE_UINDEX_VIDEO)
    cur.execute(CREATE_TABLE_SUBJECT)
    cur.execute(CREATE_UINDEX_SUBJECT)
    cur.execute(CREATE_TABLE_SENSOR_USAGE)
    cur.execute(CREATE_UINDEX_SENSOR_USAGE)
    cur.execute(CREATE_TABLE_OFFSET)
    cur.execute(CREATE_TABLE_LABEL_TYPE)
    cur.execute(CREATE_UINDEX_LABEL_TYPE)
    cur.execute(CREATE_TABLE_LABEL)
    cur.execute(CREATE_UINDEX_LABEL)
    conn.commit()
