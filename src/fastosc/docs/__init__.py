from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HandlerInputParam:
    name: str
    type: str


@dataclass
class HandlerDescription:
    address: str
    params: list[HandlerInputParam]
    result_type: str
    doc: str | None = None
    function_name: str | None = None
