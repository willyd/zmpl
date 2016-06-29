import sys
import subprocess
import zmq

from zmpl import options, server

def _run_server():
    s = server.Server()
    s.run()

def start_server_process():
    # don't use multiprocessing as it does not play well with
    # the PTVS debug REPL
    try:
        # figure out if a server is already running
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(options['default_address'])
        socket.close()
        p = subprocess.Popen([sys.executable, server.__file__])
        return p
    except zmq.ZMQError:
        # returning None here will cause us to 
        # try binding at every single call
        return True
    
