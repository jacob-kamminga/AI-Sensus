from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtWidgets import QMessageBox
from gui.designer.progress_bar import Ui_Dialog
from numpy import array_split
import sys

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
        self.thread.start()

    def progress(self, percentage):
        self.progressBar.setProperty("value", percentage+1)
        if percentage == 100:
            self.close()

    def abort(self):
        print("Aborting...")

    # def export(self, df, output_path):
    #     df_split = array_split(self.df, 100)  # Divide into 100 (roughly) equal chunks.
    #
    #     try:
    #         for i in range(100):
    #             self.progressBar.setProperty("value", i + 1)
    #             for j in range(1000):
    #                 pass
    #             df_split[i].to_csv(self.output_path, mode='a', header=False,
    #                                index=False)  # mode='a' means append to file.
    #
    #         msg = QMessageBox()
    #         msg.setIcon(QMessageBox.Information)
    #         msg.setWindowTitle("Success!")
    #         msg.setText("Export successful!")
    #         # msg.setInformativeText("")
    #         msg.setStandardButtons(QMessageBox.Ok)
    #         msg.exec()
    #         self.close()
    #     except Exception as e:
    #         msg = QMessageBox()
    #         msg.setIcon(QMessageBox.Information)
    #         msg.setWindowTitle("Error!")
    #         msg.setText("An error occurred during export: " + str(e))
    #         # msg.setInformativeText("")
    #         msg.setStandardButtons(QMessageBox.Ok)


class Worker(QObject):

    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, df, output_path):
        super().__init__()
        self.df = df
        self.output_path = output_path

    @pyqtSlot()
    def run(self):
        """Long-running task."""
        df_split = array_split(self.df, 100)  # Divide into 100 (roughly) equal chunks.

        gettrace = getattr(sys, 'gettrace', None)
        debug = gettrace() is not None  # Running in debug mode
        if debug:
            print("Slowing down export progress bar for visualisation...")
        try:
            for i in range(100):
                # self.progressBar.setProperty("value", i + 1)
                if debug:
                    for j in range(1000):
                        pass
                df_split[i].to_csv(self.output_path, mode='a', header=False, index=False)  # mode='a' means append to file.
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
