from playhouse.migrate import *


my_db = SqliteDatabase('C:/Users/Dennis/Desktop/test/project_data.db')
migrator = SqliteMigrator(my_db)

migrate(
    migrator.drop_not_null('sensordatafile', 'datetime')
)
