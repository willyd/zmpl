from . server_process import start_server_process
from . client import Client

CLIENT = None
SERVER_PROCESS = None

def _get_client():
    global CLIENT
    if CLIENT is None:
        CLIENT = Client()
    return CLIENT

def _start_server_process():
    global SERVER_PROCESS
    if SERVER_PROCESS is None:
        SERVER_PROCESS = start_server_process()
    return SERVER_PROCESS

def _initialize():
    _start_server_process()
    return _get_client()

def _create_rpc_message(id_, fn, args, kwargs):
    return dict(id=id_,
                fn=fn,
                args=args,
                kwargs=kwargs)

def _function_name():
    import traceback
    return traceback.extract_stack(None, 2)[0][2]


def figure(*args, **kwargs):
    c = _initialize()    
    reply = c.send(_create_rpc_message(None, _function_name(), args, kwargs))
    print 'reply', reply




