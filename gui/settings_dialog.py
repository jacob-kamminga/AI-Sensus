from gui.new_dialog import NewProject
from datastorage import settings


class SettingsDialog(NewProject):

    def __init__(self, settings: settings.Settings):
        super().__init__()
        self.settings = settings
        self.rejected.disconnect()
        self.comboBox_existing.setParent(None)
        self.comboBox_existing.deleteLater()
        self.lineEdit_new.setParent(None)
        self.lineEdit_new.deleteLater()
        self.label.setParent(None)
        self.label.deleteLater()
        self.label_2.setParent(None)
        self.label_2.deleteLater()
        self.verticalLayout_7.removeItem(self.verticalLayout)
        self.spinBox_timerow.setEnabled(True)
        self.spinBox_timecol.setEnabled(True)
        self.spinBox_daterow.setEnabled(True)
        self.spinBox_datecol.setEnabled(True)
        self.spinBox_srrow.setEnabled(True)
        self.spinBox_srcol.setEnabled(True)
        self.spinBox_snrow.setEnabled(True)
        self.spinBox_sncol.setEnabled(True)
        self.spinBox_namesrow.setEnabled(True)
        self.lineEdit_comment.setEnabled(True)

        self.spinBox_timerow.setValue(settings.get_setting("time_row"))
        self.spinBox_timecol.setValue(settings.get_setting("time_col"))
        self.spinBox_daterow.setValue(settings.get_setting("date_row"))
        self.spinBox_datecol.setValue(settings.get_setting("date_col"))
        self.spinBox_srrow.setValue(settings.get_setting("sr_row"))
        self.spinBox_srcol.setValue(settings.get_setting("sr_col"))
        self.spinBox_snrow.setValue(settings.get_setting("sn_row"))
        self.spinBox_sncol.setValue(settings.get_setting("sn_col"))
        self.spinBox_namesrow.setValue(settings.get_setting("names_row"))
        self.lineEdit_comment.setText(settings.get_setting("comment"))

    def open_project(self):
        self.settings.set_setting("time_row", self.time_row)
        self.settings.set_setting("time_col", self.time_col)
        self.settings.set_setting("date_row", self.date_row)
        self.settings.set_setting("date_col", self.date_col)
        self.settings.set_setting("sr_row", self.sr_row)
        self.settings.set_setting("sr_col", self.sr_col)
        self.settings.set_setting("sn_row", self.sn_row)
        self.settings.set_setting("sn_col", self.sn_col)
        self.settings.set_setting("names_row", self.names_row)
        self.settings.set_setting("comment", self.comment)