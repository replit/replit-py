import zmq

from . import context as context
from . import logger as log
from .serialization import pack, unpack, pack_bytes


class RPCProxy():
    def __init__(self, repl, service):
        self.repl = repl
        self.service = service

        #  Socket to talk to server
        self.socket = context.socket(zmq.DEALER)
        log.debug("Connecting to /tmp/router")
        self.socket.connect("ipc:///tmp/router")
        

    def __call__(self, *args, **kwargs):
        data = {
            'args': args,
            'kwargs': kwargs,
        }

        header = {
            'dest': self.repl,
            'destService': pack_bytes(self.service),
        }

        log.debug("Calling RPC at %s.%s", self.repl, self.service)
        self.socket.send_multipart([ b'', pack(header), pack(data) ])

        [_, header, response] = self.socket.recv_multipart()
        response = unpack(response)

        log.debug("RPC response from %s.%s", self.repl, self.service, response)
        return response
