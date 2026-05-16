import pytest
from unittest.mock import Mock, call
from eventobj import Event, ObjectEvent, Events


def test_basic_usecase():
    events = Events()
    mock = Mock()
    assert len(events) == 0

    @events.register(Event)
    def very_simple_handler(event):
        mock.touch(event)

    assert len(events) == 1

    event = Event()
    events.notify(event)
    mock.touch.assert_called_with(event)


def test_basic_usecase_naming_conflict():
    events = Events()
    mock = Mock()
    assert len(events) == 0

    @events.register(Event, name="test")
    def very_simple_handler(event):
        mock.touch(event)

    with pytest.raises(AssertionError):
        @events.register(Event, name="test")
        def other_simple_handler(event):
            mock.touch(event)


def test_sorted_events():

    events = Events()
    mock = Mock()

    @events.register(Event, order=3)
    def handler1(event):
        mock.touch('handler1')


    @events.register(Event, order=1)
    def handler2(event):
        mock.touch('handler2')


    @events.register(Event, order=2)
    def handler3(event):
        mock.touch('handler3')


    assert len(events) == 3
    event = Event()
    events.notify(event)

    mock.touch.assert_has_calls(
        (call("handler2"), call("handler3"), call("handler1"))
    )


def test_basic_inheritence():
    events = Events()
    mock = Mock()


    class SomeEvent(Event):
        ...


    @events.register(Event)
    def very_simple_handler(event):
        mock.touch(event)


    event = SomeEvent()
    events.notify(event)

    mock.touch.assert_called_with(event)


def test_object_event():

    events = Events()
    mock = Mock()


    @events.register(ObjectEvent, object)
    def handler_for_all(event):
        mock.touch(f'generic {event.obj}')


    @events.register(ObjectEvent, str)
    def handler2_for_str(event):
        mock.touch(f'str {event.obj}')


    @events.register(ObjectEvent, int)
    def handler3_for_int(event):
        mock.touch(f'int {event.obj}')


    event = ObjectEvent("42")
    events.notify(event)

    mock.touch.assert_has_calls(
        (call("generic 42"), call("str 42")), any_order=True
    )
    mock.reset()

    event = ObjectEvent(42)
    events.notify(event)

    mock.touch.assert_has_calls((call("int 42"),))


def test_event_typing():

    events = Events()
    mock = Mock()


    class SomeEvent(ObjectEvent):

        def __init__(self, obj: str):
            """Works only for str.
            """
            self.obj = obj


    @events.register(SomeEvent, str)
    def handler2_for_str(event):
        mock.touch(f'str {event.obj}')


    with pytest.raises(ValueError):
        @events.register(SomeEvent, int)
        def handler3_for_int(event):
            mock.touch(f'int {event.obj}')


def test_events_merging():

    events1 = Events()
    events2 = Events()

    @events1.register(ObjectEvent, str)
    def handler_for_str(event):
        mock.touch(f'str {event.obj}')


    @events1.register(ObjectEvent, int)
    def handler_for_int(event):
        mock.touch(f'int {event.obj}')


    @events2.register(ObjectEvent, str)
    def other_handler_for_str(event):
        mock.touch(f'other str {event.obj}')


    @events2.register(ObjectEvent, int)
    def other_handler_for_int(event):
        mock.touch(f'other int {event.obj}')


    assert len(events1) == 2
    assert len(events2) == 2

    events = events1 | events2
    assert len(events) == 4

    mock = Mock()
    event = ObjectEvent("42")
    events.notify(event)
    mock.touch.assert_has_calls(
        (call("str 42"), call("other str 42")), any_order=True
    )

    mock.reset()
    event = ObjectEvent(42)
    events.notify(event)
    mock.touch.assert_has_calls(
        (call("int 42"), call("other int 42")), any_order=True
    )


def test_events_merging_naming_squash():

    events1 = Events()
    events2 = Events()

    @events1.register(ObjectEvent, str, name="test")
    def handler_for_str(event):
        mock.touch(f'str {event.obj}')


    @events2.register(ObjectEvent, str, name="test")
    def other_handler_for_str(event):
        mock.touch(f'other str {event.obj}')


    events = events1 | events2
    mock = Mock()
    event = ObjectEvent("42")
    events.notify(event)
    mock.touch.assert_has_calls(
        (call("other str 42"),), any_order=True
    )


def test_complex_event_dispatch():

    mock = Mock()

    class MyEvent(Event):

        def __init__(self, val1: str, val2: int, val3):
            self.val1 = val1
            self.val2 = val2
            self.val3 = val3

        def __dispatch__(self):
            return (self.val1, self.val2, self.val3)


    events = Events()
    @events.register(MyEvent, str, int, bool)
    def handler_for_str_int_bool(event):
        mock.touch(f'got {event.val1, event.val2, event.val3}')


    @events.register(MyEvent, str, int, str)
    def handler_for_other(event):
        mock.touch(f'other got {event.val1, event.val2, event.val3}')


    event = MyEvent("abc", 42, False)
    events.notify(event)
    mock.touch.assert_has_calls(
        (call("got ('abc', 42, False)"),), any_order=True
    )
