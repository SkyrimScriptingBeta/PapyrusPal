"""Qt typing utilities"""

from .signal_typing import (
    BoolSignalHandler,
    VoidSignalHandler,
    IntSignalHandler,
    PointSignalHandler,
    GenericSignalHandler,
    signal_handler_for,
    as_bool_handler,
    as_void_handler,
    as_int_handler,
    as_generic_handler,
)

__all__ = [
    "BoolSignalHandler",
    "VoidSignalHandler",
    "IntSignalHandler",
    "PointSignalHandler",
    "GenericSignalHandler",
    "signal_handler_for",
    "as_bool_handler",
    "as_void_handler",
    "as_int_handler",
    "as_generic_handler",
]
