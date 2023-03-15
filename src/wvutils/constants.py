"""Constant values.

This module contains constants that are used throughout the package.
"""

from string import ascii_letters, digits
from typing import Final

__all__ = [
    "DEFAULT_SAFECHARS_ALLOWED_CHARS",
]

DEFAULT_SAFECHARS_ALLOWED_CHARS: Final[set[str]] = {"-", "_", *ascii_letters, *digits}
