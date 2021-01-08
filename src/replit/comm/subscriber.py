import zmq

from replit.comm import context as context
from replit.comm import logger as log
from replit.comm.serialization import pack, unpack

def subscribe(topic):
    def decorator(callback):
        # Listen on a ZMQ port
        socket = context.socket(zmq.SUB)
        socket.connect("ipc:///tmp/pub")
        socket.setsockopt(zmq.SUBSCRIBE, topic.encode('ascii'))

        # Call the callback and write the response to the stream
        def callback_wrapper(message):
            [topic, payload] = message
    
            payload = unpack(payload)
            callback(payload)
            
            log.debug("Callback for subscription %s called with data %s",
                      topic,
                      payload)
    
        log.debug("Subscribed to %s", topic)
        replit._register(socket, callback_wrapper)
    
        return callback

    return decorator

