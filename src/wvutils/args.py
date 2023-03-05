"""Argument Parsing Utilities

This module contains utilities for parsing arguments from the command line.
"""

import logging
from collections.abc import Callable

from wvutils.constants import DEFAULT_SAFECHARS_ALLOWED_CHARS

__all__ = [
    "nonempty_string",
    "safechars_string",
]

logger = logging.getLogger(__name__)


def nonempty_string(name: str) -> Callable:
    """Ensure a String is Non-Empty

    Example Usage:
        ```python
        @classmethod
        def _cli_setup_parser(cls, subparser):
            subparser.add_argument("hashtag", type=nonempty_string("hashtag"), help="A hashtag (without #)")
        ```

    Args:
        name (str): Name of the function, used for debugging.

    Returns:
        Callable: The decorated function.
    """

    def func(text):
        text = text.strip()
        if not text:
            raise ValueError("Must not be an empty string")
        return text

    func.__name__ = name
    return func


def safechars_string(
    name: str,
    allowed_chars: str | set[str] | tuple[str] | list[str] | None = None,
) -> Callable:
    """Ensure a String Contains Only Safe Characters

    Example Usage:

    ```python
    @classmethod
    def _cli_setup_parser(cls, subparser):
        subparser.add_argument("--session-key", type=safechars_string, help="Key to share a single token across processes")
    ```

    Args:
        name (str): Name of the function, used for debugging.
        allowed_chars (str | set[str] | tuple[str] | list[str] | None, optional): Custom characters used to validate the function name. Defaults to None.

    Returns:
        Callable: The decorated function.
    """
    if allowed_chars is None:
        # Default to alphanum
        allowed_chars = DEFAULT_SAFECHARS_ALLOWED_CHARS
    else:
        # Prepare user-provided chars
        allowed_chars = set(allowed_chars)

    def func(text):
        text = text.strip()
        for char in text:
            if char not in allowed_chars:
                msg = ""
                msg += "Invalid string. Must consist of characters ["
                if allowed_chars:
                    msg += "'"
                    msg += "', '".join(allowed_chars)
                    msg += "'"
                msg += "]."
                raise ValueError(msg)
        return text

    func.__name__ = name
    return func
