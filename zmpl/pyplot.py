from functools import partial

from .client import Client
from .server_process import start_server_process

CLIENT = None
SERVER_PROCESS = None
SERVER_TYPES = {}

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
    
def _remote_call(fn):
    def _remote_call_impl(self, *args, **kwargs):
        reply = self.client.send(_create_rpc_message(self.id, fn, args, kwargs))
        return _proxy(self.client, reply)
    return _remote_call_impl

def _proxy(c, reply):
    global SERVER_TYPES
    id_ = reply['id']
    assert id_ is not None
    name = reply['name']
    attrs = dict([(fn, _remote_call(fn)) for fn in reply['fns']])
    cls = SERVER_TYPES.setdefault(name, type(name, (object, ), attrs))
    p = cls()
    p.client = c
    p.id = id_
    return p
    
def figure(*args, **kwargs):
    c = _initialize()    
    reply = c.send(_create_rpc_message(None, _function_name(), args, kwargs))
    return _proxy(c, reply)
