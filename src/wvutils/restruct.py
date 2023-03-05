"""Restructure Data

This module contains functions for restructuring data.

JSON

| Python                                     | JSON        |
| :----------------------------------------- | :---------- |
| dict                                       | object      |
| list, tuple                                | array       |
| str                                        | string      |
| int, float, int- & float-derived enums     | number      |
| True                                       | true        |
| False                                      | false       |
| None                                       | null        |

Hash

-   No content

Pickle

-   An important difference between cloudpickle and pickle is that cloudpickle can serialize a function or class by value, whereas pickle can only serialize it by reference.
    Serialization by reference treats functions and classes as attributes of modules, and pickles them through instructions that trigger the import of their module at load time.
    Serialization by reference is thus limited in that it assumes that the module containing the function or class is available/importable in the unpickling environment.
    This assumption breaks when pickling constructs defined in an interactive session, a case that is automatically detected by cloudpickle, that pickles such constructs by value.
"""

import collections
import logging
from collections.abc import Generator, Iterable
from hashlib import md5

import cloudpickle
import rapidjson

from wvutils.errors import (
    HashEncodeError,
    JSONDecodeError,
    JSONEncodeError,
    PickleDecodeError,
    PickleEncodeError,
)
from wvutils.typing import (
    FilePath,
    JSONEncodable,
    JSONEncoded,
    MD5Hashable,
    MD5Hashed,
    PickleSerializable,
    PickleSerialized,
)

from wvutils.path import resolve_path

__all__ = [
    "gen_hash",
    "json_dump",
    "json_dumps",
    "json_load",
    "json_loads",
    "jsonl_dump",
    "jsonl_dumps",
    "jsonl_loader",
    "pickle_dump",
    "pickle_dumps",
    "pickle_load",
    "pickle_loads",
    "squeegee_loader",
]

logger = logging.getLogger(__name__)


def json_dumps(obj: JSONEncodable) -> JSONEncoded:
    """Encode an Object as JSON

    Args:
        obj (JSONEncodable): Object to encode.

    Returns:
        JSONEncoded: Object encoded as JSON.

    Raises:
        JSONEncodeError: If the object could not be encoded.
    """
    try:
        return rapidjson.dumps(obj, default=str, number_mode=rapidjson.NM_NATIVE)
    except JSONEncodeError as err:
        raise err


def jsonl_dumps(objs: Iterable[JSONEncodable]) -> JSONEncoded:
    """Encode Objects as JSONL

    Args:
        objs (Iterable[JSONEncodable]): Objects to encode.

    Returns:
        JSONEncoded: Objects encoded as JSONL.

    Raises:
        JSONEncodeError: If the object could not be encoded.
    """
    return "\n".join(map(lambda line: json_dumps(line), objs))


def json_dump(file_path: str, obj: JSONEncodable) -> None:
    """Encode an Object as JSON and Write it to a File

    Args:
        file_path (str): Path of the file to open.
        obj (JSONEncodable): Object to encode.

    Raises:
        JSONEncodeError: If the object could not be encoded.
    """
    file_path = resolve_path(file_path)
    with open(file_path, mode="w", encoding="utf-8") as wf:
        try:
            rapidjson.dump(obj, wf, default=str, number_mode=rapidjson.NM_NATIVE)
        except JSONEncodeError as err:
            raise err


def jsonl_dump(file_path: str, objs: Iterable[JSONEncodable]) -> None:
    """Encode Objects as JSONL and Write them to a File

    Args:
        file_path (str): Path of the file to open.
        objs (Iterable[JSONEncodable]): Objects to encode.

    Raises:
        JSONEncodeError: If the object could not be encoded.
    """
    file_path = resolve_path(file_path)
    with open(file_path, mode="w", encoding="utf-8") as wf:
        wf.write(jsonl_dumps(objs))


def json_loads(encoded_obj: JSONEncoded) -> JSONEncodable:
    """Decode a JSON-Encoded Object

    Args:
        encoded_obj (JSONEncoded): Object to decode.

    Returns:
        JSONEncodable: Decoded object.

    Raises:
        JSONDecodeError: If the object could not be decoded.
    """
    try:
        return rapidjson.loads(encoded_obj, number_mode=rapidjson.NM_NATIVE)
    except JSONDecodeError as err:
        raise err


def json_load(file_path: FilePath) -> JSONEncodable:
    """Decode a File Containing a JSON-Encoded Object

    Args:
        file_path (FilePath): Path of the file to open.

    Returns:
        JSONEncodable: Decoded object.

    Raises:
        JSONDecodeError: If the file could not be decoded.
    """
    file_path = resolve_path(file_path)
    with open(file_path, mode="r", encoding="utf-8") as rf:
        try:
            return rapidjson.load(rf, number_mode=rapidjson.NM_NATIVE)
        except JSONDecodeError as err:
            raise err


