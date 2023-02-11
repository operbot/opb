# This file is placed in the Public Domain.


import inspect
import queue
import threading


from .objects import Default, Object, name, register, update
from .runtime import launch


def __dir__():
    return (
            "Event",
            "Handler",
            "scan"
           ) 


__all__ = __dir__()


class Handler(Object):

    cmds = Object()
    errors = []
    threaded = True

    def __init__(self):
        Object.__init__(self)
        self.cbs = Object()
        self.queue = queue.Queue()
        self.stopped = threading.Event()
        register(self.cbs, "command", self.dispatch)
        Listens.add(self)

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


class Listens(Object):

    objs = []

    @staticmethod
    def add(obj):
        if repr(obj) not in [repr(x) for x in Listens.objs]:
            Listens.objs.append(obj)

    @staticmethod
    def announce(txt):
        for obj in Listens.objs:
            obj.announce(txt)

    @staticmethod
    def byorig(orig):
        res = None
        for obj in Listens.objs:
            if repr(obj) == orig:
                res = obj
                break
        return res

    @staticmethod
    def say(orig, txt, channel=None):
        bot = Listens.byorig(orig)
        if bot:
            if channel:
                bot.say(channel, txt)
            else:
                bot.raw(txt)


class Event(Default):

    def __init__(self):
        Default.__init__(self)
        self.__ready__ = threading.Event()
        self.__thr__ = None
        self.args = []
        self.gets = Object()
        self.isparsed = False
        self.result = []
        self.sets = Object()
        self.type = "command"
        self.toskip = Object()

    def parsed(self):
        return self.isparsed

    def parse(self, txt):
        self.isparsed = True
        self.otxt = txt
        spl = self.otxt.split()
        args = []
        _nr = -1
        for word in spl:
            if word.startswith("-"):
                try:
                    self.index = int(word[1:])
                except ValueError:
                    self.opts = self.opts + word[1:2]
                continue
            try:
                key, value = word.split("==")
                if value.endswith("-"):
                    value = value[:-1]
                    setattr(self.toskip, value, "")
                setattr(self.gets, key, value)
                continue
            except ValueError:
                pass
            try:
                key, value = word.split("=")
                setattr(self.sets, key, value)
                continue
            except ValueError:
                pass
            _nr += 1
            if _nr == 0:
                self.cmd = word
                continue
            args.append(word)
        if args:
            self.args = args
            self.rest = " ".join(args)
            self.txt = self.cmd + " " + self.rest
        else:
            self.txt = self.cmd

    def ready(self):
        self.__ready__.set()

    def reply(self, txt):
        self.result.append(txt)

    def show(self):
        for txt in self.result:
            Listens.say(self.orig, txt, self.channel)

    def wait(self):
        self.__ready__.wait()
