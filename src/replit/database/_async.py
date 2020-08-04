import threading
import asyncio
import sys
asyncio._run = asyncio.run


class AsyncThread(threading.Thread):
    def __init__(self, res, exc, func):
        self.result = res
        self.exc = exc
        self.func = func
        threading.Thread.__init__(self)

    def run(self):
        def inner(func):
            try:
                res = asyncio.run(func)
            except Exception as e:
                self.exc[0] = sys.exc_info()
                res = ''
            return res

        self.result[0] = inner(self.func)


def run(func):
    def error():
        ret = [None]
        exc = [None]
        thread = AsyncThread(ret, exc, func)
        thread.start()
        thread.join()
        exc = exc[0]
        if exc != None:
            raise exc[1].with_traceback(exc[2])
            sys.exit(1)
        return ret[0]

    try:
        return asyncio._run(func)
    except RuntimeError:
        return error()
    except RuntimeWarning:
        return error()
