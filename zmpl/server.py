import re
import sys
import time

import matplotlib
from matplotlib import pyplot as plt
import zmq
try:
    from PyQt5 import QtCore, QtGui, QtWidgets
    matplotlib.use('QT5Agg')
except ImportError:
    from PyQt4 import QtCore, QtGui
    QtWidgets = QtGui
    matplotlib.use('QT4Agg')

from zmpl import options
from zmpl.functions import MODULE_LEVEL_FUNCTIONS


class Listener(QtCore.QObject):

    message = QtCore.pyqtSignal(object)

    def __init__(self):

        QtCore.QObject.__init__(self)

        # Socket to talk to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(options['default_address'])

        self.running = True
        self.mutex = QtCore.QMutex()
        self.condition = QtCore.QWaitCondition()

        # result from RPC
        self.result = None

    def loop(self):
        while self.running:
            try:
                # received message without blocking
                msg = self.socket.recv_pyobj(flags=zmq.NOBLOCK)
                # change result to None
                self.mutex.lock()
                self.result = None
                # send signal to main thread
                self.message.emit(msg)
                # wait for main thread to be done
                self.condition.wait(self.mutex)
                # MUST have mutex locked here! unlock only after wait
                self.mutex.unlock()
                # send back the data set by main thread
                self.mutex.lock()
                self.socket.send_pyobj(self.result)
                self.mutex.unlock()
            except zmq.ZMQError as e:
                if e.errno == zmq.EAGAIN:
                    time.sleep(0.01)
                else:
                    raise e

plt_figure = plt.figure


def _figure_auto_show(*args, **kwargs):
    f = plt_figure(*args, **kwargs)
    f.show()
    return f

plt.figure = _figure_auto_show


class ServerMainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        frame = QtWidgets.QFrame()
        label = QtWidgets.QLabel("listening")
        self.text_edit = QtWidgets.QTextEdit()

        layout = QtWidgets.QVBoxLayout(frame)
        layout.addWidget(label)
        layout.addWidget(self.text_edit)

        self.setCentralWidget(frame)

        self.thread = QtCore.QThread()
        self.listener = Listener()
        self.listener.moveToThread(self.thread)

        self.thread.started.connect(self.listener.loop)
        self.listener.message.connect(self.signal_received)

        self._auto_draw = True

        self.objects = {None: self}

        QtCore.QTimer.singleShot(0, self.thread.start)

    def process_remote_call(self, message):
        # get the scope or object called
        id_ = message['id']
        # get the function or method
        fn = message['fn']
        # retreive the object from its id (None means self)
        scope_obj = self.objects[id_]
        # call the function
        result_obj = getattr(scope_obj, fn)(
            *message['args'], **message['kwargs'])
        if self._auto_draw:
            plt.draw()
        return result_obj

    def generate_result_dict(self, result):
        if result.__class__.__module__.startswith('matplotlib'):
            self.objects[id(result)] = result
            result_dict = dict(type='__proxy__',
                               object=dict(id=id(result),
                                           name=result.__class__.__name__,
                                           fns=[]
                                           )
                               )
            for attr in dir(result):
                special = re.match(r"__.+__", attr)
                # if special:
                #print('attr {} is special'.format(attr))
                if not special and callable(getattr(result, attr)):
                    #print('adding {}'.format(attr))
                    result_dict['object']['fns'].append(attr)
        elif isinstance(result, (list, tuple)):
            ret_type = type(result)
            ret = ret_type([self.generate_result_dict(item)
                            for item in result])
            result_dict = dict(type='__object__', object=ret)
        else:
            result_dict = dict(type='__object__', object=result)
        return result_dict

    def signal_received(self, message):
        # we received a remote call process it
        try:
            self.text_edit.append("Calling %s\n" % message['fn'])
            try:
                result = self.process_remote_call(message)
            except Exception as e:
                result = None
                self.text_edit.append("Error: %s\n" % e)
            # append received call to text edit
            res = self.generate_result_dict(result)
        except Exception as e:
            res = dict(type='__error__', object=e)
        # set the data to send back and wake the waiting thread
        self.listener.mutex.lock()
        self.listener.result = res
        self.listener.condition.wakeAll()
        self.listener.mutex.unlock()

    def closeEvent(self, event):
        self.listener.running = False
        self.thread.quit()
        self.thread.wait()

    def auto_draw(self, *args, **kwargs):
        if args:
            assert type(args[0]) == bool
            self._auto_draw = args[0]
        return self._auto_draw


def _plt_call(fn):
    def _plt_call_impl(self, *args, **kwargs):
        plt_fn = getattr(plt, fn)
        res = plt_fn(*args, **kwargs)
        return res
    return _plt_call_impl

for fn in MODULE_LEVEL_FUNCTIONS:
    try:
        getattr(ServerMainWindow, fn)
    except AttributeError:
        setattr(ServerMainWindow, fn, _plt_call(fn))


class Server(object):

    def __init__(self):
        pass

    def run(self):
        app = QtWidgets.QApplication(sys.argv)
        mw = ServerMainWindow()
        mw.show()
        sys.exit(app.exec_())

if __name__ == '__main__':
    s = Server()
    s.run()
