# This is file is placed in the Public Domain.


"the object programming version"


from . import objects


from .objects import *


def __dir__():
    return (
            'Object',
            'format',
            'items',
            'keys',
            'kind',
            'name',
            'oid',
            'search',
            'update',
            'values'
           )


__all__ = __dir__()
