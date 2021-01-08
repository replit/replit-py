import zmq


callbacks = {}
poller = zmq.Poller()


def _register(socket, callback):
    poller.register(socket, zmq.POLLIN)
    callbacks[socket] = callback


def listen():
    while True:
        try:
            socks = dict(poller.poll())
    
            # Handle every callback
            for sock in socks:
                message = sock.recv_multipart()
                callbacks[sock](message)

        except KeyboardInterrupt:
            break
