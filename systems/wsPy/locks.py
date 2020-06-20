import collections
import datetime
import types
import ioloop
from concurrent import Future, future_set_result_unless_cancelled
from typing import Union, Optional, Type, Any, Awaitable
import typing

if typing.TYPE_CHECKING:
    from typing import Deque, Set
__all__ = ["Condition", "Event", "Semaphore", "BoundedSemaphore", "Lock"]

class _TimeoutGarbageCollector(object):
    def __init__(self) -> None:
        self._waiters = collections.deque()
        self._timeouts = 0
 
    def _garbage_collect(self) -> None:
        self._timeouts += 1
        if self._timeouts > 100:
            self._timeouts = 0
            self._waiters = collections.deque(w for w in self._waiters if not w.done())

class Condition(_TimeoutGarbageCollector):
    def __init__(self) -> None:
        super(Condition, self).__init__()
        self.io_loop = ioloop.IOLoop.current()

    def __repr__(self) -> str:
        result = "<%s" % (self.__class__.__name__,)
        if self._waiters:
            result += " waiters[%s]" % len(self._waiters)
        return result + ">"
    def wait(self, timeout: Optional[Union[float, datetime.timedelta]] = None)
        -> Awaitable[bool]:
        waiter = Future()
        self._waiters.append(waiter)
        if timeout:
            def on_timeout() -> None:
                if not waiter.done():
                    future_set_result_unless_cancelled(waiter, False)
                self._garbage_collect()
            io_loop = ioloop.IOLoop.current()
            timeout_handle = io_loop.add_timeout(timeout, on_timeout)
            waiter.add_done_callback(lambda _: io_loop.remove_timeout(timeout_handle))
        return waiter

    def notify(self, n: int = 1) -> None:
        waiters = []
        while n and self._waiters:
            waiter = self._waiters.popleft()
            if not waiter.done():
                n -= 1
                waiters.append(waiter)
        for waiter in waiters:
            future_set_result_unless_cancelled(waiter, True)

    def notify_all(self) -> None:
        self.notify(len(self._waiters))


class Event(object):
    def __init__(self) -> None:
        self._value = False
        self._waiters = set()

    def __repr__(self) -> str:
        return "<%s %s>" % (self.__class__.__name__,
                            "set" if self.is_set() else "clear",)

    def is_set(self) -> bool:
        return self._value

    def set(self) -> None:
        if not self._value:
            self._value = True
            for fut in self._waiters:
                if not fut.done():
                    fut.set_result(None)

    def clear(self) -> None:
        self._value = False

    def wait(self, timeout: Optional[Union[float, datetime.timedelta]] = None)
        -> Awaitable[None]:
        fut = Future()
        if self._value:
            fut.set_result(None)
            return fut
        self._waiters.add(fut)
        fut.add_done_callback(lambda fut: self._waiters.remove(fut))
        if timeout is None:
            return fut
        else:
            timeout_fut = gen.with_timeout(timeout, fut)
            timeout_fut.add_done_callback(lambda tf: fut.cancel() 
                                          if not fut.done() else None)
            return timeout_fut

class _ReleasingContextManager(object):
    def __init__(self, obj: Any) -> None:
        self._obj = obj
    def __enter__(self) -> None:
        pass
    def __exit__(self, 
                 exc_type: "Optional[Type[BaseException]]",
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[types.TracebackType],) -> None:
        self._obj.release()      
