import zmq

from . import context as context
from . import logger as log
from .polling import _register
from .serialization import unpack, pack_topic
from .topic_tools import expand

def subscribe(topic):
    def decorator(callback):
        # Listen on a ZMQ port
        topic = expand(topic)
        socket = context.socket(zmq.SUB)
        socket.connect("ipc:///tmp/pub")
        socket.setsockopt(zmq.SUBSCRIBE, pack_topic(topic))

        # Call the callback and write the response to the stream
        def callback_wrapper(message):
            [topic, payload] = message
    
            payload = unpack(payload)
            callback(payload)
            
            log.debug("Callback for subscription %s called with data %s",
                      topic,
                      payload)
    
        log.debug("Subscribed to %s", topic)
        _register(socket, callback_wrapper)
    
        return callback

    return decorator

