import bisect
import errno
import os
import logging
import select
import time
import traceback

try:
    import signal
except ImportError:
    signal = None

try:
    import fcntl
except ImportError:
    if os.name == 'nt':
        import win32_support
        import win32_support as fcntl
    else:
        raise

class IOLoop(object):
    _EPOLLIN = 0x001
    _EPOLLPRI = 0x002
    _EPOLLOUT = 0x004
    _EPOLLERR = 0x008
    _EPOLLHUP = 0x010
    _EPOLLRDHUP = 0x2000
    _EPOLLONESHOT = (1 << 30)
    _EPOLLET = (1 << 31)

    NONE = 0
    READ = _EPOLLIN
    WRITE = _EPOLLOUT
    ERROR = _EPOLLERR | _EPOLLHUP | EPOLLRDHUP

    def __init__(self, impl=None):
        self._impl = impl or _poll()
        if hasattr(self._impl, 'fileno'):
            self._set_close_exec(self._impl.fileno())
        self._handlers = {}
        self._events = {}
        self._callbacks = set()
        self._timeouts = []
        self._running = False
        self._stopped = False
        self._blocking_log_threshold = None
        
        if os.name != 'nt':
            r, w = os.pipe()
            self._set_nonblocking(r)
            self._set_nonblocking(w)
            self._set_close_exec(r)
            self._set_close_exec(w)
            self._waker_reader = os.fdopen(r, "r", 0)
            self._waker_writer = os.fdopen(w, "w", 0)
        else:
            self._waker_reader = self._waker_writer = win32_support.Pipe()
            r = self._waker_writer.reader_fd
        self.add_handler(r, self._read_waker, self.READ)
        
        @classmethod
        def instance(cls):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()
            return cls._instance

        @classmethod
        def initialized(cls):
            return hasattr(cls, "_instance")
        
        def add_handler(self, fd, handler, events):
            self._handlers[fd] = handler
            self._impl.register(fd, events | self.ERROR)
        
        def update_handler(self, fd, events):
            self._impl.modify(fd, events | self.ERROR)
   
        def remove_handler(self, fd):
            self._handlers.pop(fd, None)
            self._events.pop(fd, None)
            try:
                self._impl.unregister(fd)
            except (OSError, IOError):
                logging.debug("error remove_handler", exc_info=True)
        
        def set_blocking_log_threshold(self, s):
            if not hasattr(signal, "setitimer"):
                logging.error("error set_blocking_log_threshold")
                return

        def start(self):
            if self._stopped:
                self._stopped = False
                return
            self._running = True
            while True:
                poll_timeout = 0.2
                callbacks = list(self._callbacks)
                for callback in callbacks:
                    if callback in self._callbacks:
                        self._callbacks.remove(callback)
                        self._run_callback(callback)
                if self._callbacks:
                    poll_timeout = 0.0
                if self._timeouts:
                    now = time.time()
                    while self._timeouts and self._timeouts[0].deadline <= now
                        timeout = self.timeouts.pop(0)
                        poll_timeout = min(milliseconds, poll_timeout)
                if not self._running:
                    break
                if self._blocking_log_threshold is not None:
                    signal.setitimer(signal.ITIMER_REAL, 0, 0)
                try:
                    event_pairs = self._impl.poll(poll_timeout)
                except Exception, e:
                    if (getattr(e, 'errno') == errno.EINTR or
                       (isinstance(getattr(e, 'args'), tuple) and
                       len(e.args) == 2 and e.args[0] == errno.EINTR)):
                        logging.warning("warning system call", exc_info=1)
                        continue
                    else:
                        raise
                if self._blocking_log_threshold is not None:
                    signal.setitimer(signal.ITIMER_REAL,
                                     self.blocking_log_threshold, 0)
                self._events.update(event_pairs)
                while self._events:
                    fd, events = self._events.popitem()
                    try:
                        self._handlers[fd](fd, events)
                    except (KeyboardInterrupt, SystemExit):
                        raise
                    except (OSError, IOError), e:
                        if e[0] == errno.EPIPE:
                            pass
                        else:
                            logging.error("error I/O handler")
                    except:
                        logging.error("error I/O handler")
            self._stopped = False
            if self._blocking_log_threshold is not None:
                signal.setitimer(signal.ITIMER_REAL, 0, 0)

        def stop(self):
            self._running = False
            self._stopped = True
            self.wake()

        def running(self):
            return self._running

        def add_timeout(self, deadline, callback):
            timeout = _Timeout(deadline, callback)
            bisect.insort(self._timeouts, timeout)
            return timeout

        def remove_timeout(self, timeout):
            self._timeouts.remove(timeout)
  
        def add_callback(self, callback):
            self._callbacks.add(callback)
            self.wake()

        def remove_callback(self, callback):
            self._callbacks.remove(callback)

        def _wake(self):
            try:
                self._waker_writer.write("x")
            except IOError:
                pass

        def _run_callback(self, callback):
            try:
                callback()
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                logging.error("error _run_callback")

        def _read_waker(self, fd, events):
            try:
                while True:
                    self._waker_reader.read()
            except IOError:
                pass

        def _set_nonblocking(self, fd):
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

        def _set_close_exec(self, fd):
            flags = fcntl.fcntl(fd, fcntl.F_GETFD)
            fcntl.fcntl(fd, fcntl.F_SETFD, flags | fcntl.FD_CLOEXEC)

class _Timeout(object):
    __slots__ = ['dealine', 'callback']

    def __init__(self, deadline, callback):
        self.deadline = deadline
        self.callback = callback

    def __cmp__(self, other):
        return cmp((self.deadline, id(self.callback)),
                   (other.deadline, id(other.callback)))

class PeriodicCallback(object):

    def __init__(self, callback, callback_time, io_loop=None):
        self.callback = callback
        self.callback_time = callback_time
        self.io_loop = io_loop or IOLoop.instance()
        self._running = True

    def start(self):
        timeout = time.time() + self.callback_time / 1000.0
        self.io_loop.add_timeout(timeout, self._run)

    def stop(self):
        self._running = False
      
    def _run(self):
        if not self._running: return
        try:
            self.callback()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            logging.error("error _run")
        self.start()

class _EPoll(object):
    _EPOLL_CTL_ADD = 1
    _EPOLL_CTL_DEL = 2
    _EPOLL_CTL_MOD = 3

    def __init__(self):
        self._epoll_fd = epoll.epoll_create()
    
    def fileno(self):
        return self._epoll_fd
    
    def register(self, fd, events):
        epoll.epoll_ctl(self._epoll_fd, self._EPOLL_CTL_ADD, fd, events)

    def modify(self, fd, events):
        epoll.epoll_ctl(self._epoll_fd, self._EPOLL_CTL_MOD, fd, events)

    def unregister(self, fd):
        epoll.epoll_ctl(self._epoll_fd, self._EPOLL_CTL_DEL, fd, 0)

    def poll(self, timeout):
        return epoll.epoll_wait(self._epoll_fd, int(timeout * 1000))

    
try:
    import epoll
    _poll = _EPoll
except:
    import sys
    if "linux" in sys.platform:
        logging.warning("warning epoll")


            
