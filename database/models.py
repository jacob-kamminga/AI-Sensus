from peewee import Model, SqliteDatabase
from peewee import TextField, DoubleField, DateTimeField, ForeignKeyField, IntegerField, DateField, CharField

db = SqliteDatabase(None)

class BaseModel(Model):
    class Meta:
        database = db


class Camera(BaseModel):
    name = TextField(unique=True)
    timezone = TextField(default='UTC')
    manual_offset = DoubleField(null=True)


class Video(BaseModel):
    file_name = TextField()
    file_path = TextField()
    datetime = DateTimeField()
    camera = ForeignKeyField(Camera)


class SensorModel(BaseModel):
    model_name = TextField(unique=True)
    date_row = IntegerField()
    time_row = IntegerField()
    timestamp_column = IntegerField()
    relative_absolute = TextField()
    timestamp_unit = TextField()
    format_string = TextField()
    sensor_id_row = IntegerField()
    sensor_id_column = IntegerField(null=True)
    sensor_id_regex = TextField(null=True)
    col_names_row = IntegerField()
    comment_style = TextField(null=True)


class Sensor(BaseModel):
    name = TextField()
    model = ForeignKeyField(SensorModel)
    timezone = TextField(null=True)


class SensorDataFile(BaseModel):
    file_name = TextField()
    file_path = TextField()
    file_id_hash = TextField(unique=True)
    sensor = ForeignKeyField(Sensor)
    datetime = DateTimeField(null=True)
    last_used_column = TextField(null=True)


class Subject(BaseModel):
    name = TextField(unique=True)
    color = TextField(null=True)
    size = TextField(null=True)
    extra_info = TextField(null=True)


class SubjectMapping(BaseModel):
    subject = ForeignKeyField(Subject)
    sensor = ForeignKeyField(Sensor)
    start_datetime = DateTimeField()
    end_datetime = DateTimeField()

    class Meta:
        indexes = (
            (('subject_id', 'start_datetime'), True),
        )


class Offset(BaseModel):
    camera = ForeignKeyField(Camera)
    sensor = ForeignKeyField(Sensor)
    offset = DoubleField()
    added = DateField()

    class Meta:
        indexes = (
            # Create a unique index on camera/sensor
            (('camera', 'sensor'), True),
        )


class LabelType(BaseModel):
    activity = TextField(unique=True)
    color = TextField()
    description = TextField()
    keyboard_shortcut = CharField(max_length=1, unique=True)


class Label(BaseModel):
    start_time = DateTimeField()
    end_time = DateTimeField()
    label_type = ForeignKeyField(LabelType)
    sensor_data_file = ForeignKeyField(SensorDataFile)

    class Meta:
        indexes = (
            (('sensor_data_file', 'start_time'), True),
        )
