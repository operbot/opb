# This file is placed in the Public Domain.


import inspect
import queue
import threading


from .command import Command
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
        self.cbs = Object()
        self.queue = queue.Queue()
        self.stopped = threading.Event()

    def clone(self, other):
        update(self.cmds, other.cmds)

    def dispatch(self, evt):
        Command.handle(evt)

    def handle(self, obj):
        func = getattr(self.cbs, obj.type, None)
        if func:
            func(obj)

    def loop(self):
        while not self.stopped.set():
            self.handle(self.poll())

    def poll(self):
        return self.queue.get()

    def put(self, evt):
        self.queue.put_nowait(evt)

    def register(self, cmd, func):
        setattr(self.cbs, cmd, func)

    def scan(self, mod):
        for _key, cmd in inspect.getmembers(mod, inspect.isfunction):
            if "event" in cmd.__code__.co_varnames:
                setattr(self.cbs, cmd.__name__, cmd)

    def wait(self):
        while 1:
            time.sleep(1.0)
