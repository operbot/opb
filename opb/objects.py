# This file is placed in the Public Domain.


"Big Object"


import datetime
import os
import uuid
import _thread


def __dir__():
    return (
            'Object',
            'format',
            'items',
            'keys',
            'kind',
            'oid',
            'search',
            'update',
            'values'
            )


__all__ = __dir__()


disklock = _thread.allocate_lock()


class Object:

    def __init__(self, *args, **kwargs):
        if args:
            val = args[0]
            if isinstance(val, list):
                update(self, dict(val))
            elif isinstance(val, zip):
                update(self, dict(val))
            elif isinstance(val, dict):
                update(self, val)
            elif isinstance(val, Object):
                update(self, vars(val))
        if kwargs:
            self.__dict__.update(kwargs)

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __str__(self):
        return str(self. __dict__)


def format(self, args="", skip="", plain=False):
    res = []
    keyz = []
    if "," in args:
        keyz = args.split(",")
    if not keyz:
        keyz = keys(self)
    for key in keyz:
        if key.startswith("_"):
            continue
        if skip:
            skips = skip.split(",")
            if key in skips:
                continue
        value = getattr(self, key, None)
        if not value:
            continue
        if " object at " in str(value):
            continue
        txt = ""
        if plain:
            value = str(value)
        if isinstance(value, str) and len(value.split()) >= 2:
            txt = f'{key}="{value}"'
        else:
            txt = f'{key}={value}'
        res.append(txt)
    txt = " ".join(res)
    return txt.strip()


def items(self):
    if isinstance(self, type({})):
        return self.items()
    return self.__dict__.items()


def keys(self):
    return self.__dict__.keys()


def kind(self):
    kin = str(type(self)).split()[-1][1:-2]
    if kin == "type":
        kin = self.__name__
    return kin


def oid(self):
    return os.path.join(
                        kind(self),
                        str(uuid.uuid4().hex),
                        os.sep.join(str(datetime.datetime.now()).split()),
                       )


def search(self, selector):
    res = False
    select = Object(selector)
    for key, value in items(select):
        try:
            val = getattr(self, key)
        except AttributeError:
            continue
        if str(value) in str(val):
            res = True
            break
    return res


def update(self, data):
    for key, value in items(data):
        setattr(self, key, value)


def values(self):
    return self.__dict__.values()
