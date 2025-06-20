import socket
import threading
import time
from typing import Optional
from urllib.parse import urlparse

from spectator.writer import Writer
from spectator.writer.line_buffer import LineBuffer


class UnixWriter(Writer):
    """Writer that outputs data to a Unix Domain Socket."""

    def __init__(self, location: str, buffer_size: int = 0) -> None:
        super().__init__()
        self._logger.info("initialize UnixWriter to %s", location)
        self._location = urlparse(location).path
        self._buffer: Optional[LineBuffer] = LineBuffer(buffer_size) if buffer_size > 0 else None
        self._thread = threading.Thread(target=self._background_flush, daemon=True)
        self._lock = threading.Lock()
        self._sock = None

        if self._buffer is not None:
            self._logger.info("start UnixWriter background flush, every 5 seconds")
            self._thread.start()

    def _background_flush(self) -> None:
        while True:
            time.sleep(5)
            if len(self._buffer) > 0:
                with self._lock:
                    try:
                        self._sock.sendto(bytes(self._buffer.flush(), encoding="utf-8"), self._location)
                    except IOError:
                        self._logger.error("failed to write buffer from background flush")

    def _acquire_socket(self) -> None:
        # lazily instantiate the socket, in a thread-safe manner
        if self._sock is None:
            try:
                with self._lock:
                    if self._sock is None:
                        self._sock = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_DGRAM)
            except Exception as e:
                self._logger.error("exception during socket acquire: %s", e)

    def _write_buffer(self, line: str) -> None:
        with self._lock:
            if self._buffer.append(line):
                try:
                    self._sock.sendto(bytes(self._buffer.flush(), encoding="utf-8"), self._location)
                except IOError:
                    self._logger.error("failed to write line=%s", line)

    def _write_socket(self, line: str) -> None:
        try:
            self._sock.sendto(bytes(line, encoding="utf-8"), self._location)
        except IOError:
            self._logger.error("failed to write line=%s", line)

    def write(self, line: str) -> None:
        self._logger.debug("write line=%s", line)
        self._acquire_socket()

        if self._buffer is not None:
            self._write_buffer(line)
        else:
            self._write_socket(line)

    def close(self) -> None:
        self._sock.close()
