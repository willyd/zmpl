import multiprocessing as mp

from . import server


def _run_server():
    s = server.Server()
    s.run()

def start_server_process():
    p = mp.Process(target=_run_server)
    p.start()
    return p
