"""Custom exception class.

Original: KekLib/OurException.py
Copyright (c) SAXS Team, KEK-PF
"""


class OurException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
