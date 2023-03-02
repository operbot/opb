# This file is placed in the Public Domain.


from .default import Default
from .listens import Listens
from .objects import Object


def __dir__():
    return (
            'Message',
           )


__all__ = __dir__()


class Message(Default):

    def __init__(self, *args, **kwargs):
        Default.__init__(self, *args, **kwargs)      
        self.result = []
        self.type = "cmd"

    def parse(self, txt):
        if not txt:
            return self
        splitted = txt.split()
        self.cmd = splitted.pop(0)
        self.selector = Object(zip({tuple(x.split("==")) for x in splitted if "==" in x}))
        self.args = list({x for x in splitted if "==" not in x})
        self.rest = " ".join(self.args)
        return self

    def reply(self, txt):
        self.result.append(txt)

    def show(self):
        for txt in self.result:
            Listens.say(self.orig, txt)
