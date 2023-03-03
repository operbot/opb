# This file is placed in the Public Domain.


"clients"


from .command import Command
from .handler import Handler
from .listens import Listens
from .message import Message
from .threads import launch


def __dir__():
    return (
            "Client",
           )


class Client(Handler):

    def __init__(self):
        Handler.__init__(self)
        Listens.add(self)
        self.register("command", Command.handle)
     
    def announce(self, txt):
        self.raw(txt)

    def event(self, txt):
        msg = Message()
        msg.type = "command"
        msg.orig = repr(self)
        msg.parse(txt)
        return msg

    def one(self, txt):
        return self.handle(self.event(txt))

    def raw(self, txt):
        pass

    def say(self, channel, txt):
        self.raw(txt)

    def start(self):
        launch(self.loop)

    def stop(self):
        self.stopped.set()
        self.queue.put_nowait(None)
