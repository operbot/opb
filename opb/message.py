# This file is placed in the Public Domain.


import threading


from .default import Default
from .listens import Listens
from .objects import update
from .parsers import Parsed


def __dir__():
    return (
            'Message',
           )


__all__ = __dir__()


class Message(Default):

    __slots__ = ("__createtime__", "__parsed__", "__ready__", "__thr__")

    def __init__(self):
        Default.__init__(self)
        self.__ready__ = threading.Event()
        self.__thr__ = None
        self.channel = ""
        self.orig = ""
        self.result = []
        self.txt = ""
        self.type = "message"

    def bot(self):
        return Listens.byorig(self.orig)

    def done(self, txt=None):
        text = "ok " + (txt or "")
        text = text.rstrip()
        Listens.say(self.orig, text, self.channel)

    def error(self):
        pass

    def parse(self, txt):
        p = Parsed()
        p.parse(txt)
        update(self, p)

    def ready(self):
        self.__ready__.set()

    def reply(self, txt):
        self.result.append(txt)

    def show(self):
        for txt in self.result:
            Listens.say(self.orig, txt, self.channel)

    def wait(self):
        if self.__thr__:
            self.__thr__.join()
        self.__ready__.wait()
