# ruff: noqa: FBT001,FBT002
from __future__ import annotations

import inspect
import logging
from typing import Any, Callable

from fastosc.dispatcher import Dispatcher
from fastosc.dispatcher.handler import HandlerInfo
from fastosc.message.arg_value import ArgValue
from fastosc.message.osc_message import OscMessage


def _format_response(arg_value: ArgValue) -> list[ArgValue]:
    if isinstance(arg_value, list):
        return arg_value
    return [arg_value]


def wrapper(
    address: str,
    prefix_: str,
    include_original_message: bool = False,
    include_remote_addr: bool = False,
    listen: bool = False,
) -> Callable[..., Callable[[list[ArgValue], tuple[str, int]], list[ArgValue]]]:
    if not address.startswith("/"):
        address = f"/{address}"

    # todo maybe clean up this code a little bit as it was changed to infer parameter types
    # from handler function signature vs annotation
    def check_accepts(
        f: Callable[..., Any],
    ) -> Callable:
        sign = inspect.signature(f)
        shape = [sign.parameters[p].annotation for p in sign.parameters]
        shape = [eval(t) if isinstance(t, str) else t for t in shape]
        if len(shape) == 1:
            shape = []
        if len(shape) > 1:
            shape = shape[1:]
        orignal_shape = shape
        if not shape:
            shape = []
        if not isinstance(shape, list):
            shape = [shape]

        shape = [OSCRouter, *shape]
        if include_remote_addr:
            shape = [*shape, tuple]
        if include_original_message:
            shape = [*shape, OscMessage]  # todo: osc.Message here as well for validation

        arg_count = f.__code__.co_argcount - 1

        shape_len = len(shape) - 1

        if shape_len < arg_count:
            raise InvalidParameterValueException(
                f"too many arguments, expected {shape_len} " f"arguments but signature has {arg_count}.",
            )
        if shape_len > arg_count:
            raise InvalidParameterValueException(
                f"too few arguments, expected {shape_len} " f"arguments but signature has {arg_count}.",
            )

        # do we do someting with remote_addres?
        # maybe include it if part of parameters? remote_addr param - inject as final param if needed
        def new_f(self: OSCRouter, original_args: list[ArgValue], remote_address: tuple[str, int]) -> list[ArgValue]:
            for a, t in zip(original_args, shape[1:] if len(shape) > 1 else []):
                q = "'" if isinstance(a, str) else ""
                if not isinstance(a, t):
                    raise InvalidParameterValueException(
                        f"arg {q}{a}{q} of type <{type(a).__name__}> "  # type: ignore[str-bytes-safe]
                        f"does not match <{t.__name__}>",
                    )
            args = original_args
            if include_remote_addr:
                args = [*original_args, remote_address]  # type: ignore[list-item]
            if include_original_message:
                args = [*args, original_args]  # type: ignore[list-item]
            return _format_response(f(self, *args))

        if listen:
            new_f.listen = True  # type: ignore[attr-defined]
        new_f.osc_handler = True  # type: ignore[attr-defined]
        new_f.address = f"/{prefix_}{address}"  # type: ignore[attr-defined]
        new_f.raw_address = address  # type: ignore[attr-defined]
        new_f.__name__ = f.__name__  # type: ignore[attr-defined]
        new_f.handler_info = HandlerInfo(  # type: ignore[attr-defined]
            shape=orignal_shape,
            signature=sign,
            doc=inspect.getdoc(f),
            function_name=f.__name__,
        )
        return new_f

    return check_accepts


def osc_get(
    address: str,
    include_original_message: bool = False,
    include_remote_addr: bool = False,
    listen: bool = True,
) -> Callable[..., Callable[[list[ArgValue], tuple[str, int]], list[ArgValue]]]:
    return wrapper(
        address,
        "get",
        include_original_message=include_original_message,
        include_remote_addr=include_remote_addr,
        listen=listen,
    )


def osc_set(
    address: str,
    include_original_message: bool = False,
    include_remote_addr: bool = False,
) -> Callable[..., Callable[[list[ArgValue], tuple[str, int]], list[ArgValue]]]:
    return wrapper(
        address,
        "set",
        include_original_message=include_original_message,
        include_remote_addr=include_remote_addr,
    )


def _create_listener_key(address: str, remote_addr: tuple[str, int], args: list[ArgValue]) -> str:
    return f"{remote_addr}|{address}|{args}"


