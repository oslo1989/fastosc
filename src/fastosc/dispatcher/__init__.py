from __future__ import annotations

import logging
import re
from typing import Callable

from fastosc.dispatcher.handler import HandlerInfo
from fastosc.docs import HandlerDescription, HandlerInputParam
from fastosc.message.arg_value import ArgValue
from fastosc.message.osc_bundle import OscBundle
from fastosc.message.osc_message import OscMessage
from fastosc.server.server_base import OSCServerBase

MAX_LINE_LENGTH = 45


class Dispatcher:
    def __init__(self, *, logger: logging.Logger, base_address: str = "") -> None:
        self._server: OSCServerBase | None = None
        self._callbacks: dict[str, Callable[[list[ArgValue], tuple[str, int]], list[ArgValue]]] = {}
        self._logger = logger
        if not base_address.startswith("/"):
            base_address = f"/{base_address}"
        self._base_address = base_address
        self._handler_docs: list[HandlerDescription] = []

    def set_server(self, server: OSCServerBase) -> None:
        self._server = server

    def add_handler(
        self,
        *,
        address: str,
        handler: Callable[[list[ArgValue], tuple[str, int]], list[ArgValue]],
        handler_info: HandlerInfo | None = None,
    ) -> None:
        """
        Add an OSC handler.

        Args:
            address: The OSC address string
            handler: A handler function, with signature:
                     params: Tuple[Any, ...]
            handler_info: metadata about the incoming message
        """
        if not address.startswith("/"):
            address = f"/{address}"
        address = f"{self._base_address}{address}"
        route_log_info = f"Added route {address}"
        self._callbacks[address] = handler
        if handler_info:
            s = handler_info.signature
            params = [
                HandlerInputParam(name=s.parameters[p].name, type=s.parameters[p].annotation)
                for p in s.parameters
                if s.parameters[p].name != "self"
            ]
            handler_desc = HandlerDescription(
                params=params,
                doc=handler_info.doc,
                result_type=s.return_annotation,
                address=address,
                function_name=handler_info.function_name,
            )
            self._handler_docs.append(handler_desc)
            whitespace = (MAX_LINE_LENGTH - len(address)) * " "
            return_type_str = ""
            if handler_desc.result_type.startswith("list"):
                return_type_str = handler_desc.result_type[4:-1]
            elif handler_desc.result_type.startswith("tuple"):
                return_type_str = handler_desc.result_type[6:-1]
            else:
                return_type_str = handler_desc.result_type
            route_log_info = (
                f"{route_log_info}{whitespace}"
                f"[{', '.join([f'{p.name}:{p.type}' for p in handler_desc.params])}] "
                f"-> [{return_type_str}]"
            )
        self._logger.info(route_log_info)

    def clear_handlers(self) -> None:
        """
        Remove all existing OSC handlers.
        """

        self._callbacks = {}

    def send(
        self,
        *,
        address: str,
        remote_addr: tuple[str, int],
        params: list[ArgValue],
        include_base_address: bool = False,
    ) -> None:
        if self._server:
            if include_base_address:
                address = f"{self._base_address}{address}"
            self._server.send(address=address, params=params, remote_addr=remote_addr)
        else:
            self._logger.error(f"Trying to send OSC message to remote address {remote_addr}, but not server is set up")

    def process_message(self, *, message: OscMessage, remote_addr: tuple[str, int]) -> None:
        if message.address in self._callbacks:
            callback = self._callbacks[message.address]
            rv = callback(message.params, remote_addr)
            if rv:
                assert isinstance(rv, list)
                if rv != [None]:
                    self.send(address=message.address, params=rv, remote_addr=remote_addr)
        elif "*" in message.address:
            regex = message.address.replace("*", "[^/]+")
            for callback_address, callback in self._callbacks.items():
                if re.match(regex, callback_address):
                    try:
                        rv = callback(message.params, remote_addr)
                    except ValueError:
                        # --------------------------------------------------------------------------------
                        # Don't throw errors for queries that require more arguments
                        # (e.g. /live/track/get/send with no args)
                        # --------------------------------------------------------------------------------
                        continue
                    except AttributeError:
                        # --------------------------------------------------------------------------------
                        # Don't throw errors when trying to create listeners for properties that can't
                        # be listened for (e.g. can_be_armed, is_foldable)
                        # --------------------------------------------------------------------------------
                        continue
                    if rv is not None:
                        assert isinstance(rv, list)
                        self.send(address=callback_address, params=rv, remote_addr=remote_addr)
        else:
            self._logger.error(f"Unknown OSC address: {message.address}")
            # todo: return the error to the socket that sent it

    def process_bundle(self, *, bundle: OscBundle, remote_addr: tuple[str, int]) -> None:
        for i in bundle:
            if OscBundle.dgram_is_bundle(i.dgram):
                self.process_bundle(bundle=i, remote_addr=remote_addr)
            else:
                self.process_message(message=i, remote_addr=remote_addr)
