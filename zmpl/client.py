import zmq

class Client(object):
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://127.0.0.1:5000")

    def send(self, msg):
        self.socket.send_pyobj(msg)        
        msg_in = self.socket.recv_pyobj()
        print "Received", msg