def jsonl_loader(
    file_path: FilePath,
    allow_empty_lines: bool = True,
) -> Generator[JSONEncodable, None, None]:
    """Decode a File Containing JSON-Encoded Objects in JSONL

    Args:
        file_path (FilePath): Path of the file to open.
        allow_empty_lines (bool, optional): Whether to allow empty lines. Defaults to True.

    Yields:
        JSONEncodable: Decoded object.

    Raises:
        JSONDecodeError: If the line could not be decoded, or if an empty line was found and `allow_empty_lines` is False.
    """
    file_path = resolve_path(file_path)
    with open(file_path, mode="r", encoding="utf-8") as rf:
        for line in rf:
            # Remove trailing newline
            line = line[:-1]
            # Handle empty lines
            if not line:
                if allow_empty_lines:
                    continue
                else:
                    raise JSONDecodeError("Empty line found")
            yield json_loads(line)


def squeegee_loader(file_path: FilePath) -> Generator[JSONEncodable, None, None]:
    """Automatically Decode a File Containing JSON-Encoded Objects

    Supports multiple formats (JSON, JSONL, JSONL of JSONL, etc).

    Args:
        file_path (FilePath): Path of the file to open.

    Yields:
        JSONEncodable: Decoded object.

    Raises:
        JSONDecodeError: If the line could not be decoded.
    """
    file_path = resolve_path(file_path)

    # Try to decode as JSON standard
    try:
        decoded_obj = json_load(file_path)
    except JSONDecodeError:
        decoded_obj = None

    if decoded_obj is not None:
        # Recognized as JSON (JSON standard)
        if isinstance(decoded_obj, list):
            # List of objects (multiline)
            for single_content in decoded_obj:
                yield single_content
        elif isinstance(decoded_obj, dict):
            # Single object (multiline)
            yield decoded_obj
    else:
        # Recognized as JSONL (JSON line)
        for decoded_obj in jsonl_loader(file_path, allow_empty_lines=True):
            if isinstance(decoded_obj, dict):
                # Single object (single line)
                yield decoded_obj
            elif isinstance(decoded_obj, list):
                # List of objects (single line)
                for single_content in decoded_obj:
                    yield single_content


def gen_hash(obj: MD5Hashable) -> MD5Hashed | None:
    """Create an MD5 Hash from an JSONEncodable Object

    Args:
        obj (MD5Hashable): Object to hash.

    Returns:
        MD5Hashed | None: MD5 hash of the object or None if object was an empty iterable.

    Raises:
        HashEncodeError: If the object could not be encoded.
    """
    hashed_obj = None
    try:
        if isinstance(obj, bytes):
            # Already bytes
            obj_b = obj
        elif isinstance(obj, str):
            # Encode string
            obj_b = obj.encode("utf-8")
        elif isinstance(obj, (list, collections.deque)):
            # Encode list or deque as JSONL-encoded list
            # TODO: Could add support for tuple and set, and combine with list below since 'jsonl_dumps' accepts iterables.
            #       Worth noting that this may confuse the user, as hashing (0, 1, 2) or {0, 1, 2} or [0, 1, 2] would be effectively the same.
            obj_b = jsonl_dumps(obj).encode("utf-8")
        elif isinstance(obj, (dict, int, float, bool)):
            # Encode remaining built-ins as JSON
            obj_b = json_dumps(obj).encode("utf-8")
        # Hash if not empty iterable
        if obj_b is not None:
            hashed_obj = md5(obj_b).hexdigest()
    except HashEncodeError as err:
        raise err
    return hashed_obj


def pickle_dump(file_path: FilePath, obj: PickleSerializable) -> None:
    """Serialize an Object as a Pickle and Write it to a File

    Args:
        file_path (FilePath): Path of the file to write.
        obj (JSONEncodable): Object to serialize.

    Raises:
        PickleEncodeError: If the object could not be encoded.
    """
    with open(file_path, mode="wb") as wb:
        try:
            cloudpickle.dump(obj, wb)
        except PickleEncodeError as err:
            raise err


def pickle_dumps(obj: PickleSerializable) -> PickleSerialized:
    """Serialize an Object as a Pickle

    Args:
        obj (PickleSerializable): Object to serialize.

    Returns:
        PickleSerialized: Serialized object.

    Raises:
        PickleEncodeError: If the object could not be encoded.
    """
    try:
        return cloudpickle.dumps(obj)
    except PickleEncodeError as err:
        raise err


def pickle_load(file_path: FilePath) -> PickleSerializable:
    """Deserialize Pickle-Serialized Object from a File

    NOTE: Not safe for large files.

    Args:
        file_path (FilePath): Path of the file to open.

    Returns:
        PickleSerializable: Deserialized object.

    Raises:
        PickleDecodeError: If the object could not be decoded.
    """
    with open(file_path, mode="rb") as rb:
        try:
            return cloudpickle.load(rb)
        except PickleDecodeError as err:
            raise err


def pickle_loads(serialized_obj: PickleSerialized) -> PickleSerializable:
    """Deserialize Pickle-Serialized Object

    Args:
        serialized_obj (PickleSerialized): Object to deserialize.

    Returns:
        PickleSerializable: Deserialized object.

    Raises:
        PickleDecodeError: If the object could not be decoded.
    """
    try:
        return cloudpickle.loads(serialized_obj)
    except PickleDecodeError as err:
        raise err
