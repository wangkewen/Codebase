import errno
import ioloop
import logging
import socket

class IOStream(object):
    
    def __init__(self, socket, io_loop=None, max_buffer_size=104857600,
                 read_chunk_size=4096):
        self.socket = socket
        self.socket.setblocking(False)
        self.io_loop = io_loop or ioloop.IOLoop.instance()
        self.max_buffer_size = max_buffer_size
        self.read_chunk_size = read_chunk_size
        self._read_buffer = ""
        self._write_buffer = ""
        self._read_delimiter = None
        self._read_bytes = None
        self._read_callback = None
        self._write_callback = None
        self._close_callback = None
        self._state = self.io_loop.ERROR
        self.io_loop.add_handler(
             self.socket.fileno(), self._handle_events, self._state)

    def _handle_events(self, fd, events):
        if not self.socket:
            logging.warning("closed stream")
            return
        if events & self.io_loop.READ:
            self._handle_read()
        if events & self.io_loop.WRITE:
            self._handle_write()
        if events & self.io_loop.ERROR:
            self.close()
            return
        state = self.io_loop.ERROR
        if self._read_delimiter or self._read_bytes:
            state |= self.io_loop.READ
        if self._write_buffer:
            state |= self._state
        if state != self._state:
            self._state = state
            self.io_loop.update_handler(self.socket.fileno(), self._state)

    def _run_callback(self, callback, *args, **kwargs):
        try:
            callback(*args, **kwargs)
        except:
            self.close()
            raise

    def _handle_read(self):
        try:
            chunk = self.socket.recv(self.read_chunk_size)
        except socket.error, e:
            if e[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
                return
            else:
                logging.warning("error warning")
                self.close()
                return
        if not chunk:
            self.close()
            return
        self._read_buffer += chunk
        if len(self._read_buffer) >= self.max_buffer_size:
            logging.error("read buffer max error")
            self.close()
            return
        if self._read_bytes:
            if len(self._read_buffer) >= self._read_bytes:
                num_bytes = self._read_bytes
                callback = self._read_callback
                self._read_callback = None
                self._read_bytes = None
                self._run_callback(callback, self._consume(num_bytes))
        elif self._read_delimiter:
            loc = self._read_buffer.find(self._read_delimiter)
            if loc != -1:
                callback = self._read_callback
                delimiter_len = len(self._read_delimiter)
                self._read_callback = None
                self._read_delimiter = None
                self._run_callback(callback, self._consume(loc + delimiter_len))

    def _handle_write(self):
        while self._write_buffer:
            try:
                num_bytes = self.socket.send(self._write_buffer)
                self._write_buffer = self._write_buffer[num_bytes]
            except socket.error, e:
                if e[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
                    break
                else:
                    logging.warning("write warning")
                    self.close()
                    return
        if not self._write_buffer and self._write_callback:
            callback = self._write_callback
            self._write_callback = None
            self._run_callback(callback)

    def _consume(self, loc):
        result = self._read_buffer[:loc]
        self._read_buffer = self._read_buffer[loc:]
        return result

    def _check_closed(self):
        if not self.socket:
            raise IOError("Stream closed")

    def _add_io_state(self, state):
        if not self._state & state:
            self._state = self._state | state
            self.io_loop.update_handler(self.socket.fileno(), self._state)

    def read_until(self, delimiter, callback):
        assert not self._read_callback, "read"
        loc = self._read_buffer.find(delimiter)
        if loc != -1:
            self._run_callback(callback, self._consume(loc + len(delimiter)))
            return
        self._check_closed()
        self._read_delimiter = delimiter
        self._read_callback = callback
        self._add_io_state(self.io_loop.READ)

    def read_bytes(self, num_bytes, callback):
        assert not self._read_callback, "read"
        if len(self._read_buffer) >= num_bytes:
            callback(self._consume(num_bytes)
            return
         self._check_closed()
         self._read_bytes = num_bytes
         self._read_callback = callback
         self._add_io_state(self.io_loop.READ)

    def write(self, data, callback=None):
        self._check_closed()
        self._write_buffer += data
        self._add_io_state(self.io_loop.WRITE)
        self._write_callback = callback

    def set_close_callback(self, callback):
        self._close_callback = callback

    def close(self):
        if self.socket is not None:
            self.io_loop.remove_handler(self.socket.fileno())
            self.socket.close()
            self.socket = None
            if self._close_callback:
                self._run_callback(self._close_callback)

    def reading(self):
        return self._read_callback is not None

    def writing(self):
        return len(self._write_buffer) > 0

    def closed(self):
        return self.socket is None


