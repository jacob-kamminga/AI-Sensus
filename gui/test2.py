"""
A simple example of an animated plot
"""
import sys

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg


class Test(QMainWindow):

    def __init__(self):
        super().__init__()
        self.figure = plt.figure()
        ax = self.figure.add_subplot(111)
        self.x = np.arange(0, 2 * np.pi, 0.01)
        self.line, = ax.plot(self.x, np.sin(self.x))
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(1)
        self.canvas.draw()
        self.setCentralWidget(self.canvas)
        self.i = 0

    def animate(self):
        self.line.set_ydata(np.sin(self.x + self.i / 10.0))  # update the data
        self.canvas.draw()
        print(self.i)
        self.i += 1
        if self.i > 100:
            self.timer.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    test = Test()
    test.show()
    sys.exit(app.exec_())
