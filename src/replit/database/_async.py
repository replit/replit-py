"""Allows asyncio.run to work in async environment."""
import asyncio
import sys
import threading
from typing import Any, Callable, List

asyncio._run = asyncio.run


class AsyncThread(threading.Thread):
    def __init__(self, res: List[None], exc: List[None], func: Callable) -> None:
        self.result = res
        self.exc = exc
        self.func = func
        threading.Thread.__init__(self)

    def run(self) -> Any:
        def inner(func: Callable) -> Any:
            try:
                res = asyncio.run(func)
            except Exception:
                self.exc[0] = sys.exc_info()
                res = ""
            return res

        self.result[0] = inner(self.func)


def run(func: Callable) -> Any:
    def error() -> Any:
        ret = [None]
        exc = [None]
        thread = AsyncThread(ret, exc, func)
        thread.start()
        thread.join()
        exc = exc[0]
        if exc is not None:
            raise exc[1].with_traceback(exc[2])
            sys.exit(1)
        return ret[0]

    try:
        return asyncio._run(func)
    except RuntimeError:
        return error()
    except RuntimeWarning:
        return error()
