import zmq

from . import context as context
from . import logger as log
from .serialization import pack, unpack, pack_topic
from .polling import _register


# Decorator that marks a function as being an rpc target
def rpc(callback):
    name = callback.__name__

    # Listen on a ZMQ port
    socket = context.socket(zmq.ROUTER)
    socket.setsockopt(zmq.IDENTITY, pack_topic(name.encode))
    log.debug("Connecting to /tmp/router")
    socket.connect("ipc:///tmp/router")

    # Call the callback and write the response to the stream
    def callback_wrapper(message):
        # Decode the message to get the RPC arguments
        [session, _, routing, payload] = message

        payload = unpack(message[-1])
        args = payload['args']
        kwargs = payload['kwargs']

        # Call the RPC provider
        log.info("Recieved RPC call to %s with %s", name, args, kwargs)
        try:
            response = callback(*args, **kwargs)
        except Exception as e:
            log.warning("Exception occured while processing RPC callback %s", e)
            response = e

        # Update the routing information to use for reply
        routing = unpack(routing)
        routing['dest'] = routing['source']
        routing['destService'] = routing['sourceService']
        routing = pack(routing)

        log.info("Sending RPC response from %s with %s", name, response)
        socket.send_multipart(message[:2] + [routing, pack(response)])

    # Register the socket so it can be polled
    log.info("Loaded RPC callback for %s", name)
    _register(socket, callback_wrapper)

    return callback
