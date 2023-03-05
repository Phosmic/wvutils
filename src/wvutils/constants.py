"""Constants

This module contains constants used throughout the package.
"""

from string import ascii_letters, digits

__all__ = [
    "DEFAULT_SAFECHARS_ALLOWED_CHARS",
]

DEFAULT_SAFECHARS_ALLOWED_CHARS: set[str] = {"-", "_", *ascii_letters, *digits}
