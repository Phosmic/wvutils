"""Common Utilities

This module contains common utilities used throughout packages.
"""

import copy
import gc
import logging
import platform
import sys
from collections.abc import Generator, Sequence
from io import BufferedReader
from typing import Any

from wvutils.typing import FilePath

from wvutils.path import resolve_path

__all__ = [
    "chunker",
    "count_lines_in_file",
    "gc_set_threshold",
    "is_iterable",
    "rename_key",
    "sys_set_recursion_limit",
    "unnest_key",
]

logger = logging.getLogger(__name__)


def _count_generator(bytes_io: BufferedReader) -> Generator[bytes, None, None]:
    reader = bytes_io.raw.read
    b = reader(1024 * 1024)
    while b:
        yield b
        b = reader(1024 * 1024)


def count_lines_in_file(input_path: FilePath) -> int:
    """Count the Number of Lines in a File

    All files have at least 1 line:
        number of lines = # of newlines + 1

    Args:
        input_path (FilePath): Path of the file to count lines in.

    Returns:
        int: Total number of lines in the file.
    """
    input_path = resolve_path(input_path)
    num_lines = 1
    with open(input_path, mode="rb") as rbf:
        for buffer in _count_generator(rbf):
            num_lines += buffer.count(b"\n")
    return num_lines


def sys_set_recursion_limit() -> None:
    """Raise Recursion Limit to Allow for More Recurse"""
    sys.setrecursionlimit(10000)
    logger.debug("Adjusted Python recursion to allow more recurse")


def gc_set_threshold() -> None:
    """Reduce Number of GC Runs to Improve Performance

    Note:
        Only applies to CPython.
    """
    if platform.python_implementation() == "CPython":
        # allocs, g1, g2 = gc.get_threshold()
        gc.set_threshold(50_000, 500, 1000)
        logger.debug("Adjusted Python allocations to reduce GC runs")


def chunker(seq: Sequence[Any], n: int) -> Generator[Sequence[Any], None, None]:
    """Iterate a Sequence in Chunks

    Args:
        seq (Sequence[Any]): Sequence of values.
        n (int): Number of values per chunk.

    Yields:
        Sequence[Any]: Chunk of values with length <= n.
    """
    if n == 0:
        raise ValueError("n should be non-zero")
    if n < 0:
        raise ValueError("n should be positive")
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


def is_iterable(obj: Any) -> bool:
    """Check if an Object is Iterable

    Args:
        obj (Any): Object to check.

    Returns:
        bool: Whether the object is iterable.
    """
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def rename_key(
    obj: dict,
    src_key: str,
    dest_key: str,
    in_place: bool = False,
) -> dict | None:
    """Rename a Dictionary Key

    Args:
        obj (dict): Reference to the dictionary to modify.
        src (str): Name of the key to rename.
        dest (str): Name of the key to change to.
        in_place (bool, optional): Perform in-place using the provided reference. Defaults to False.

    Returns:
        dict | None: Copy of the dictionary if in_place is False, otherwise None.
    """
    if in_place:
        if src_key in obj:
            obj[dest_key] = obj.pop(src_key)
        return None
    else:
        obj_copy = copy.deepcopy(obj)
        rename_key(obj_copy, src_key, dest_key, in_place=True)
        return obj_copy


def unnest_key(obj: dict, *keys: str) -> Any:
    """Fetch a Value from a Deeply Nested Dictionary

    Args:
        obj (dict): Dictionary to recursively iterate.
        *keys (str): Ordered keys to fetch.

    Returns:
        Any: The result of the provided keys.
    """
    found = obj
    for key in keys:
        if key in found:
            found = found[key]
        else:
            return None
    return found
