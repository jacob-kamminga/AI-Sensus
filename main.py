import platform
import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

from gui import gui

try:
    import apt
except ImportError:
    pass

try:
    import winreg
except ImportError:
    pass


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


def is_tool(name) -> bool:
    """Check whether `name` is on PATH and marked as executable."""
    from shutil import which

    return which(name) is not None


def win_software_installed(hive, flag):
    aReg = winreg.ConnectRegistry(None, hive)
    aKey = winreg.OpenKey(
        aReg,
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        0,
        winreg.KEY_READ | flag,
    )

    count_subkey = winreg.QueryInfoKey(aKey)[0]

    software_list = []

    for i in range(count_subkey):
        software = {}
        try:
            asubkey_name = winreg.EnumKey(aKey, i)
            asubkey = winreg.OpenKey(aKey, asubkey_name)
            software["name"] = winreg.QueryValueEx(asubkey, "DisplayName")[0]

            try:
                software["version"] = winreg.QueryValueEx(asubkey, "DisplayVersion")[0]
            except EnvironmentError:
                software["version"] = "undefined"
            try:
                software["publisher"] = winreg.QueryValueEx(asubkey, "Publisher")[0]
            except EnvironmentError:
                software["publisher"] = "undefined"
            software_list.append(software)
        except EnvironmentError:
            continue

    return software_list


def is_lav_filters():
    """ Check if LavFilters is present """
    if platform.system() == 'Windows':
        software_list = (
                win_software_installed(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY)
                + win_software_installed(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY)
                + win_software_installed(winreg.HKEY_CURRENT_USER, 0)
        )
        if not any("LAV Filters" in software["name"] for software in software_list):
            # does not exist
            return False
    else:
        cache = apt.Cache()
        cache.open()
        try:
            # print("lav filters")
            return cache["gst123"].is_installed
        except Exception:
            # does not exist
            return False
    return True


def dependencies_installed() -> bool:
    """Check whether all dependencies have been installed on the system."""
    return is_tool('exiftool') and is_tool('ffmpeg') and is_lav_filters()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    project = gui.GUI()
    # project.setWindowTitle("AI Sensus")
    project.show()

    # Check whether all dependencies have been installed
    if not dependencies_installed():
        # TODO: Show user dialog
        exit()

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
        std_err_handler.err_msg.connect(project.std_err_post)

    elif gettrace():  # Running in debug mode.
        print("Running in debug mode.")

    sys.exit(app.exec())
