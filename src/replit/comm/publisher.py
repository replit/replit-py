import zmq

from replit.comm import context as context
from replit.comm import logger as log
from replit.comm.serialization import pack, unpack

publish_sockets = {}

def publish(topic, message):
    try:
        socket = publish_sockets[topic]
        log.debug("Using cached publisher for %s", topic)

    except KeyError:
        log.info("Connecting new publisher for %s", topic)
        socket = context.socket(zmq.PUB)
        socket.connect("ipc:///tmp/sub")

    log.debug("Publishing message %s to %s", message, topic)
    socket.send_multipart([topic.encode('ascii'), pack(message)])

