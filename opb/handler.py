# This file is placed in the Public Domain.


import inspect
import queue
import threading


from .listens import Listens
from .objects import Object, register, update
from .runtime import launch


def __dir__():
    return (
            "Handler",
           ) 


__all__ = __dir__()


class Handler(Object):

    cmds = Object()
    errors = []
    threaded = False

    def __init__(self):
        Object.__init__(self)
        self.cbs = Object()
        self.queue = queue.Queue()
        self.stopped = threading.Event()
        register(self.cbs, "command", self.dispatch)
        Listens.add(self)


    @staticmethod
    def add(cmd):
        setattr(Handler.cmds, cmd.__name__, cmd)

    def clone(self, other):
        update(self.cmds, other.cmds)

    def dispatch(self, event):
        if not event.isparsed:
            event.parse(event.txt)
        if not event.orig:
            event.orig = repr(self)
        func = getattr(Handler.cmds, event.cmd, None)
        if func:
            try:
                func(event)
            except Exception as ex:
                exc = ex.with_traceback(ex.__traceback__)
                Handler.errors.append(exc)
                event.ready()
                return None
            event.show()
        event.ready()

    def handle(self, event):
        func = getattr(self.cbs, event.type, None)
        if not func:
            event.ready()
            return
        if Handler.threaded:
            event.__thr__ = launch(func, event)
        else:
            func(event)

    def loop(self):
        while not self.stopped.set():
            self.handle(self.poll())

    def poll(self):
        return self.queue.get()

    def put(self,event):
        if not event.orig:
            event.orig = repr(self)
        self.queue.put_nowait(event)

    def register(self, typ, cbs):
        setattr(self.cbs, typ, cbs)

    def scan(self, mod):
        for key, cmd in inspect.getmembers(mod, inspect.isfunction):
            if key.startswith("cb"):
                continue
            names = cmd.__code__.co_varnames
            if "event" in names:
                register(self.cmds, key, cmd)

    def stop(self):
        self.stopped.set()

    def start(self):
        self.stopped.clear()
        self.loop()
