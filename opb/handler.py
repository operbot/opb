# This file is placed in the Public Domain.


"handler"


import queue
import threading


from .command import Command
from .objects import Object, update


def __dir__():
    return (
            'Handler',
           )


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
