from datetime import datetime

from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate, QStringListModel
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox

from gui.designer_subject_table import Ui_Subject_table
from datastorage.subjectmapping import SubjectManager
from datastorage.labelstorage import LabelManager


class SubjectTable(QtWidgets.QDialog, Ui_Subject_table):

    def __init__(self, project_name: str):
        super().__init__()
        # Initialize the generated UI from designer_gui.py.
        self.setupUi(self)

        self.project_name = project_name
        self.subject_manager = SubjectManager(project_name)
        self.col_names, self.table_data = self.subject_manager.get_table()  # get stored data from the database
        self.subject_names = [x[0] for x in self.table_data]
        self.sensorIDs = LabelManager(self.project_name).get_sensor_ids()  # get all used sensor ids for this project
        self.tableWidget.setColumnCount(len(self.col_names))
        self.tableWidget.setRowCount(len(self.table_data))
        self.tableWidget.setHorizontalHeaderLabels(self.col_names)

        # fill table
        self.tableWidget.blockSignals(True)  # blockSignals to prevent calls to update functions
        for i in range(len(self.table_data)):
            for j in range(len(self.table_data[i])):
                item = self.table_data[i][j]
                if j == 1:  # sensor id column
                    combo_box = QComboBox()
                    combo_box.setModel(QStringListModel())
                    if item is None:  # if no sensor has been selected yet, add a blank option
                        combo_box.addItem("")
                    combo_box.addItems(self.sensorIDs)
                    combo_box.setCurrentText(item)  # set the selected item to the item from the database (if it is set)
                    combo_box.currentTextChanged.connect(self.update_sensor_id)
                    self.tableWidget.setCellWidget(i, j, combo_box)
                elif j == 2 or j == 3:  # date columns, 'item' is a datetime object
                    date_item = QDateEdit(QDate(item.year, item.month, item.day))
                    date_item.dateChanged.connect(self.update_date)
                    self.tableWidget.setCellWidget(i, j, date_item)
                else:  # all cells of other columns are text items
                    self.tableWidget.setItem(i, j, QTableWidgetItem(item))
        self.tableWidget.blockSignals(False)

        self.tableWidget.resizeColumnToContents(1)  # fit the sensor id column to its content

        self.closeButton.clicked.connect(self.close)
        self.rowButton.clicked.connect(self.add_row)
        self.colButton.clicked.connect(self.add_col)
        self.delSubjectButton.clicked.connect(self.delete_row)
        self.delColumnButton.clicked.connect(self.delete_column)
        self.tableWidget.cellChanged.connect(self.update_string)

    def add_row(self) -> None:
        text, accepted = QInputDialog.getText(self, "Enter new subject name", "Subject name:", QLineEdit.Normal, "")
        if accepted:
            if text == '':
                self.show_warning("Give a subject name")
                return
            if text in self.subject_names:
                self.show_warning("The name of this subject already exists")
                return
            self.tableWidget.blockSignals(True)
            position = self.tableWidget.rowCount()  # get row index of the end of the table
            self.tableWidget.insertRow(position)
            self.tableWidget.setItem(position, 0, QTableWidgetItem(text))  # set subject name
            self.subject_names.append(text)         # add subject to internal list
            self.subject_manager.add_subject(text)  # add subject to database

            # sensor id column, add combobox with blank option selected
            combo_box = QComboBox()
            combo_box.setModel(QStringListModel())
            combo_box.addItem("")
            combo_box.addItems(self.sensorIDs)
            combo_box.currentTextChanged.connect(self.update_sensor_id)
            self.tableWidget.setCellWidget(position, 1, combo_box)

            # date columns, add date-selector with today's date selected
            start_date = QDateEdit(QDate.currentDate())
            start_date.dateChanged.connect(self.update_date)
            end_date = QDateEdit(QDate.currentDate())
            end_date.dateChanged.connect(self.update_date)
            self.subject_manager.update_start_date(text, datetime.now())  # also add the dates to the database in case
            self.subject_manager.update_end_date(text, datetime.now())    # the user doesn't change them manually
            self.tableWidget.setCellWidget(position, 2, start_date)
            self.tableWidget.setCellWidget(position, 3, end_date)

            self.tableWidget.blockSignals(False)

    def add_col(self) -> None:
        text, accepted = QInputDialog.getText(self, "Enter new column name", "Column name:", QLineEdit.Normal, "")
        if accepted:
            if text == '':
                self.show_warning("Give a column name")
                return
            if text in self.col_names:
                self.show_warning("The name of this column already exists")
                return
            position = self.tableWidget.columnCount()  # get column index of the end of the table
            self.tableWidget.insertColumn(position)
            self.tableWidget.setHorizontalHeaderItem(position, QTableWidgetItem(text))  # set column name in the table
            self.subject_manager.add_column(text)
            self.col_names.append(text)

    def delete_row(self) -> None:
        if len(self.subject_names) == 0:
            self.show_warning("There is no subject that can be removed")
            return
        subject, accepted = QInputDialog.getItem(self, "Select a subject",
                                                 "Select a subject to remove", self.subject_names, 0, False)
        if accepted:
            # remove the given subject row from database and table
            self.subject_manager.delete_subject(subject)
            row = self.subject_names.index(subject)
            self.subject_names.remove(subject)
            self.tableWidget.removeRow(row)

    def delete_column(self) -> None:
        if len(self.col_names) == 4:  # there are 4 standard columns (subject name, sensor id, start date, end date)
            self.show_warning("There is no column that can be removed")
            return

        col_name, accepted = QInputDialog.getItem(self, "Select a column",
                                                  "Select a column to remove", self.col_names[4:], 0, False)
        if accepted:
            # remove column from table and remove name from internal mapping
            self.subject_manager.delete_column(col_name)
            column = self.col_names.index(col_name)
            self.col_names.remove(col_name)
            self.tableWidget.removeColumn(column)

    def update_string(self, row: int, col: int) -> None:
        # called by edit of a text cell, either subject name column or a user-made column
        subject = self.subject_names[row]
        new_value = self.tableWidget.item(row, col).text()
        if col == 0:  # subject name
            if new_value in self.subject_names:
                self.show_warning("The name of this subject already exists")
                self.tableWidget.blockSignals(True)
                self.tableWidget.item(row, col).setText(self.subject_names[row])  # reset cell value
                self.tableWidget.blockSignals(False)
                return
            self.subject_manager.update_subject(self.subject_names[row], new_value)
            self.subject_names[row] = new_value

        else:  # user-made column
            col_name = self.col_names[col]
            self.subject_manager.update_user_column(col_name, subject, new_value)

    def update_sensor_id(self, sensor_id: str) -> None:
        row = self.tableWidget.currentRow()  # get the row of the changed sensor id
        combo_box = self.tableWidget.cellWidget(row, self.tableWidget.currentColumn())
        if "" in combo_box.model().stringList():  # blank option no longer necessary because a sensor was just selected
            combo_box.removeItem(0)  # the "" option is always at index 0. remove it
        subject = self.subject_names[row]
        self.subject_manager.update_sensor(subject, sensor_id)

    def update_date(self, date: QDate) -> None:
        row = self.tableWidget.currentRow()
        col = self.tableWidget.currentColumn()
        subject = self.subject_names[row]
        new_date = datetime(date.year(), date.month(), date.day())
        if col == 2:  # start date
            self.subject_manager.update_start_date(subject, new_date)
        else:  # end date
            self.subject_manager.update_end_date(subject, new_date)

    def show_warning(self, message: str) -> None:
        QMessageBox.warning(self, 'Warning', message, QMessageBox.Cancel)