# This file is placed in the Public Domain.


"parse"


from .default import Default
from .objects import Object


def __dir__():
    return (
            'Parsed',
           )


__all__ = __dir__()


class Parsed(Default):

    def __init__(self):
        Default.__init__(self)
        self.args = []
        self.gets = Object()
        self.isparsed = False
        self.sets = Object()
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
