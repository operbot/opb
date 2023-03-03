# This file is placed in the Public Domain.


from .default import Default
from .listens import Listens
from .objects import Object, tostr


def __dir__():
    return (
            'Message',
           )


__all__ = __dir__()


class Message(Default):

    def __init__(self, *args, **kwargs):
        Default.__init__(self, *args, **kwargs)      
        self.args = []
        self.result = []
        self.txt = ""
        self.type = "cmd"

    def parse(self, txt):
        splitted = txt.split()
        if splitted:
            self.cmd = splitted.pop(0)
        if splitted:
            self.args = list({x for x in splitted if "==" not in x})
            x = Object()
            self.gets = Object({x.split("==") for x in splitted if x and "==" in x[0]})
            self.rest = " ".join(self.args)
        return self

    def reply(self, txt):
        self.result.append(txt)

    def show(self):
        for txt in self.result:
            Listens.say(self.orig, txt, self.channel)
