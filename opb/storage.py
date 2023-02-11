# This file is placed in the Public Domain.


import os


from .objects import Object, items, kind, oid, search, update
from .utility import fnclass, fntime


def __dir__():
    return (
            'Storage',
            'last',
            'save'
           )


__all__ = __dir__()


class NoClass(Exception):

    pass


class Storage:

    cls = Object()
    workdir = ""

    @staticmethod
    def add(clz):
        setattr(Storage.cls, "%s.%s" % (clz.__module__, clz.__name__), clz)

    @staticmethod
    def files(oname=None):
        res = []
        path = Storage.path("")
        print(path)
        if not os.path.exists(path):
            return res
        for fnm in os.listdir(path):
            if oname and oname.lower() not in fnm.split(".")[-1].lower():
                continue
            if fnm not in res:
                res.append(fnm)
        print(res)
        return res

    @staticmethod
    def find(otp, selector=None):
        if selector is None:
            selector = {}
        for typ in Storage.types(otp):
            for fnm in Storage.fns(typ):
                obj = Storage.hook(fnm)
                if "__deleted__" in obj and obj.__deleted__:
                    continue
                if selector and not search(obj, selector):
                    continue
                yield fnm, obj

    @staticmethod
    def fns(otp):
        assert Storage.workdir
        path = Storage.path(otp)
        dname = ""
        for rootdir, dirs, _files in os.walk(path, topdown=False):
            if dirs:
                dname = sorted(dirs)[-1]
                if dname.count("-") == 2:
                    ddd = os.path.join(rootdir, dname)
                    fls = sorted(os.listdir(ddd))
                    if fls:
                        path2 = os.path.join(ddd, fls[-1])
                        yield path2

    @staticmethod
    def hook(otp):
        fqn = fnclass(otp)
        cls = getattr(Storage.cls, fqn, None)
        if not cls:
            raise NoClass(fqn)
        obj = cls()
        load(obj, otp)
        return obj

    @staticmethod
    def path(path=""):
        return os.path.join(Storage.workdir, "store", path)

    @staticmethod
    def types(oname=None):
        for name, _typ in items(Storage.cls):
            if oname and oname in name.split(".")[-1].lower():
                print(name)
                yield name

    @staticmethod
    def strip(path):
        return path.split("store")[-1][1:]


Storage.add(Object)


@locked
def dump(obj, opath):
    cdir(opath)
    with open(opath, "w", encoding="utf-8") as ofile:
        json.dump(
            obj.__dict__, ofile, cls=ObjectEncoder, indent=4, sort_keys=True
        )
    return opath


def last(obj, selector=None):
    if selector is None:
        selector = {}
    result = sorted(Storage.find(kind(obj), selector), key=lambda x: fntime(x[0]))
    if result:
        _fn, ooo = result[-1]
        if ooo:
            update(obj, ooo)

@locked(disklock)
def load(obj, opath):
    with open(opath, "r", encoding="utf-8") as ofile:
        res = json.load(ofile, cls=ObjectDecoder)
        update(obj, res)
    return opath


def save(obj):
    opath = Storage.path(oid(obj))
    dump(obj, opath)
    return Storage.strip(opath)
