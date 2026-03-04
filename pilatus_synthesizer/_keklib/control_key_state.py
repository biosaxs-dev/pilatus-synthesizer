"""Shift/Ctrl key state tracking for matplotlib event handlers.

Original: lib/KekLib/ControlKeyState.py
Copyright (c) SAXS Team, KEK-PF
"""

_shift_key_state = False
_ctrl_key_state = False


def set_shift_key_state(state: bool) -> None:
    global _shift_key_state
    _shift_key_state = state


def set_ctrl_key_state(state: bool) -> None:
    global _ctrl_key_state
    _ctrl_key_state = state


def get_shift_key_state() -> bool:
    return _shift_key_state


def get_ctrl_key_state() -> bool:
    return _ctrl_key_state