class OSCRouter:
    _listeners: dict[str, Callable]
    _routers: list[OSCRouter]

    def _add_router(self, *, router: OSCRouter) -> None:
        self._routers.append(router)

    def _add_handler(
        self,
        *,
        address: str,
        handler: Callable[[list[ArgValue], tuple[str, int]], list[ArgValue]],
        handler_info: HandlerInfo | None = None,
    ) -> None:
        self._dispatcher.add_handler(address=f"{self._namespace}{address}", handler=handler, handler_info=handler_info)

    # class for overriding so an implementing class can wire up the listener as sees fit,
    # but this class will maintain a dict / cache with address/callback ids etc
    def _add_listener(self, *, address: str, listener: Callable, args: list[Any]) -> Callable[[], None] | None:
        # the method returns how to remove itself
        # this will already be validated for the appropriate address so it should be safe,
        # but not sure how we will transfer the types properly.
        # this must be implemented by the implementing class
        # the idea is that you get the args, like /track/device/parameter args= [tidx,didx,pidx] _song.tracks[0
        #  if address == "/tempo"
        #   tidx, didx, pidx = args
        #   param = _song.tracks[tidx].devices[didx].parameters[pidx].add_tempo_listener(listener)
        # if hasattr(param, f"add_{address}_listener"):
        " the listener class should do a call to the get of the param with the args" ""

    # class for overriding so an implementing class can remove up the listener as sees fit
    def _remove_listener(self, address: str, listener: Callable, args: list[Any]) -> None:
        # here, we can just look up the result from the saved listener method and invoke it?
        # self.listeners[x] = _add_listener()
        # if self._listeners.get(x)]:
        #   self._listeners()
        pass

    def _setup_listener(
        self,
        h: Callable[[list[ArgValue], tuple[str, int]], list[ArgValue]],
        start: bool = False,
        stop: bool = False,
    ) -> tuple[str, Callable[[list[ArgValue], tuple[str, int]], list[ArgValue]]]:
        if not start and not stop:
            raise InvalidParameterValueException("Need to set either stop or start for listener")
        prefix = "/start_listen" if start else "/stop_listen"
        address: str = h.address  # type: ignore[attr-defined]
        raw_address: str = h.raw_address  # type: ignore[attr-defined]

        def listener(args: list[ArgValue], remote_address: tuple[str, int]) -> None:
            key = _create_listener_key(address=address, remote_addr=remote_address, args=args)
            self._logger.info(key)
            if start:
                if key not in self._listeners:

                    def callback() -> None:
                        self._dispatcher.send(
                            address=f"{self._namespace}{address}",
                            remote_addr=remote_address,
                            params=h(args, remote_address),
                            include_base_address=True,
                        )

                    added_listener = self._add_listener(address=raw_address, listener=callback, args=args)
                    if added_listener:
                        self._listeners[key] = added_listener
                        logging.info(f"listener added for {address} and args {args} for client@{remote_address}")
                    else:
                        logging.info(f"start listen called for {address} and args {args}, but no listener was added.")
                else:
                    logging.info(
                        f"listener already existing for {address} and args {args} for client@{remote_address}, "
                        f"will not add unless sending a specific callback query param trailing (|Nil|QueryId",
                    )
            elif stop and key in self._listeners:
                self._listeners[key]()
                logging.info(f"listener stopped for {address} and args {args} for client@{remote_address}")

            # this will also send a message on every start / stop request
            self._dispatcher.send(
                address=f"{self._namespace}{address}",
                remote_addr=remote_address,
                params=h(args, remote_address),
                include_base_address=True,
            )

        return f"{prefix}{h.raw_address}", listener  # type: ignore[attr-defined,return-value]

    def _setup_handlers(self) -> None:
        handlers = [d[1] for d in inspect.getmembers(self) if not d[0].startswith("_") and inspect.ismethod(d[1])]
        for h in handlers:
            if hasattr(h, "osc_handler") and h.osc_handler and hasattr(h, "address") and h.address:
                handler_info: HandlerInfo | None = None
                if hasattr(h, "handler_info"):
                    handler_info = h.handler_info
                self._add_handler(
                    address=h.address,
                    handler=h,
                    handler_info=handler_info,
                )
                if hasattr(h, "listen") and h.listen and hasattr(h, "raw_address") and h.raw_address:
                    start_address, start_listen = self._setup_listener(h, start=True)
                    self._add_handler(
                        address=start_address,
                        handler=start_listen,
                        handler_info=handler_info,
                    )
                    stop_address, stop_listen = self._setup_listener(h, stop=True)
                    self._add_handler(
                        address=stop_address,
                        handler=stop_listen,
                        handler_info=handler_info,
                    )

    def clear_listeners(self) -> None:
        pass
        # for listener in self._listeners:
        # call listener()
        #     if self._song.tempo_has_listener(listener):
        #         self._song.remove_tempo_listener(listener)

    def __init__(self, *, dispatcher: Dispatcher, namespace: str) -> None:
        self._dispatcher = dispatcher
        if not namespace.startswith("/"):
            namespace = f"/{namespace}"
        self._namespace = namespace
        self._logger = self._dispatcher._logger
        self._listeners = {}
        self._routers = []
        self._setup_handlers()

    def _clear_listeners(self) -> None:
        for stop_listener in self._listeners.values():
            stop_listener()


class InvalidParameterValueException(Exception):
    pass
