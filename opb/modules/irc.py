# This file is placed in the Public Domain.


"internet relay chat"


import base64
import os
import queue
import random
import socket
import ssl
import time
import textwrap
import threading
import _thread


from ..clients import Client
from ..command import Command
from ..default import Default
from ..objects import Object, keys, tostr, update
from ..message import Message
from ..utility import elapsed, fntime, locked
from ..threads import launch
from ..storage import Storage


def __dir__():
    return (
            'Config',
            'IRC',
            "NoUser",
            "Users",
            "User",
            'init',
            'dlt',
            'cfg',
            'met',
            'mre',
            'pwd'
           )


saylock = _thread.allocate_lock()


def init():
    irc = IRC()
    irc.start()
    return irc


class NoUser(Exception):

    pass


class Config(Default):

    channel = "#opb"
    control = "!"
    nick = "opb"
    password = ""
    port = 6667
    realname = "object programming bot"
    sasl = False
    server = "localhost"
    servermodes = ""
    sleep = 60
    username = "opb"
    users = False

    def __init__(self):
        Default.__init__(self)
        self.control = Config.control
        self.channel = Config.channel
        self.nick = Config.nick
        self.password = Config.password
        self.port = Config.port
        self.realname = Config.realname
        self.sasl = Config.sasl
        self.server = Config.server
        self.servermodes = Config.servermodes
        self.sleep = Config.sleep
        self.username = Config.username
        self.users = Config.users


Storage.add(Config)


class TextWrap(textwrap.TextWrapper):

    def __init__(self):
        super().__init__()
        self.break_long_words = False
        self.drop_whitespace = True
        self.fix_sentence_endings = True
        self.replace_whitespace = True
        self.tabsize = 4
        self.width = 450


class Output(Object):

    cache = Object()

    def __init__(self):
        Object.__init__(self)
        self.oqueue = queue.Queue()
        self.dostop = threading.Event()

    def dosay(self, channel, txt):
        raise NotImplementedError

    def extend(self, channel, txtlist):
        if channel not in self.cache:
            setattr(self.cache, channel, [])
        cache = getattr(self.cache, channel, None)
        cache.extend(txtlist)

    def gettxt(self, channel):
        txt = None
        try:
            cache = getattr(self.cache, channel, None)
            txt = cache.pop(0)
        except (KeyError, IndexError):
            pass
        return txt

    def oput(self, channel, txt):
        if channel not in self.cache:
            setattr(self.cache, channel, [])
        self.oqueue.put_nowait((channel, txt))

    def output(self):
        while not self.dostop.is_set():
            (channel, txt) = self.oqueue.get()
            if channel is None and txt is None:
                break
            if self.dostop.is_set():
                break
            wrapper = TextWrap()
            try:
                txtlist = wrapper.wrap(txt)
            except AttributeError:
                continue
            if len(txtlist) > 3:
                self.extend(channel, txtlist)
                self.dosay(channel, "%s put in cache, use !mre to show more" % len(txtlist))
                continue
            _nr = -1
            for txt in txtlist:
                _nr += 1
                self.dosay(channel, txt)

    def size(self, chan):
        if chan in self.cache:
            return len(getattr(self.cache, chan, []))
        return 0

    def start(self):
        self.dostop.clear()
        launch(self.output)
        return self

    def stop(self):
        self.dostop.set()
        self.oqueue.put_nowait((None, None))


