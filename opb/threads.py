# This file is placed in the Public Domain.


"thread"


import queue
import threading


def __dir__():
    return (
            'Thread',
            'launch'
           )


__all__ = __dir__()


class Thread(threading.Thread):

    def __init__(self, func, thrname, *args, daemon=True):
        super().__init__(None, self.run, thrname, (), {}, daemon=daemon)
        self._result = None
        self.name = thrname or "%s.%s" % (func.__module__, func.__name__)
        self.queue = queue.Queue()
        self.queue.put_nowait((func, args))
        self.sleep = None

    def __iter__(self):
        return self

    def __next__(self):
        for k in dir(self):
            yield k

    def join(self, timeout=None):
        super().join(timeout)
        return self._result

    def run(self) -> None:
        func, args = self.queue.get()
        self._result = func(*args)


def launch(func, *args, **kwargs):
    thrname = kwargs.get("name", func.__name__)
    thr = Thread(func, thrname, *args)
    thr.start()
    return thr
