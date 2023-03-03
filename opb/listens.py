# This is placed in the Public Domain.


"listens"


from .objects import Object


def __dir__():
    return (
            'Listens',
           )


class Listens(Object):

    objs = []

    @staticmethod
    def add(obj):
        Listens.objs.append(obj)

    @staticmethod
    def announce(txt):
        for obj in Listens.objs:
            obj.announce(txt)

    @staticmethod
    def byorig(orig):
        for obj in Listens.objs:
            if repr(obj) == orig:
                return obj

    @staticmethod
    def say(orig, txt, channel=None):
        bot = Listens.byorig(orig)
        if bot:
            if channel:
                bot.say(channel, txt)
            else:
                bot.raw(txt)

    