from datetime import datetime

from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate, QStringListModel, QDateTime
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QDateTimeEdit

from database.db_sensor import SensorManager
from database.db_subject import SubjectManager, INDEX_SUBJECT_NAME, INDEX_SUBJECT_ID
from gui.designer_subject_sensor_map import Ui_Dialog
from database.db_subject_sensor_map import SubjectSensorMapManager
from database.db_label import LabelManager


INDEX_MAP_ID = 0
INDEX_MAP_SUBJECT = 1
INDEX_MAP_SENSOR = 2
INDEX_MAP_START = 3
INDEX_MAP_END = 4


class SubjectSensorMapDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, project_name: str):
        super().__init__()
        self.setupUi(self)

        self.project_name = project_name
        self.subject_manager = SubjectManager(project_name)
        self.sensor_manager = SensorManager(project_name)
        self.map_manager = SubjectSensorMapManager(project_name)

        self.all_subjects = self.subject_manager.get_all_subjects()
        self.subjects_dict = dict((id_, name) for id_, name, _, _, _ in self.all_subjects)

        self.all_sensors = self.sensor_manager.get_all_sensors()
        self.sensors_dict = dict((id_, name) for id_, name in self.all_sensors)

        self.maps = self.map_manager.get_all_maps()
        self.column_names = ["ID", "Subject", "Sensor", "Start date", "End date"]

        self.create_table()

        # # Fill table
        # self.tableWidget.blockSignals(True)  # blockSignals to prevent calls to update functions
        #
        # for i in range(len(self.table_data)):
        #     for j in range(len(self.table_data[i])):
        #         item = self.table_data[i][j]
        #
        #         if j == 1:  # Sensor id column
        #             combo_box = QComboBox()
        #             combo_box.setModel(QStringListModel())
        #
        #             if item is None:  # If no sensor has been selected yet, add a blank option
        #                 combo_box.addItem("")
        #
        #             combo_box.addItems(self.sensorIDs)
        #             combo_box.setCurrentText(item)  # Set the selected item to the item from the database (if it is set)
        #             combo_box.currentTextChanged.connect(self.update_sensor_id)
        #             self.tableWidget.setCellWidget(i, j, combo_box)
        #         elif j == 2 or j == 3:  # Date columns, 'item' is a datetime object
        #             datetime_item = QDateTimeEdit(QDateTime(item.year, item.month, item.day, item.hour, item.minute,
        #                                                     item.second))
        #             datetime_item.dateTimeChanged.connect(self.update_datetime)
        #             self.tableWidget.setCellWidget(i, j, datetime_item)
        #         else:  # All cells of other columns are text items
        #             self.tableWidget.setItem(i, j, QTableWidgetItem(item))
        #
        # self.tableWidget.blockSignals(False)
        #
        # self.tableWidget.resizeColumnToContents(1)  # fit the sensor id column to its content
        #
        # self.closeButton.clicked.connect(self.close)
        # self.rowButton.clicked.connect(self.add_row)
        # self.colButton.clicked.connect(self.add_col)
        # self.delSubjectButton.clicked.connect(self.delete_row)
        # self.delColumnButton.clicked.connect(self.delete_column)
        # self.tableWidget.cellChanged.connect(self.update_string)

    def create_table(self):
        self.tableWidget.blockSignals(True)

        self.tableWidget.setColumnCount(len(self.column_names))
        self.tableWidget.setRowCount(len(self.maps))
        self.tableWidget.setHorizontalHeaderLabels(self.column_names)

        for i, row in enumerate(self.maps):
            id_ = row[INDEX_MAP_ID]
            subject_id = row[INDEX_MAP_SUBJECT]
            sensor_id = row[INDEX_MAP_SENSOR]
            start_dt = row[INDEX_MAP_START]
            end_dt = row[INDEX_MAP_END]

            # subject_combobox = QComboBox()
            # subject_combobox.setModel(QStringListModel())
            # subject_combobox.addItems(self.subjects_dict.values())
            # subject_combobox.setCurrentText(self.subjects_dict[subject_id])
            #
            # sensor_combobox = QComboBox()
            # sensor_combobox.setModel(QStringListModel())
            # sensor_combobox.addItems(self.sensors_dict.values())
            # sensor_combobox.setCurrentText(self.sensors_dict[sensor_id])

            self.tableWidget.setItem(i, INDEX_MAP_ID, QTableWidgetItem(str(id_)))
            self.tableWidget.setItem(i, INDEX_MAP_SUBJECT, QTableWidgetItem(self.subjects_dict[subject_id]))
            self.tableWidget.setItem(i, INDEX_MAP_SENSOR, QTableWidgetItem(self.sensors_dict[sensor_id]))
            self.tableWidget.setItem(i, INDEX_MAP_START, QTableWidgetItem(str(start_dt)))
            self.tableWidget.setItem(i, INDEX_MAP_END, QTableWidgetItem(str(end_dt)))

        # Hide the ID column
        self.tableWidget.hideColumn(INDEX_MAP_ID)

        self.tableWidget.blockSignals(False)

    # def add_row(self) -> None:
    #     text, accepted = QInputDialog.getText(self, "Enter new subject name", "Subject name:", QLineEdit.Normal, "")
    #
    #     if accepted:
    #         if text == '':
    #             self.show_warning("Give a subject name")
    #             return
    #         if text in self.subject_names:
    #             self.show_warning("The name of this subject already exists")
    #             return
    #         self.tableWidget.blockSignals(True)
    #         position = self.tableWidget.rowCount()  # get row index of the end of the table
    #         self.tableWidget.insertRow(position)
    #         self.tableWidget.setItem(position, 0, QTableWidgetItem(text))  # set subject name
    #         self.subject_names.append(text)         # add subject to internal list
    #         self.map_manager.add_subject(text)  # add subject to database
    #
    #         # Sensor id column, add combobox with blank option selected
    #         combo_box = QComboBox()
    #         combo_box.setModel(QStringListModel())
    #         combo_box.addItem("")
    #         combo_box.addItems(self.sensorIDs)
    #         combo_box.currentTextChanged.connect(self.update_sensor_id)
    #         self.tableWidget.setCellWidget(position, 1, combo_box)
    #
    #         # Date columns, add date-selector with today's date selected
    #         start_date = QDateTimeEdit(QDateTime.currentDateTime())
    #         start_date.dateTimeChanged.connect(self.update_datetime)
    #         end_date = QDateTimeEdit(QDateTime.currentDate())
    #         end_date.dateTimeChanged.connect(self.update_datetime)
    #         self.map_manager.update_start_date(text, datetime.now())  # Also add the dates to the database in case
    #         self.map_manager.update_end_date(text, datetime.now())    # the user doesn't change them manually
    #         self.tableWidget.setCellWidget(position, 2, start_date)
    #         self.tableWidget.setCellWidget(position, 3, end_date)
    #
    #         self.tableWidget.blockSignals(False)

    # def add_col(self) -> None:
    #     text, accepted = QInputDialog.getText(self, "Enter new column name", "Column name:", QLineEdit.Normal, "")
    #
    #     if accepted:
    #         if text == '':
    #             self.show_warning("Give a column name")
    #             return
    #
    #         if text in self.col_names:
    #             self.show_warning("The name of this column already exists")
    #             return
    #
    #         position = self.tableWidget.columnCount()  # get column index of the end of the table
    #         self.tableWidget.insertColumn(position)
    #         self.tableWidget.setHorizontalHeaderItem(position, QTableWidgetItem(text))  # set column name in the table
    #         self.map_manager.add_column(text)
    #         self.col_names.append(text)
    #
    # def delete_row(self) -> None:
    #     if len(self.subject_names) == 0:
    #         self.show_warning("There is no subject that can be removed")
    #         return
    #
    #     subject, accepted = QInputDialog.getItem(self, "Select a subject",
    #                                              "Select a subject to remove", self.subject_names, 0, False)
    #
    #     if accepted:
    #         # Remove the given subject row from database and table
    #         self.map_manager.delete_subject(subject)
    #         row = self.subject_names.index(subject)
    #         self.subject_names.remove(subject)
    #         self.tableWidget.removeRow(row)
    #
    # def delete_column(self) -> None:
    #     if len(self.col_names) == 4:  # there are 4 standard columns (subject name, sensor id, start date, end date)
    #         self.show_warning("There is no column that can be removed")
    #         return
    #
    #     col_name, accepted = QInputDialog.getItem(self, "Select a column",
    #                                               "Select a column to remove", self.col_names[4:], 0, False)
    #     if accepted:
    #         # Remove column from table and remove name from internal mapping
    #         self.map_manager.delete_column(col_name)
    #         column = self.col_names.index(col_name)
    #         self.col_names.remove(col_name)
    #         self.tableWidget.removeColumn(column)
    #
    # def update_string(self, row: int, col: int) -> None:
    #     # Called by edit of a text cell, either subject name column or a user-made column
    #     subject = self.subject_names[row]
    #     new_value = self.tableWidget.item(row, col).text()
    #
    #     if col == 0:  # subject name
    #         if new_value in self.subject_names:
    #             self.show_warning("The name of this subject already exists")
    #             self.tableWidget.blockSignals(True)
    #             self.tableWidget.item(row, col).setText(self.subject_names[row])  # Reset cell value
    #             self.tableWidget.blockSignals(False)
    #             return
    #         self.map_manager.update_subject(self.subject_names[row], new_value)
    #         self.subject_names[row] = new_value
    #
    #     else:  # User-made column
    #         col_name = self.col_names[col]
    #         self.map_manager.update_user_column(col_name, subject, new_value)
    #
    # def update_sensor_id(self, sensor_id: str) -> None:
    #     row = self.tableWidget.currentRow()  # Get the row of the changed sensor id
    #     combo_box = self.tableWidget.cellWidget(row, self.tableWidget.currentColumn())
    #
    #     if "" in combo_box.model().stringList():  # Blank option no longer necessary because a sensor was just selected
    #         combo_box.removeItem(0)  # The "" option is always at index 0. Remove it
    #
    #     subject = self.subject_names[row]
    #     self.map_manager.update_sensor(subject, sensor_id)
    #
    # def update_datetime(self, qdt: QDateTime) -> None:
    #     row = self.tableWidget.currentRow()
    #     col = self.tableWidget.currentColumn()
    #     subject = self.subject_names[row]
    #     new_datetime = qdt.toPyDateTime()
    #
    #     if col == 2:  # Start date
    #         self.map_manager.update_start_date(subject, new_datetime)
    #     else:  # End date
    #         self.map_manager.update_end_date(subject, new_datetime)
    #
    # def show_warning(self, message: str) -> None:
    #     QMessageBox.warning(self, 'Warning', message, QMessageBox.Cancel)
