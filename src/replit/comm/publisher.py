import zmq

from . import context as context
from . import logger as log
from .serialization import pack, pack_topic
from .topic_tools import expand

publish_sockets = {}

def publish(topic, message):
    topic = expand(topic)

    try:
        socket = publish_sockets[topic]
        log.debug("Using cached publisher for %s", topic)

    except KeyError:
        log.info("Connecting new publisher for %s", topic)
        socket = context.socket(zmq.PUB)
        socket.connect("ipc:///tmp/sub")

    log.debug("Publishing message %s to %s", message, topic)
    socket.send_multipart([pack_topic(topic), pack(message)])
    publish_sockets[topic] = socket
