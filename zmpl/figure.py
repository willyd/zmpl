import sys

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt4 import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt4agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure as MplFigure
from PyQt4 import QtCore, QtGui


class MplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = MplFigure(figsize=(width, height), dpi=dpi)
        # self.axes = self.fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        # self.axes.hold(False)

        # self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class MyStaticMplCanvas(MplCanvas):
    """Simple canvas with a sine plot."""

    def compute_initial_figure(self):
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2*np.pi*t)
        self.axes.plot(t, s)


class MyDynamicMplCanvas(MplCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, *args, **kwargs):
        MplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

    def compute_initial_figure(self):
        self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')

    def update_figure(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        l = [random.randint(0, 10) for i in range(4)]

        self.axes.plot([0, 1, 2, 3], l, 'r')
        self.draw()

class Figure(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.vbox = QtGui.QVBoxLayout(self)
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.navi_toolbar = NavigationToolbar(self.canvas, self)
        self.vbox.addWidget(self.navi_toolbar)
        self.vbox.addWidget(self.canvas)

    def add_subplot(self, *args, **kwargs):
        ax = self.canvas.fig.add_subplot(*args, **kwargs)
        # self.canvas.updateGeometry()
        self.canvas.draw()
        return ax
