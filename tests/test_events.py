from unittest.mock import Mock, call
from eventobj import Event, ObjectEvent, Events


def test_basic_usecase():
    events = Events()
    mock = Mock()


    @events.register(Event)
    def very_simple_handler(event):
        mock.touch(event)


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
