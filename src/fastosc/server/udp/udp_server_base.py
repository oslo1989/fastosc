from __future__ import annotations

import logging
import socket

from fastosc.dispatcher import Dispatcher
from fastosc.message.osc_bundle import OscBundle
from fastosc.message.osc_message import OscMessage
from fastosc.server.dispatcher_server import OSCDispatcherServer


class OSCUDPServerBase(OSCDispatcherServer):
    def __init__(
        self,
        *,
        dispatcher: Dispatcher,
        logger: logging.Logger,
        local_addr: tuple[str, int],
    ) -> None:
        super().__init__(logger=logger, local_addr=local_addr, dispatcher=dispatcher)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self._socket.bind(self._local_addr)

    def _send_bytes(self, data: bytes, remote_addr: tuple[str, int]) -> None:
        self._socket.sendto(data, remote_addr)

    def _parse_datagram(self, *, data: bytes, remote_addr: tuple[str, int]) -> None:
        if OscMessage.dgram_is_message(data):
            self._dispatcher.process_message(message=OscMessage(data), remote_addr=remote_addr)
        elif OscBundle.dgram_is_bundle(data):
            self._dispatcher.process_bundle(bundle=OscBundle(data), remote_addr=remote_addr)
        else:
            logging.debug(f"unknown osc message: {data} from {remote_addr}")  # type: ignore[str-bytes-safe]
