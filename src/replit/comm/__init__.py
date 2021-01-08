import logging
import zmq


# Set package logging config
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Single zmq context for all magic replit connections
context = zmq.Context()


from .rpc_provider import rpc
from .subscriber import subscribe
from .polling import listen
