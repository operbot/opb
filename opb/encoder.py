# This file is placed in the Public Domain.


"object encoder"


import json


from .objects import Object


def __dir__():
    return (
            'ObjectEncoder',
            'dumps'
           ) 


__all__ = __dir__()


class ObjectEncoder(json.JSONEncoder):


    def default(self, o):
        if isinstance(o, dict):
            return o.items()
        if isinstance(o, Object):
            return vars(o)
        if isinstance(o, list):
            return iter(o)
        if isinstance(o,
                      (type(str), type(True), type(False),
                       type(int), type(float))
                     ):
            return str(o)
        try:
            return json.JSONEncoder.default(self, o)
        except TypeError:
            return str(o)


def dumps(obj):
    return json.dumps(obj, cls=ObjectEncoder)
