# This file is placed in the Public Domain.


import unittest


from opb.decoder import loads
from opb.encoder import dumps
from opb.objects import Object


class TestDecoder(unittest.TestCase):

    def test_loads(self):
        obj = Object()
        obj.test = "bla"
        oobj = loads(dumps(obj))
        self.assertEqual(oobj.test, "bla")

