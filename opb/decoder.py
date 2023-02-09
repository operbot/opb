# This file is placed in the Public Domain.


import json


from .objects import Object, update


def __dir__():
    return (
            'ObjectDecoder',
            'load',
            'loads'
           )

__all__ = __dir__()


class ObjectDecoder(json.JSONDecoder):


    def decode(self, s, _w=None):
        value = json.loads(s)
        return Object(value)


def load(obj, opath):
    with open(opath, "r", encoding="utf-8") as ofile:
        res = json.load(ofile, cls=ObjectDecoder)
        update(obj, res)


def loads(jsonstr):
    return json.loads(jsonstr, cls=ObjectDecoder)
