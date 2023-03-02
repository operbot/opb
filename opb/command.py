# This file is placed in the Public Domain.


from .objects import Object

class Command(Object):

    cmds = Object()

    @staticmethod
    def add(self, cmd, func):
        setattr(Command.cmds, cmd, func)

    def handle(self, obj):
        func = getattr(Command.cmds, obj.cmd, None)
        if func:
            func(obj)

    def scan(self, mod):
        for _key, cmd in inspect.getmembers(mod, inspect.isfunction):
            if "event" in cmd.__code__.co_varnames:
                setattr(self.cmds, cmd.__name__, cmd)
