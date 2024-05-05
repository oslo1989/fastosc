from __future__ import annotations

import errno
import logging
import traceback

from fastosc.dispatcher import Dispatcher
from fastosc.server.udp.udp_server_base import OSCUDPServerBase


class OSCUDPPullServer(OSCUDPServerBase):
    """
    OSC Udp server that stores datagrams and has a process() method to pull in stored datagrams.
    This is more efficient in certain environments such as Ableton live embedded python which
    does not support multithreading well (i.e it gives latencies in 100+ms and cannot handle high rates of inbound
    messages without spiking latency.
    """

    def __init__(self, *, dispatcher: Dispatcher, logger: logging.Logger, local_addr: tuple[str, int]) -> None:
        super().__init__(logger=logger, dispatcher=dispatcher, local_addr=local_addr)
        self._socket.setblocking(False)

    def process(self) -> None:
        """
        Synchronously process all data queued on the OSC socket.
        """
        try:
            while True:
                data, remote_addr = self._socket.recvfrom(65536)
                self._parse_datagram(data=data, remote_addr=remote_addr)

        except OSError as e:
            if e.errno == errno.ECONNRESET:
                # --------------------------------------------------------------------------------
                # This benign error seems to occur on startup on Windows
                # --------------------------------------------------------------------------------
                self._logger.warning("Non-fatal socket error: %s" % (traceback.format_exc()))
            elif e.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                # --------------------------------------------------------------------------------
                # Another benign networking error, throw when no data is received
                # on a call to recvfrom() on a non-blocking socket
                # --------------------------------------------------------------------------------
                pass
            else:
                # --------------------------------------------------------------------------------
                # Something more serious has happened
                # --------------------------------------------------------------------------------
                self._logger.error("Socket error: %s" % (traceback.format_exc()))

        except Exception as e:
            self._logger.error("Error handling OSC message: %s" % e)
            self._logger.warning("%s" % traceback.format_exc())

    def shutdown(self) -> None:
        """
        Shutdown the server network sockets.
        """
        self._socket.close()