class IRC(Client, Output):

    def __init__(self):
        Client.__init__(self)
        Output.__init__(self)
        self.buffer = []
        self.cfg = Config()
        self.connected = threading.Event()
        self.channels = []
        self.joined = threading.Event()
        self.keeprunning = False
        self.outqueue = queue.Queue()
        self.sock = None
        self.speed = "slow"
        self.state = Object()
        self.state.needconnect = False
        self.state.errors = []
        self.state.last = 0
        self.state.lastline = ""
        self.state.nrconnect = 0
        self.state.nrerror = 0
        self.state.nrsend = 0
        self.state.pongcheck = False
        self.threaded = False
        self.zelf = ""
        self.register("903", self.h903)
        self.register("904", self.h903)
        self.register("AUTHENTICATE", self.auth)
        self.register("CAP", self.cap)
        self.register("ERROR", self.error)
        self.register("LOG", self.log)
        self.register("NOTICE", self.notice)
        self.register("PRIVMSG", self.privmsg)
        self.register("QUIT", self.quit)
        self.register("command", self.dispatch)
        self.target = "type"

    def announce(self, txt):
        for channel in self.channels:
            self.say(channel, txt)

    def auth(self, event):
        time.sleep(1.0)
        self.direct("AUTHENTICATE %s" % self.cfg.password)

    def cap(self, event):
        time.sleep(1.0)
        if self.cfg.password and "ACK" in event.arguments:
            self.direct("AUTHENTICATE PLAIN")
        else:
            self.direct("CAP REQ :sasl")

    @locked(saylock)
    def command(self, cmd, *args):
        if not args:
            self.raw(cmd)
        elif len(args) == 1:
            self.raw("%s %s" % (cmd.upper(), args[0]))
        elif len(args) == 2:
            self.raw("%s %s :%s" % (cmd.upper(), args[0], " ".join(args[1:])))
        elif len(args) >= 3:
            self.raw(
                "%s %s %s :%s" % (cmd.upper(),
                                  args[0],
                                  args[1],
                                  " ".join(args[2:]))
            )
        if (time.time() - self.state.last) < 5.0:
            time.sleep(5.0)
        self.state.last = time.time()

    def connect(self, server, port=6667):
        self.state.nrconnect += 1
        self.connected.clear()
        if self.cfg.password:
            self.cfg.sasl = True
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
            ctx.check_hostname = False
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock = ctx.wrap_socket(sock)
            self.sock.connect((server, port))
            self.command("CAP LS 302")
        else:
            addr = socket.getaddrinfo(server, port, socket.AF_INET)[-1][-1]
            self.sock = socket.create_connection(addr)
        if self.sock:
            os.set_inheritable(self.fileno(), os.O_RDWR)
            self.sock.setblocking(True)
            self.sock.settimeout(180.0)
            self.connected.set()
            return True
        return False

    def direct(self, txt):
        self.sock.send(bytes(txt+"\n", "utf-8"))

    def disconnect(self):
        self.sock.shutdown(2)

    def dispatch(self, evt):
        evt.orig = repr(self)
        Command.handle(evt)

    def doconnect(self, server, nck, port=6667):
        while 1:
            try:
                if self.connect(server, port):
                    break
            except (OSError, ConnectionResetError) as ex:
                self.state.errors.append(str(ex))
            time.sleep(self.cfg.sleep)
        self.logon(server, nck)

    def dosay(self, channel, txt):
        self.joined.wait()
        txt = str(txt).replace("\n", "")
        txt = txt.replace("  ", " ")
        self.command("PRIVMSG", channel, txt)

    def error(self, event):
        self.state.nrerror += 1
        self.state.errors.append(event.txt)
        self.stop()

    def event(self, txt):
        evt = self.parsing(txt)
        cmd = evt.command
        if cmd == "PING":
            self.state.pongcheck = True
            self.command("PONG", evt.txt or "")
        elif cmd == "PONG":
            self.state.pongcheck = False
        if cmd == "001":
            self.state.needconnect = False
            if self.cfg.servermodes:
                self.command("MODE %s %s" % (self.cfg.nick, self.cfg.servermodes))
            self.zelf = evt.args[-1]
            self.joinall()
        elif cmd == "002":
            self.state.host = evt.args[2][:-1]
        elif cmd == "366":
            self.state.errors = []
            self.joined.set()
        elif cmd == "433":
            self.state.errors.append(txt)
            nck = self.cfg.nick + "_" + str(random.randint(1,10))
            self.command("NICK", nck)
        return evt

    def fileno(self):
        return self.sock.fileno()

    def h903(self, event):
        time.sleep(1.0)
        self.command("CAP END")

    def h904(self, event):
        time.sleep(1.0)
        self.command("CAP END")

    def joinall(self):
        for channel in self.channels:
            self.command("JOIN", channel)

    def keep(self):
        while 1:
            self.connected.wait()
            self.keeprunning = True
            time.sleep(self.cfg.sleep)
            self.state.pongcheck = True
            self.command("PING", self.cfg.server)
            time.sleep(10.0)
            if self.state.pongcheck:
                self.keeprunning = False
                self.stopped.set()
                self.loop()

    def logon(self, server, nck):
        assert server
        assert nck
        assert self.cfg.username
        assert self.cfg.realname
        self.direct("NICK %s" % nck)
        self.direct(
                 "USER %s %s %s :%s" % (self.cfg.username,
                 server,
                 server,
                 self.cfg.realname)
                )

    def kill(self, event):
        pass

    def log(self, event):
        pass

    def notice(self, event):
        if event.txt.startswith("VERSION"):
            txt = "\001VERSION %s %s - %s\001" % (
                "op",
                self.cfg.version,
                self.cfg.username,
            )
            self.command("NOTICE", event.channel, txt)

    def parsing(self, txt):
        rawstr = str(txt)
        rawstr = rawstr.replace("\u0001", "")
        rawstr = rawstr.replace("\001", "")
        obj = Message()
        obj.rawstr = rawstr
        obj.command = ""
        obj.arguments = []
        arguments = rawstr.split()
        if arguments:
            obj.origin = arguments[0]
        else:
            obj.origin = self.cfg.server
        if obj.origin.startswith(":"):
            obj.origin = obj.origin[1:]
            if len(arguments) > 1:
                obj.command = arguments[1]
                obj.type = obj.command
            if len(arguments) > 2:
                txtlist = []
                adding = False
                for arg in arguments[2:]:
                    if arg.count(":") <= 1 and arg.startswith(":"):
                        adding = True
                        txtlist.append(arg[1:])
                        continue
                    if adding:
                        txtlist.append(arg)
                    else:
                        obj.arguments.append(arg)
                obj.txt = " ".join(txtlist)
        else:
            obj.command = obj.origin
            obj.origin = self.cfg.server
        try:
            obj.nick, obj.origin = obj.origin.split("!")
        except ValueError:
            obj.nick = ""
        target = ""
        if obj.arguments:
            target = obj.arguments[0]
        if target.startswith("#"):
            obj.channel = target
        else:
            obj.channel = obj.nick
        if not obj.txt:
            obj.txt = rawstr.split(":", 2)[-1]
        if not obj.txt and len(arguments) == 1:
            obj.txt = arguments[1]
        spl = obj.txt.split()
        if len(spl) > 1:
            obj.args = spl[1:]
        obj.orig = repr(self)
        obj.txt = obj.txt.strip()
        obj.type = obj.command 
        return obj

    def poll(self):
        self.connected.wait()
        if not self.buffer:
            try:
                self.some()
            except (socket.timeout, ConnectionResetError) as ex:
                self.joined.clear()
                time.sleep(5.0)
                evt = Message()
                evt.txt = str(ex)
                evt.orig = repr(self)
                return evt
        return self.event(self.buffer.pop(0))

    def privmsg(self, event):
        if event.txt:
            if event.txt[0] in [self.cfg.control, "!"]:
                event.txt = event.txt[1:]
            elif event.txt.startswith("%s:" % self.cfg.nick):
                event.txt = event.txt[len(self.cfg.nick)+1:]
            else:
                return
            if self.cfg.users and not Users.allowed(event.origin, "USER"):
                return
            msg = Message(event)
            msg.type = "command"
            msg.parse(event.txt)
            self.dispatch(msg)

    def quit(self, event):
        if event.orig and event.orig in self.zelf:
            self.reconnect()

    def raw(self, txt):
        txt = txt.rstrip()
        if not txt.endswith("\r\n"):
            txt += "\r\n"
        txt = txt[:512]
        txt += "\n"
        txt = bytes(txt, "utf-8")
        if self.sock:
            try:
                self.sock.send(txt)
            except (ConnectionResetError, BrokenPipeError) as ex:
                time.sleep(5.0)
                self.errors.append(ex)
                self.stop()
        self.state.last = time.time()
        self.state.nrsend += 1

    def reconnect(self):
        try:
            self.disconnect()
        except OSError:
            pass
        self.connected.clear()
        self.joined.clear()
        self.doconnect(self.cfg.server, self.cfg.nick, int(self.cfg.port))

    def say(self, channel, txt):
        self.oput(channel, txt)

    def some(self):
        self.connected.wait()
        if not self.sock:
            return
        inbytes = self.sock.recv(512)
        txt = str(inbytes, "utf-8")
        if txt == "":
            raise ConnectionResetError
        self.state.lastline += txt
        splitted = self.state.lastline.split("\r\n")
        for line in splitted[:-1]:
            self.buffer.append(line)
        self.state.lastline = splitted[-1]

    def start(self):
        assert self.cfg.nick
        assert self.cfg.server
        Storage.last(self.cfg)
        if self.cfg.channel not in self.channels:
            self.channels.append(self.cfg.channel)
        self.connected.clear()
        self.joined.clear()
        launch(Client.start, self)
        launch(Output.start, self)
        launch(
               self.doconnect,
               self.cfg.server,
               self.cfg.nick,
               int(self.cfg.port or "6667")
              )
        if not self.keeprunning:
            launch(self.keep)

    def stop(self):
        try:
            self.sock.shutdown(2)
        except OSError:
            pass
        Client.stop(self)


