from peewee import *


class SensorModel(Model):
    name = CharField()
    date_format = CharField()
    date_row = SmallIntegerField()
    date_col = SmallIntegerField()
    date_regex = CharField()
    time_format = CharField()
    time_row = SmallIntegerField()
    time_col = SmallIntegerField()
    time_regex = CharField()
    sensor_id_row = SmallIntegerField()
    sensor_id_col = SmallIntegerField()
    sensor_id_regex = CharField()
    headers_row = SmallIntegerField()
    comment_style = CharField()
