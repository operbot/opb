# This file is placed in the Public Domain.


"command"


import inspect


from .objects import Object
from .message import Message


def __dir__():
    return (
            'Command',
            'scan'
           )


class Command(Object):

    cmds = Object()

    @staticmethod
    def add(cmd, func):
        setattr(Command.cmds, cmd, func)

    @staticmethod
    def handle(obj):
        func = getattr(Command.cmds, obj.cmd, None)
        if func:
            func(obj)
            obj.show()


def command(txt):
    e = Message()
    e.parse(txt)
    Command.handle(e)
    return e


def scan(mod):
    for _key, cmd in inspect.getmembers(mod, inspect.isfunction):
        if "event" in cmd.__code__.co_varnames:
            Command.add(cmd.__name__, cmd)