class Users(Object):

    @staticmethod
    def allowed(origin, perm):
        perm = perm.upper()
        user = Users.get_user(origin)
        val = False
        if user and perm in user.perms:
            val = True
        return val

    @staticmethod
    def delete(origin, perm):
        res = False
        for user in Users.get_users(origin):
            try:
                user.perms.remove(perm)
                Storage.save(user)
                res = True
            except ValueError:
                pass
        return res

    @staticmethod
    def get_users(origin=""):
        selector = {"user": origin}
        return Storage.find("user", selector)

    @staticmethod
    def get_user(origin):
        users = list(Users.get_users(origin))
        res = None
        if len(users) > 0:
            res = users[-1]
        return res

    @staticmethod
    def perm(origin, permission):
        user = Users.get_user(origin)
        if not user:
            raise NoUser(origin)
        if permission.upper() not in user.perms:
            user.perms.append(permission.upper())
            Storage.save(user)
        return user


class User(Object):

    def __init__(self, val=None):
        Object.__init__(self)
        self.user = ""
        self.perms = []
        if val:
            update(self, val)


def cfg(event):
    config = Config()
    Storage.last(config)
    if not event.sets:
        event.reply(tostr(
                          config,
                          keys(config),
                          skip="control,password,realname,sleep,username")
                         )
    else:
        update(config, event.sets)
        Storage.save(config)
        event.reply("ok")


