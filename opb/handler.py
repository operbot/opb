# This file is placed in the Public Domain.


import inspect
import queue
import threading


from .default import Default
from .listens import Listens
from .objects import Object, update


def __dir__():
    return (
            'Handler',
           )


__all__ = __dir__()



class Handler(Object):

    def __init__(self):
        Object.__init__(self)
        self.cmds = Object()
        self.queue = queue.Queue()
        self.stopped = threading.Event()
        self.target = "cmd"

    def clone(self, other):
        update(self.cmds, other.cmds)

    def handle(self, evt):
        func = getattr(self.cmds, getattr(evt, self.target, None), None)
        if func:
            func(evt)
            evt.show()

    def loop(self):
        while not self.stopped.set():
            self.handle(self.poll())

    def poll(self):
        return self.queue.get()

    def put(self, evt):
        self.queue.put_nowait(evt)

    def register(self, cmd, func):
        setattr(self.cmds, cmd, func)

    def scan(self, mod):
        for _key, cmd in inspect.getmembers(mod, inspect.isfunction):
            if "event" in cmd.__code__.co_varnames:
                setattr(self.cmds, cmd.__name__, cmd)

    def wait(self):
        while 1:
            time.sleep(1.0)
