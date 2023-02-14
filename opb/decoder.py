# This file is placed in the Public Domain.


"object decoder"


import json


from .objects import Object


def __dir__():
    return (
            'ObjectDecoder',
            'loads'
           )

 
class ObjectDecoder(json.JSONDecoder):


    def decode(self, s, _w=None):
        value = json.loads(s)
        return Object(value)



def loads(jsonstr):
    return json.loads(jsonstr, cls=ObjectDecoder)
