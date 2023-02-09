README
######


**NAME**


``OPB`` - object programming bot.


**SYNOPSIS**

::

 opb [<cmd>|-c|-d] [key=value] [key==value]


**DESCRIPTION**

``OPB`` is a bot, intended to be programmable, with a client program to
develop modules on and a systemd version with code included to run a 24/7
presence in a channel. 


``OPB`` stores it's data on disk where objects are time versioned and the
last version saved on disk is served to the user layer. Files are JSON dumps
that are read-only so thus should provide (disk) persistence. Paths carry the
type in the path name what makes reconstruction from filename easier then
reading type from the object.


``OPB`` has some functionality, mostly feeding RSS feeds into a irc
channel. It can do some logging of txt and take note of things todo.


**INSTALL**

::

 $ sudo pip3 install opb


**CONFIGURATION**


configuration is done by calling the ``cfg`` command of ``opb``


IRC

::

 $ opb cfg server=<server> channel=<channel> nick=<nick>

 (*) default channel/server is #opb on localhost


SASL

::

 $ opb pwd <nickservnick> <nickservpass>
 $ opb cfg password=<outputfrompwd>


USERS

as default the user's userhost is not checked when a user types a command in a
channel. To enable userhost checking enable users with the ``cfg`` command::

 $ opb cfg users=True


To add a user to the bot use the met command::

 $ opb met <userhost>

to delete a user use the del command with a substring of the userhost::

 $ opb del <substring>


RSS

::

 $ opb rss <url>



**RUNNING**


this part shows how to run ``opb``.


**cli**


without any arguments ``opb`` doesn't respond, add arguments to have
``opb`` execute a command::


 $ opb
 $


the ``cmd`` command shows you a list of available commands::


 $ opb cmd
 cfg,cmd,dlt,dpl,flt,fnd,ftc,met,krn,mre,nme,pwd,rem,rss,thr,upt


**console**


use the -c option to start the bot as a console::

 $ opb -c 
 OPB started at Fri Jan 6 01:49:58 2023
 > cmd
 cmd,dlt,dpl,flt,ftc,krn,log,met,mre,nme,pwd,rem,rss,thr,upt
 >


running the bot in the background is done with the -d option::

 $ opb -d
 $


**COMMANDS**


here is a short description of the commands::

 cfg - show the irc configuration, also edits the config
 cmd - show all commands
 dlt - remove a user
 dne - flag todo as done
 dpl - set display items for a rss feed
 flt - show a list of bot registered to the bus
 fnd - allow you to display objects on the datastore, read-only json files on disk 
 ftc - run a rss feed fetching batch
 krn - kernel
 log - log some text
 met - add a users with there irc userhost
 mre - displays cached output, channel wise.
 nme - set name of a rss feed
 pwd - combine a nickserv name/password into a sasl password
 rem - remove a rss feed by matching is to its url
 rss - add a feed to fetch, fetcher runs every 5 minutes
 thr - show the running threads
 tdo - adds a todo item, no options returns list of todo's
 upt - show uptime
 ver - show version


**PROGRAMMING**


The ``opb`` package provides an Object class, that mimics a dict while using
attribute access and provides a save/load to/from json files on disk.
Objects can be searched with database functions and uses read-only files
to improve persistence and a type in filename for reconstruction. Methods are
factored out into functions to have a clean namespace to read JSON data into.

basic usage is this::

 >>> from opb import Object
 >>> o = Object()
 >>> o.key = "value"
 >>> o.key
 >>> 'value'

Objects try to mimic a dictionary while trying to be an object with normal
attribute access as well. hidden methods are provided, the methods are
factored out into functions like get, items, keys, register, set, update
and values.

load/save from/to disk::

 >>> from opb import Object, load, save
 >>> o = Object()
 >>> o.key = "value"
 >>> p = save(o)
 >>> obj = Object()
 >>> load(obj, p)
 >>> obj.key
 >>> 'value'

great for giving objects peristence by having their state stored in files::

 >>> from opb import Object, save
 >>> o = Object()
 >>> save(o)
 opb.objects.Object/89efa5fd7ad9497b96fdcb5f01477320/2022-11-21/17:20:12.221192


**SYSTEMD**


to run the bot after reboot, install the service file and start the service
by enabling it with ``--now``::


 $ sudo cp /usr/local/opb/opb.service /etc/systemd/system
 $ sudo systemctl enable opb  --now

 (*) default channel/server is #opb on localhost


use ``opbctl`` instead of the use ``opb`` program::


 $ sudo opbctl cfg server=<server> channel=<channel> nick=<nick>``
 $ sudo opbctl pwd <nickservnick> <nickservpass>``
 $ sudo opbctl cfg password=<outputfrompwd>``
 $ sudo opbctl cfg users=True``
 $ sudo opbctl met <userhost>``
 $ sudo opbctl rss <url>``


**AUTHOR**


B.H.J. Thate - operbot100@gmail.com


**COPYRIGHT**


``OPB`` is placed in the Public Domain.
