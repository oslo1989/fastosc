from __future__ import annotations

from fastosc.message.arg_value import ArgValue
from fastosc.message.osc_message_builder import BuildError, OscMessageBuilder


def convert_message(*, address: str, params: list[ArgValue]) -> bytes:
    msg_builder = OscMessageBuilder(address)
    for param in params or []:
        msg_builder.add_arg(param)
    try:
        msg = msg_builder.build()
        return msg.dgram
    except BuildError as e:
        raise e
