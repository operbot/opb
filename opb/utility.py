# This file is placed in the Public Domain.


"utility"


import os
import pathlib
import time


from functools import wraps


def __dir__():
    return (
            'cdir',
            'elapsed',
            'fnclass',
            'fntime',
            'locked',
            'spl',
            'wait'
           )


def cdir(path):
    pth = pathlib.Path(path)
    if path.split(os.sep)[-1].count(":") == 2:
        pth = pth.parent
    os.makedirs(pth, exist_ok=True)


def elapsed(seconds, short=True):
    txt = ""
    nsec = float(seconds)
    if nsec < 1:
        return f"{nsec:.4f}s"
    year = 365*24*60*60
    week = 7*24*60*60
    nday = 24*60*60
    hour = 60*60
    minute = 60
    years = int(nsec/year)
    nsec -= years*year
    weeks = int(nsec/week)
    nsec -= weeks*week
    nrdays = int(nsec/nday)
    nsec -= nrdays*nday
    hours = int(nsec/hour)
    nsec -= hours*hour
    minutes = int(nsec/minute)
    nsec -= int(minute*minutes)
    sec = int(nsec)
    if years:
        txt += "%sy" % years
    if weeks:
        nrdays += weeks * 7
    if nrdays:
        txt += "%sd" % nrdays
    if years and short and txt:
        return txt.strip()
    if hours:
        txt += "%sh" % hours
    if minutes:
        txt += "%sm" % minutes
    if sec:
        txt += "%ss" % sec
    else:
        txt += "0s"
    txt = txt.strip()
    return txt


def fnclass(path):
    try:
        _rest, *pth = path.split("store")
        splitted = pth[0].split(os.sep)
        return splitted[1]
    except ValueError:
        pass
    return None


def fntime(daystr):
    daystr = daystr.replace("_", ":")
    datestr = " ".join(daystr.split(os.sep)[-2:])
    if "." in datestr:
        datestr, rest = datestr.rsplit(".", 1)
    else:
        rest = ""
    tme = time.mktime(time.strptime(datestr, "%Y-%m-%d %H:%M:%S"))
    if rest:
        tme += float("." + rest)
    else:
        tme = 0
    return tme


def locked(lock):

    def lockeddec(func, *args, **kwargs):

        if args or kwargs:
            locked.noargs = True

        @wraps(func)
        def lockedfunc(*args, **kwargs):
            lock.acquire()
            res = None
            try:
                res = func(*args, **kwargs)
            finally:
                lock.release()
            return res

        lockeddec.__wrapped__ = func
        lockeddec.__doc__ = func.__doc__
        return lockedfunc

    return lockeddec


def spl(txt):
    try:
        res = txt.split(",")
    except (TypeError, ValueError):
        res = txt
    return [x for x in res if x]


def wait():
    while 1:
        time.sleep(1.0)
