from __future__ import annotations

import logging
from abc import ABC

from fastosc.dispatcher import Dispatcher
from fastosc.server.server_base import OSCServerBase


class OSCDispatcherServer(OSCServerBase, ABC):
    def __init__(self, dispatcher: Dispatcher, logger: logging.Logger, local_addr: tuple[str, int]) -> None:
        super().__init__(logger, local_addr)
        self._dispatcher = dispatcher
        self._dispatcher.set_server(self)
