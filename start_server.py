import sys
from PyQt4 import QtCore, QtGui
import zmq
import matplotlib
matplotlib.use('QT4Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MyStaticMplCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""

    def compute_initial_figure(self):
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2*np.pi*t)
        self.axes.plot(t, s)


class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
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

class MyFigure(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.vbox = QtGui.QVBoxLayout(self)
        self.sc = MyStaticMplCanvas(self, width=5, height=4, dpi=100)
        self.vbox.addWidget(self.sc)
        

class ZeroMQ_Listener(QtCore.QObject):

    message = QtCore.pyqtSignal(object)
    
    def __init__(self):
       
        QtCore.QObject.__init__(self)
        
        # Socket to talk to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://127.0.0.1:5000")        
        
        self.running = True
    
    def loop(self):
        while self.running:
            msg = self.socket.recv_pyobj()
            self.message.emit(msg)
            self.socket.send_pyobj(msg)

class ZeroMQ_Window(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        frame = QtGui.QFrame()
        label = QtGui.QLabel("listening")
        self.text_edit = QtGui.QTextEdit()
        
        layout = QtGui.QVBoxLayout(frame)
        layout.addWidget(label)
        layout.addWidget(self.text_edit)
        
        self.setCentralWidget(frame)

        self.figs = []

        self.thread = QtCore.QThread()
        self.zeromq_listener = ZeroMQ_Listener()
        self.zeromq_listener.moveToThread(self.thread)
        
        self.thread.started.connect(self.zeromq_listener.loop)
        self.zeromq_listener.message.connect(self.signal_received)
        
        QtCore.QTimer.singleShot(0, self.thread.start)

        
    
    def signal_received(self, message):
        fig = MyFigure(self)
        self.figs.append(fig)
        fig.show()
        self.text_edit.append("%s\n"% message)

    def closeEvent(self, event):
        self.zeromq_listener.running = False
        self.thread.quit()
        self.thread.wait()            

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)       
    mw = ZeroMQ_Window()
    mw.show()       
    sys.exit(app.exec_())
            

