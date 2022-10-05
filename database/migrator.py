from playhouse.migrate import SqliteDatabase, SqliteMigrator, migrate
from database.models import SubjectMapping
from pathlib import Path

# migrator.drop_not_null('sensordatafile', 'datetime')
# migrator.add_column('camera', 'manual_offset', DoubleField(null=True))
# migrator.add_index('offset', ('camera', 'sensor'), True),

def rename_table(db_path: Path, old: str, new: str):
    my_db = SqliteDatabase(db_path)
    migrator = SqliteMigrator(my_db)
    migrate(migrator.rename_table(old, new))


