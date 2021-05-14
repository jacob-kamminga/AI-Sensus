from playhouse.migrate import *


my_db = SqliteDatabase('C:/Users/Dennis/Desktop/test1/project_data.db')
migrator = SqliteMigrator(my_db)

migrate(
    # migrator.drop_not_null('sensordatafile', 'datetime')
    # migrator.add_column('camera', 'manual_offset', DoubleField(null=True))
    migrator.add_index('offset', ('camera', 'sensor'), True),
)
