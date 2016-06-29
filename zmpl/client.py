"""
This module defines a client for the plotting server
"""

import zmq
from zmpl import options

class Client(object):
    """
    Client class to connect to the plotting server
    """
    def __init__(self):
        """
        Initializes the client and connects to the default address
        """
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(options['default_address'])

    def send(self, request):
        """
        Send a request to the server, i.e. RPC call
        """
        self.socket.send_pyobj(request)
        reply = self.socket.recv_pyobj()
        return reply
