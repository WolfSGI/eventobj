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
