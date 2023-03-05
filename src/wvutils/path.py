"""Path Utilities

This module provides utilities for working with paths.
"""

__all__ = [
    "cache_path",
    "ensure_abspath",
    # "is_iolike",
    "is_pathlike",
    "resolve_path",
    "stringify_path",
    "xdg_cache_path",
]

import logging
import os
from typing import Any

from wvutils.typing import FilePath

logger = logging.getLogger(__name__)


# def is_iolike(potential_io: Any) -> bool:
#     """Check if an Object is IO-Like
#
#     Args:
#         potential_io (Any): Object to check.
#
#     Returns:
#         bool: True if the object is IO-like, otherwise False.
#     """
#     return hasattr(potential_io, "read") and hasattr(potential_io, "write")


def is_pathlike(potential_path: Any) -> bool:
    """Check if an Object is Path-Like

    Args:
        potential_path (Any): Object to check.

    Returns:
        bool: True if the object is path-like, otherwise False.
    """
    return isinstance(potential_path, str) or hasattr(potential_path, "__fspath__")


def stringify_path(file_path: FilePath) -> str:
    """Resolve a Path-Like Object to a String

    Args:
        file_path (FilePath): Path-like object to stringify.

    Returns:
        str: Path-like object as a string.
    """
    if not isinstance(file_path, str):
        # e.g. pathlib.Path('/home/ubuntu') -> '/home/ubuntu'
        try:
            file_path = file_path.__fspath__()
        except AttributeError:
            raise TypeError(f"Object is not path-like: {file_path!r}")
    # Expand user directory values
    # e.g. '~' -> '/home/ubuntu'
    file_path = os.path.expanduser(file_path)
    return file_path


def ensure_abspath(file_path: str) -> str:
    """Make a Path Absolute if it is Not Already

    Args:
        file_path (str): Path to ensure is absolute.

    Returns:
        str: Absolute path.
    """
    return file_path if os.path.isabs(file_path) else os.path.abspath(file_path)


def resolve_path(file_path: FilePath) -> str:
    """Resolve a Path-Like Object to an Absolute Path that is a String

    Args:
        file_path (FilePath): Path-like object to resolve.

    Returns:
        str: Absolute path of the path-like object as a string.
    """
    return ensure_abspath(stringify_path(file_path))


def xdg_cache_path() -> str:
    """Base Directory to Store User-Specific Non-Essential Data Files

    This should be '${HOME}/.cache', but the 'HOME' environment variable may not exist on non-POSIX-compliant systems.
    On POSIX-compliant systems, the XDG base directory specification is followed exactly since '~' expands to '$HOME' if it is present.

    Returns:
        str: Path for XDG cache.
    """
    file_path = os.environ.get("XDG_CACHE_HOME")
    if not file_path or not os.path.isabs(file_path):
        file_path = os.path.join(os.path.expanduser("~"), ".cache")
    return file_path
