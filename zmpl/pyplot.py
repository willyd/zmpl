import sys
from functools import partial

from zmpl import options
from .client import Client
from .server_process import start_server_process
from .functions import MODULE_LEVEL_FUNCTIONS

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
        reply = self._rpc_client.send(_create_rpc_message(self._rpc_id, fn, args, kwargs))
        return _proxy(self._rpc_client, reply)
    return _remote_call_impl

def _proxy(c, reply):
    global SERVER_TYPES
    type_ = reply['type']
    if type_ == '__object__':
        ret = reply['object']
        if isinstance(ret, (list, tuple)):
            ret_type = type(ret)
            ret = ret_type([_proxy(c, item) for item in ret])
        return ret
    elif type_ == '__proxy__':
       obj = reply['object'] 
       id_ = obj['id']
       if id_ is not None:
           name = obj['name']
           attrs = dict([(fn, _remote_call(fn)) for fn in obj['fns']])
           cls = SERVER_TYPES.setdefault(name, type(name, (object, ), attrs))
           p = cls()
           p._rpc_client = c
           p._rpc_id = id_
           return p
    elif type_ == '__error__':
        raise reply['object']
    else:
        raise Exception("Unkown reply type {}".format(type_))

class RemoteController(object):

    def __init__(self):
        self._rpc_id = None
        self.__rpc_client = None
        self._server_process = None

    def _initialize(self):
        if self._server_process is None and options['server_auto_start']:
            self._server_process = start_server_process()        
        if self.__rpc_client is None:
            self.__rpc_client = Client()

    @property
    def _rpc_client(self):
        self._initialize()
        return self.__rpc_client      

CLIENT_MODULE_LEVEL_FUNCTIONS = MODULE_LEVEL_FUNCTIONS + ['auto_draw', ]

for fn in CLIENT_MODULE_LEVEL_FUNCTIONS:
    setattr(RemoteController, fn, _remote_call(fn))
    
REMOTE_CONTROLLER = RemoteController()

module_obj = sys.modules[__name__]
for fn in CLIENT_MODULE_LEVEL_FUNCTIONS:
    setattr(module_obj, fn, getattr(REMOTE_CONTROLLER, fn))
