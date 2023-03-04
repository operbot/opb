# This file is placed in the Public Domain.


import json
import os
import unittest


from opb.objects import Object
from opb.storage import Storage


import opb.storage


Storage.workdir = ".test"


ATTRS1 = (
          'Storage',
         )


ATTRS2 = (
          '__class__',
          '__delattr__',
          '__dict__',
          '__dir__',
          '__doc__',
          '__eq__',
          '__format__',
          '__ge__',
          '__getattribute__',
          '__gt__',
          '__hash__',
          '__init__',
          '__init_subclass__',
          '__le__',
          '__lt__',
          '__module__',
          '__ne__',
          '__new__',
          '__reduce__',
          '__reduce_ex__',
          '__repr__',
          '__setattr__',
          '__sizeof__',
          '__str__',
          '__subclasshook__',
          '__weakref__',
          'add',
          'cls',
          'files',
          'find',
          'fns',
          'hook',
          'last',
          'path',
          'save',
          'strip',
          'types',
          'workdir'
         )


class TestStorage(unittest.TestCase):

    def test_constructor(self):
        obj = Storage()
        self.assertTrue(type(obj), Storage)

    def test__class(self):
        obj = Storage()
        clz = obj.__class__()
        self.assertTrue("Storage" in str(type(clz)))

    def test_dirmodule(self):
        self.assertEqual(
                         dir(opb.storage),
                         list(ATTRS1)
                        )

    def test_dirobject(self):
        db = Storage()
        self.assertEqual(
                         dir(db),
                         list(ATTRS2)
                        )

    def test_module(self):
        self.assertTrue(Storage().__module__, "opb.storage")

    def test_save(self):
        Storage.workdir = ".test"
        obj = Object()
        opath = Storage.save(obj)
        self.assertTrue(os.path.exists(opath))
