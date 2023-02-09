# This file is placed in the Public Domain.


import json
import sys


from .objects import Object
from .utility import cdir


def __dir__():
    return (
            'ObjectEncoder',
            'dump',
            'dumps',
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


def dump(obj, opath):
    sys.stdout.flush()
    cdir(opath)
    with open(opath, "w", encoding="utf-8") as ofile:
        json.dump(
            obj.__dict__, ofile, cls=ObjectEncoder, indent=4, sort_keys=True
        )
    return opath


def dumps(obj):
    return json.dumps(obj, cls=ObjectEncoder)
