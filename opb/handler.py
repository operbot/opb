# This file is placed in the Public Domain.


import inspect
import queue
import threading


from .listens import Listens
from .objects import Object
from .threads import launch


class Handler(Object):

    cmds = Object()
    errors = []


    def __init__(self):
        Object.__init__(self)
        self.cbs = Object()
        self.queue = queue.Queue()
        self.stopped = threading.Event()
        self.register("command", self.handle)
        Listens.add(self)

    def dispatch(self, event):
        event.orig = event.orig or repr(self)
        func = getattr(self.cbs, event.type, None)
        if not func:
            event.ready()
            return
        if event.threaded:
            event.__thr__ = launch(func, event)
        else:
            func(event)

    def handle(self, event):
        if not event.isparsed:
            event.parse(event.txt)
        func = getattr(self.cmds, event.cmd, None)
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

    def loop(self):
        while not self.stopped.set():
            self.dispatch(self.poll())

    def poll(self):
        return self.queue.get()

    def put(self,event):
        if not event.orig:
            event.orig = repr(self)
        self.queue.put_nowait(event)

    def register(self, typ, cbs):
        if typ not in self.cbs:
            setattr(self.cbs, typ, cbs)

    def stop(self):
        self.stopped.set()

    def start(self):
        self.stopped.clear()
        launch(self.loop)


def scan(mod):
    for key, cmd in inspect.getmembers(mod, inspect.isfunction):
        if key.startswith("cb"):
            continue
        names = cmd.__code__.co_varnames
        if "event" in names:
            setattr(Handler.cmds, key, cmd)
