from __future__ import annotations

import inspect
from dataclasses import dataclass


@dataclass
class HandlerInfo:
    signature: inspect.Signature
    doc: str | None
    shape: type | list[type] | None = None
    function_name: str | None = None
