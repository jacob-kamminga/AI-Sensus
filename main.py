import sys

from PyQt5.QtWidgets import QApplication

from gui import gui

if __name__ == '__main__':
    app = QApplication(sys.argv)
    project = gui.GUI()
    project.show()
    sys.exit(app.exec_())
