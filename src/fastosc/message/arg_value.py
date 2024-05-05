from __future__ import annotations

from datetime import datetime
from typing import Any, List, Union

from fastosc.message.parsing import osc_types

ArgValue = Union[
    None,
    str,
    bytes,
    bool,
    int,
    float,
    tuple,
    datetime,
    osc_types.MidiPacket,
    List[
        Union[
            None,
            str,
            bytes,
            bool,
            int,
            float,
            tuple,
            datetime,
            osc_types.MidiPacket,
            List[
                Union[
                    None,
                    str,
                    bytes,
                    bool,
                    int,
                    float,
                    tuple,
                    datetime,
                    osc_types.MidiPacket,
                    List[
                        Union[
                            None,
                            str,
                            bytes,
                            bool,
                            int,
                            float,
                            tuple,
                            datetime,
                            osc_types.MidiPacket,
                            List[
                                Union[
                                    None,
                                    str,
                                    bytes,
                                    bool,
                                    int,
                                    float,
                                    tuple,
                                    datetime,
                                    osc_types.MidiPacket,
                                    List[
                                        Union[
                                            None,
                                            str,
                                            bytes,
                                            bool,
                                            int,
                                            float,
                                            tuple,
                                            datetime,
                                            osc_types.MidiPacket,
                                            List[
                                                Union[
                                                    None,
                                                    str,
                                                    bytes,
                                                    bool,
                                                    int,
                                                    float,
                                                    tuple,
                                                    datetime,
                                                    osc_types.MidiPacket,
                                                    List[
                                                        Union[
                                                            None,
                                                            str,
                                                            bytes,
                                                            bool,
                                                            int,
                                                            float,
                                                            tuple,
                                                            datetime,
                                                            osc_types.MidiPacket,
                                                            List[
                                                                Union[
                                                                    None,
                                                                    str,
                                                                    bytes,
                                                                    bool,
                                                                    int,
                                                                    float,
                                                                    tuple,
                                                                    datetime,
                                                                    osc_types.MidiPacket,
                                                                    List[
                                                                        Union[
                                                                            None,
                                                                            str,
                                                                            bytes,
                                                                            bool,
                                                                            int,
                                                                            float,
                                                                            tuple,
                                                                            datetime,
                                                                            osc_types.MidiPacket,
                                                                            List[
                                                                                Union[
                                                                                    None,
                                                                                    str,
                                                                                    bytes,
                                                                                    bool,
                                                                                    int,
                                                                                    float,
                                                                                    tuple,
                                                                                    datetime,
                                                                                    osc_types.MidiPacket,
                                                                                    List[
                                                                                        Union[
                                                                                            None,
                                                                                            str,
                                                                                            bytes,
                                                                                            bool,
                                                                                            int,
                                                                                            float,
                                                                                            tuple,
                                                                                            datetime,
                                                                                            osc_types.MidiPacket,
                                                                                            List[Any],
                                                                                        ]
                                                                                    ],
                                                                                ]
                                                                            ],
                                                                        ]
                                                                    ],
                                                                ]
                                                            ],
                                                        ]
                                                    ],
                                                ]
                                            ],
                                        ]
                                    ],
                                ]
                            ],
                        ]
                    ],
                ]
            ],
        ]
    ],
]

ARG_TYPE_FLOAT = "f"
ARG_TYPE_DOUBLE = "d"
ARG_TYPE_INT = "i"
ARG_TYPE_INT64 = "h"
ARG_TYPE_STRING = "s"
ARG_TYPE_BLOB = "b"
ARG_TYPE_RGBA = "r"
ARG_TYPE_MIDI = "m"
ARG_TYPE_TIMETAG = "t"
ARG_TYPE_TRUE = "T"
ARG_TYPE_FALSE = "F"
ARG_TYPE_NIL = "N"

ARG_TYPE_ARRAY_START = "["
ARG_TYPE_ARRAY_STOP = "]"

SUPPORTED_ARG_TYPES = (
    ARG_TYPE_FLOAT,
    ARG_TYPE_DOUBLE,
    ARG_TYPE_INT,
    ARG_TYPE_INT64,
    ARG_TYPE_TIMETAG,
    ARG_TYPE_BLOB,
    ARG_TYPE_STRING,
    ARG_TYPE_RGBA,
    ARG_TYPE_MIDI,
    ARG_TYPE_TRUE,
    ARG_TYPE_FALSE,
    ARG_TYPE_NIL,
)
