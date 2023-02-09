# This file is placed in the Public Domain.


import time


from .. import Object
from .. import Storage, save
from .. import elapsed, fntime


def __dir__():
    return (
            'Log',
            'log',
           )


class Log(Object):

    def __init__(self):
        super().__init__()
        self.txt = ""


Storage.add(Log)


def log(event):
    if not event.rest:
        nmr = 0
        for fnm, obj in Storage.find("log"):
            event.reply("%s %s %s" % (
                                      nmr,
                                      obj.txt,
                                      elapsed(time.time() - fntime(fnm)))
                                     )
            nmr += 1
        if not nmr:
            event.reply("log <txt>")
        return
    obj = Log()
    obj.txt = event.rest
    save(obj)
    event.done()