def dlt(event):
    if not event.args:
        event.reply("dlt <username>")
        return
    selector = {"user": event.args[0]}
    for obj in Storage.find("user", selector):
        obj.__deleted__ = True
        Storage.save(obj)
        event.reply("ok")
        break


def met(event):
    if not event.args:
        nmr = 0
        for obj in Storage.find("user"):
            event.reply("%s %s %s %s" % (
                                         nmr,
                                         obj.user,
                                         obj.perms,
                                         elapsed(time.time() - fntime(obj.__fnm__)))
                                        )
            nmr += 1
        if not nmr:
            event.reply("no users introduced yet")
        return
    user = User()
    user.user = event.rest
    user.perms = ["USER"]
    Storage.save(user)
    event.reply("ok")


def mre(event):
    if not event.channel:
        event.reply("channel is not set.")
        return
    bot = event.bot()
    if "cache" not in dir(bot):
        event.reply("bot is missing cache")
        return
    if event.channel not in bot.cache:
        event.reply("no output in %s cache." % event.channel)
        return
    for _x in range(3):
        txt = bot.gettxt(event.channel)
        if txt:
            bot.say(event.channel, txt)
    size = bot.size(event.channel)
    event.reply("%s more in cache" % size)


def pwd(event):
    if len(event.args) != 2:
        event.reply("pwd <nick> <password>")
        return
    txt = "\x00%s\x00%s" % (event.args[0], event.args[1])
    enc = txt.encode("ascii")
    base = base64.b64encode(enc)
    dcd = base.decode("ascii")
    event.reply(dcd)
