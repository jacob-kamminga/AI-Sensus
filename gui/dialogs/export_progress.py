from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtWidgets import QMessageBox
from gui.designer.progress_bar import Ui_Dialog
from numpy import array_split
import sys
import os


class ExportProgressDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, df, output_path):
        super().__init__()
        self.setupUi(self)

        # Connect UI elements
        self.pushButton_cancel.clicked.connect(self.abort)

        self.worker = Worker(df, output_path)
        self.thread = QThread()
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.progress)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.moveToThread(self.thread)
        self.worker.start()

    def progress(self, percentage):
        self.progressBar.setProperty("value", percentage+1)
        if percentage == 100:
            self.close()

    def abort(self):
        self.worker.quit()
        self.close()


class Worker(QThread):
    """
    Worker to export the dataframe df to output_path.
    """
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, df, output_path):
        super().__init__()
        self.df = df
        self.output_path = output_path

    @pyqtSlot()
    def run(self):
        """Export the dataframe to a CSV file in chunks.

        This loop separates the dataframe in 100 roughly equal parts and appends each part to the
        previous parts, so that a progress update can be given in the form of a progress bar. This
        is particularly useful for dataframes that encompass large amounts of time."""

        df_split = array_split(self.df, 100)  # Divide into 100 (roughly) equal chunks.

        debug = getattr(sys, 'gettrace', None)() is not None  # Check if the program is running in debug mode.
        if debug:
            print("Slowing down export progress bar for visualisation...")

        try:
            for i in range(100):
                if debug:  # Slows down the progress bar to check if it works correctly.
                    for j in range(1000):
                        pass
                # Append each chunk to output_path CSV using mode='a' (append).
                df_split[i].to_csv(self.output_path, mode='a', header=False, index=False)
                self.progress.emit(i + 1)

            # msg = QMessageBox()
            # msg.setIcon(QMessageBox.Information)
            # msg.setWindowTitle("Success!")
            # msg.setText("Export successful!")
            # # msg.setInformativeText("")
            # msg.setStandardButtons(QMessageBox.Ok)
            # msg.exec()
            # # self.close()

        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Error!")
            msg.setText("An error occurred during export: " + str(e))
            # msg.setInformativeText("")
            msg.setStandardButtons(QMessageBox.Ok)

        self.finished.emit()
