import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

from gui import gui

class StdErrHandler(QtCore.QObject):
    """
    This class provides an alternate write() method for stderr messages.
    Messages are sent by pyqtSignal to the pyqtSlot in the main window.
    """
    err_msg = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self)

    def write(self, msg):
        # stderr messages are sent to this method.
        self.err_msg.emit(msg)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = gui.GUI()
    if main_window.app_controller.prev_project_dir is None:
        main_window.show_welcome_dialog()
    main_window.init_project()
    main_window.show()

    # Check if running in normal mode or debug mode.
    gettrace = getattr(sys, 'gettrace', None)

    if gettrace() is None:  # Running in normal mode.
        print("Running in normal mode.")
        # Override the except hook so it will print the traceback to stdout/stderr
        sys.excepthook = except_hook

        # Create the stderr handler and point stderr to it
        std_err_handler = StdErrHandler()
        sys.stderr = std_err_handler

        # Connect err_msg signal to message box method in main window
        std_err_handler.err_msg.connect(main_window.std_err_post)

    elif gettrace():  # Running in debug mode.
        print("Running in debug mode.")

    sys.exit(app.exec())
