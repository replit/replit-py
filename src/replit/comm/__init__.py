import logging
import zmq

import replit.rpc.*
import replit.pubsub.*

# Set package logging config
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Single zmq context for all magic replit connections
context = zmq.Context()

