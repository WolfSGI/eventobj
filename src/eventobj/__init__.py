from uuid import uuid4
from typing import Any, Type
from signature_registries import Registry, Proxy
from plum import Signature


def event_sorter(result: tuple[Signature, Proxy]):
    return result[1].__metadata__.order


class Event:

    def __dispatch__(self):
        return ()


class ObjectEvent(Event):

    def __init__(self, obj: Any):
        self.obj = obj

    def __dispatch__(self):
        return (self.obj,)


class Events(Registry):

    def register(self, event_type: Type[Event], *args, name=None, **kwargs):
        event_signature = Signature.from_callable(event_type)
        handler_signature = Signature(*args)
        if not event_signature >= handler_signature:
            raise ValueError(
                'Arguments do not match required event signature')

        if name is None:
            name = str(uuid4())
        return super().register((event_type, *args), name=name, **kwargs)

    def notify(self, event):
        args = event.__dispatch__()
        for handler in self.lookup(event, *args, None, sorter=event_sorter):
            handler(event)
