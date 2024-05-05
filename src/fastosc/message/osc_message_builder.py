"""Build OSC messages for client applications."""

# ruff: noqa: PLR2004
from __future__ import annotations

from datetime import datetime
from typing import Any

from fastosc.message import osc_message
from fastosc.message.arg_value import (
    ARG_TYPE_ARRAY_START,
    ARG_TYPE_ARRAY_STOP,
    ARG_TYPE_BLOB,
    ARG_TYPE_DOUBLE,
    ARG_TYPE_FALSE,
    ARG_TYPE_FLOAT,
    ARG_TYPE_INT,
    ARG_TYPE_INT64,
    ARG_TYPE_MIDI,
    ARG_TYPE_NIL,
    ARG_TYPE_RGBA,
    ARG_TYPE_STRING,
    ARG_TYPE_TIMETAG,
    ARG_TYPE_TRUE,
    SUPPORTED_ARG_TYPES,
    ArgValue,
)

from .parsing import osc_types

# ruff: noqa: PLR0912,B904


class BuildError(Exception):
    """Error raised when an incomplete message is trying to be built."""


class OscMessageBuilder:
    """Builds arbitrary OscMessage instances."""

    def __init__(self, address: str | None = None) -> None:
        """Initialize a new builder for a message.

        Args:
          - address: The osc address to send this message to.
        """
        self._address = address
        self._args: list[tuple[str, ArgValue]] = []

    @property
    def address(self) -> str | None:
        """Returns the OSC address this message will be sent to."""
        return self._address

    @address.setter
    def address(self, value: str) -> None:
        """Sets the OSC address this message will be sent to."""
        self._address = value

    @property
    def args(self) -> list[tuple[str, ArgValue]]:
        """Returns the (type, value) arguments list of this message."""
        return self._args

    def _valid_type(self, arg_type: str) -> bool:
        if arg_type in SUPPORTED_ARG_TYPES:
            return True
        if isinstance(arg_type, (list, tuple)):
            return all(self._valid_type(sub_type) for sub_type in arg_type)
        return False

    def add_arg(self, arg_value: ArgValue, arg_type: str | None = None) -> None:
        """Add a typed argument to this message.

        Args:
          - arg_value: The corresponding value for the argument.
          - arg_type: A value in ARG_TYPE_* defined in this class,
                      if none then the type will be guessed.
        Raises:
          - ValueError: if the type is not supported.::wq
        """
        if arg_type and not self._valid_type(arg_type):
            raise ValueError(f"arg_type must be one of {SUPPORTED_ARG_TYPES}, or an array of valid types")
        if not arg_type:
            arg_type = self._get_arg_type(arg_value)
        if isinstance(arg_type, (list, tuple)):
            self._args.append((ARG_TYPE_ARRAY_START, None))
            for v, t in zip(arg_value, arg_type):  # type: ignore[var-annotated, arg-type]
                self.add_arg(v, t)  # type: ignore[var-annotated, arg-type]
            self._args.append((ARG_TYPE_ARRAY_STOP, None))
        else:
            self._args.append((arg_type, arg_value))

    # The return type here is actually Union[str, List[<self>]], however there
    # is no annotation for a recursive type like this.
    def _get_arg_type(self, arg_value: ArgValue) -> str:
        """Guess the type of a value.
        Args:
          - arg_value: The value to guess the type of.
        Raises:
          - ValueError: if the type is not supported.
        """
        if isinstance(arg_value, str):
            arg_type: str | Any = ARG_TYPE_STRING
        elif isinstance(arg_value, bytes):
            arg_type = ARG_TYPE_BLOB
        elif arg_value is True:
            arg_type = ARG_TYPE_TRUE
        elif arg_value is False:
            arg_type = ARG_TYPE_FALSE
        elif isinstance(arg_value, datetime):
            arg_type = ARG_TYPE_TIMETAG
        elif isinstance(arg_value, int):
            arg_type = ARG_TYPE_INT64 if arg_value.bit_length() > 32 else ARG_TYPE_INT
        elif isinstance(arg_value, float):
            arg_type = ARG_TYPE_FLOAT
        elif isinstance(arg_value, tuple) and len(arg_value) == 4:
            is_midi = True
            for i in arg_value:
                if not isinstance(i, int):  # for now assume midi if its a tuple of all ints
                    is_midi = False
            arg_type = ARG_TYPE_MIDI if is_midi else [self._get_arg_type(v) for v in arg_value]
        elif isinstance(arg_value, (list, tuple)):
            arg_type = [self._get_arg_type(v) for v in arg_value]
        elif arg_value is None:
            arg_type = ARG_TYPE_NIL
        else:
            raise ValueError("Infered arg_value type is not supported")
        return arg_type

    def build(self) -> osc_message.OscMessage:
        """Builds an OscMessage from the current state of this builder.

        Raises:
          - BuildError: if the message could not be build or if the address
                        was empty.

        Returns:
          - an osc_message.OscMessage instance.
        """
        if not self._address:
            raise BuildError("OSC addresses cannot be empty")
        dgram = b""
        try:
            # Write the address.
            dgram += osc_types.write_string(self._address)
            if not self._args:
                dgram += osc_types.write_string(",")
                return osc_message.OscMessage(dgram)

            # Write the parameters.
            arg_types = "".join([arg[0] for arg in self._args])  # type: ignore[misc]
            dgram += osc_types.write_string("," + arg_types)
            for arg_type, value in self._args:
                if arg_type == ARG_TYPE_STRING:
                    dgram += osc_types.write_string(value)  # type: ignore[arg-type]
                elif arg_type == ARG_TYPE_INT:
                    dgram += osc_types.write_int(value)  # type: ignore[arg-type]
                elif arg_type == ARG_TYPE_INT64:
                    dgram += osc_types.write_int64(value)  # type: ignore[arg-type]
                elif arg_type == ARG_TYPE_FLOAT:
                    dgram += osc_types.write_float(value)  # type: ignore[arg-type]
                elif arg_type == ARG_TYPE_TIMETAG:
                    dgram += osc_types.write_timetag(value)  # type: ignore[arg-type]
                elif arg_type == ARG_TYPE_DOUBLE:
                    dgram += osc_types.write_double(value)  # type: ignore[arg-type]
                elif arg_type == ARG_TYPE_BLOB:
                    dgram += osc_types.write_blob(value)  # type: ignore[arg-type]
                elif arg_type == ARG_TYPE_RGBA:
                    dgram += osc_types.write_rgba(value)  # type: ignore[arg-type]
                elif arg_type == ARG_TYPE_MIDI:
                    dgram += osc_types.write_midi(value)  # type: ignore[arg-type]
                elif arg_type in (
                    ARG_TYPE_TRUE,
                    ARG_TYPE_FALSE,
                    ARG_TYPE_ARRAY_START,
                    ARG_TYPE_ARRAY_STOP,
                    ARG_TYPE_NIL,
                ):
                    continue
                else:
                    raise BuildError(f"Incorrect parameter type found {arg_type}")  # type: ignore[str-bytes-safe]

            return osc_message.OscMessage(dgram)
        except osc_types.BuildError as be:
            raise BuildError(f"Could not build the message: {be}")
