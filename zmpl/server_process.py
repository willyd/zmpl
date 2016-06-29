import sys
import subprocess


from zmpl import server

def _run_server():
    s = server.Server()
    s.run()

def start_server_process():
    # don't use multiprocessing as it does not play well with
    # the PTVS debug REPL
    p = subprocess.Popen([sys.executable, server.__file__])
    return p
    
