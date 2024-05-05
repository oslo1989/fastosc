from __future__ import annotations

import logging
import traceback
from abc import ABC, abstractmethod

from fastosc.message.arg_value import ArgValue
from fastosc.message.convert import convert_message
from fastosc.message.osc_message_builder import BuildError


class OSCServerBase(ABC):
    def __init__(self, logger: logging.Logger, local_addr: tuple[str, int]) -> None:
        self._logger = logger
        self._local_addr = local_addr
        self._logger.info("Starting OSC server (local %s)", str(self._local_addr))

    @abstractmethod
    def _send_bytes(self, data: bytes, remote_addr: tuple[str, int]) -> None:
        pass

    def send(self, *, address: str, params: list[ArgValue], remote_addr: tuple[str, int]) -> None:
        try:
            self._send_bytes(data=convert_message(address=address, params=params), remote_addr=remote_addr)
        except BuildError:
            self._logger.error(f"OSC build error: {traceback.format_exc()}")
