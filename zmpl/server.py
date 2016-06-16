import sys
from PyQt4 import QtCore, QtGui
import zmq
import matplotlib
matplotlib.use('QT4Agg')
from matplotlib import pyplot as plt


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
            self.message.emit(string)
            self.send_pyobj(msg)

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
  
          self.thread = QtCore.QThread()
          self.zeromq_listener = ZeroMQ_Listener()
          self.zeromq_listener.moveToThread(self.thread)
          
          self.thread.started.connect(self.zeromq_listener.loop)
          self.zeromq_listener.message.connect(self.signal_received)
          
          QtCore.QTimer.singleShot(0, self.thread.start)
      
      def signal_received(self, message):
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
            

