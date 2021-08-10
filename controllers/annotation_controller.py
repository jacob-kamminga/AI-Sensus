import peewee

from database.models import Label, LabelType


class AnnotationController:

    def __init__(self, gui):
        self.gui = gui

    def save_label_to_db(self, activity, color, shortcut):
        # Normally an IntegrityError would be raised when the shortcut or activity name already exist.
        # One would have to check if it as raised as a result of the activity name already existing,
        # or the keyboard shortcut already being in use. The latter is checked first, so if the shortcut is already
        # taken (as happens when no shortcut is given, i.e. it is None), Peewee does not raise a separate error for the
        # name not being unique. Therefore this has to be checked manually as long as the database is set up this way.
        # In the end, IntegrityErrors should not be raised if it passes these two checks as long as the database
        # remains as it is.

        existing_activities = set(row.activity for row in LabelType.select(LabelType.activity))
        if activity in existing_activities:
            raise NonUniqueActivityNameException(activity)

        try:
            LabelType.get(LabelType.keyboard_shortcut == shortcut).activity
        except peewee.DoesNotExist:
            pass  # The above query failed, so there is currently no activity with the specified shortcut.
        else:
            raise NonUniqueShortcutException(shortcut, activity)  # An activity has been found with the shortcut.

        LabelType(activity=activity, color=color, description="", keyboard_shortcut=shortcut).save()

    def remove_label(self, remove_item):
        label_type = LabelType.get(LabelType.activity == remove_item)
        # Delete label type and all existing associated labels
        query = Label.delete().where(Label.label_type == label_type)
        query.execute()
        label_type.delete_instance()

class NonUniqueShortcutException(Exception):

    def __init__(self, shortcut, activity):
        self.shortcut = shortcut
        self.activity = activity

class NonUniqueActivityNameException(Exception):

    def __init__(self, activity):
        self.activity = activity