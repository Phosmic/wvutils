# WVUtils

[WVUtils](https://github.com/Phosmic/wvutils) is a collection of utilities that are shared across multiple [Phosmic](https://phosmic.com) projects.

---

## Requirements:

**WVUtils** requires Python 3.10 or higher and is platform independent.

## Issue reporting

If you discover an issue with WVUtils, please report it at [https://github.com/Phosmic/wvutils/issues](https://github.com/Phosmic/wvutils/issues).

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.

---

-   [Requirements](#requirements)
-   [Installing](#installing)
-   [Library](#library)

## Installing

Most stable version from [**PyPi**](https://pypi.org/project/wvutils/):

[![PyPI](https://img.shields.io/pypi/v/wvutils?style=flat-square)](https://pypi.org/project/wvutils/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/wvutils?style=flat-square)](https://pypi.org/project/wvutils/)
[![PyPI - License](https://img.shields.io/pypi/l/wvutils?style=flat-square)](https://pypi.org/project/wvutils/)

```bash
python3 -m pip install wvutils
```

Development version from [**GitHub**](https://github.com/Phosmic/wvutils):


![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/Phosmic/wvutils/ubuntu.yml?style=flat-square)
![Codecov](https://img.shields.io/codecov/c/github/Phosmic/wvutils/master?flag=unittests&style=flat-square&token=XMJZIW8ZL3)
![GitHub](https://img.shields.io/github/license/Phosmic/wvutils?style=flat-square)


```bash
git clone git+https://github.com/Phosmic/wvutils.git
cd wvutils
python3 -m pip install -e .
```

---

## Library

<a id="wvutils.aws"></a>

# `wvutils.aws`

Utilities for interacting with AWS services.

This module provides utilities for interacting with AWS services.

<a id="wvutils.aws.get_boto3_session"></a>

#### `get_boto3_session`

```python
def get_boto3_session(region_name: AWSRegion) -> Session
```

Get the globally shared Boto3 session for a region (thread-safe).

**Todo**:

  * Add support for other session parameters.

**Arguments**:

- `region_name` _AWSRegion_ - Region name for the session.

**Returns**:

- _Session_ - Boto3 session.

<a id="wvutils.aws.clear_boto3_sessions"></a>

#### `clear_boto3_sessions`

```python
def clear_boto3_sessions()
```

Clear all globally shared Boto3 sessions (thread-safe).

**Returns**:

- _bool_ - Whether any sessions were cleared.

<a id="wvutils.aws.boto3_client_ctx"></a>

#### `boto3_client_ctx`

```python
@contextmanager
def boto3_client_ctx(service_name: str, region_name: AWSRegion)
```

Context manager for a Boto3 client (thread-safe).

**Todo**:

  * Add support for other session parameters.

**Arguments**:

- `service_name` _str_ - Name of the service.
- `region_name` _AWSRegion_ - Region name for the service.

**Yields**:

- _Any_ - Boto3 client.

**Raises**:

- `ClientError` - If an error occurs.

<a id="wvutils.aws.parse_s3_uri"></a>

#### `parse_s3_uri`

```python
def parse_s3_uri(s3_uri: str) -> tuple[str, str]
```

Parse the bucket name and path from a S3 URI.

**Arguments**:

- `s3_uri` _str_ - S3 URI to parse.

**Returns**:

- _tuple[str, str]_ - Bucket name and path.

<a id="wvutils.aws.download_from_s3"></a>

#### `download_from_s3`

```python
def download_from_s3(file_path: FilePath,
                     bucket_name: str,
                     bucket_path: str,
                     region_name: AWSRegion,
                     overwrite: bool = True) -> None
```

Download a file from S3.

**Arguments**:

- `file_path` _FilePath_ - Output path to use while downloading the file.
- `bucket_name` _str_ - Name of the S3 bucket containing the file.
- `bucket_path` _str_ - Path of the S3 bucket containing the file.
- `region_name` _AWSRegion_ - Region name for S3.
- `overwrite` _bool_ - Overwrite file on disk if already exists. Defaults to True.

**Raises**:

- `FileExistsError` - If the file already exists and overwrite is False.

<a id="wvutils.aws.upload_file_to_s3"></a>

#### `upload_file_to_s3`

```python
def upload_file_to_s3(file_path: FilePath, bucket_name: str, bucket_path: str,
                      region_name: AWSRegion) -> None
```

Upload a file to S3.

**Arguments**:

- `file_path` _FilePath_ - Path of the file to upload.
- `bucket_name` _str_ - Name of the S3 bucket to upload the file to.
- `bucket_path` _str_ - Path in the S3 bucket to upload the file to.
- `region_name` _AWSRegion_ - Region name for S3.

**Raises**:

- `FileNotFoundError` - If the file does not exist.

<a id="wvutils.aws.upload_bytes_to_s3"></a>

#### `upload_bytes_to_s3`

```python
def upload_bytes_to_s3(raw_b: bytes, bucket_name: str, bucket_path: str,
                       region_name: AWSRegion) -> None
```

Write bytes to a file in S3.

**Arguments**:

- `raw_b` _bytes_ - Bytes of the file to be written.
- `bucket_name` _str_ - Name of the S3 bucket to upload the file to.
- `bucket_path` _str_ - Path in the S3 bucket to upload the file to.
- `region_name` _AWSRegion_ - Region name for S3.

**Raises**:

- `TypeError` - If `raw_b` is not bytes.

<a id="wvutils.aws.secrets_fetch"></a>

#### `secrets_fetch`

```python
def secrets_fetch(
        secret_name: str,
        region_name: AWSRegion) -> str | int | float | list | dict | None
```

Request and decode a secret from Secrets.

**Arguments**:

- `secret_name` _str_ - Secret name to use.
- `region_name` _AWSRegion_ - Region name for Secrets.

**Returns**:

- _str | int | float | list | dict | None_ - Secret string.

<a id="wvutils.aws.athena_execute_query"></a>

#### `athena_execute_query`

```python
def athena_execute_query(query: str, database_name: str,
                         region_name: AWSRegion) -> str | None
```

Execute a query in Athena.

**Arguments**:

- `query` _str_ - Query to execute.
- `database_name` _str_ - Name of database to execute the query against.
- `region_name` _AWSRegion_ - Region name for Athena.

**Returns**:

- _str | None_ - Query execution ID of the query.

<a id="wvutils.aws.athena_retrieve_query"></a>

#### `athena_retrieve_query`

```python
def athena_retrieve_query(qeid: str, database_name: str,
                          region_name: AWSRegion) -> str | None
```

Retrieve the S3 URI for results of a query in Athena.

**Arguments**:

- `qeid` _str_ - Query execution ID of the query to fetch.
- `database_name` _str_ - Name of the database the query is running against (for debugging).
- `region_name` _AWSRegion_ - Region name for Athena.

**Returns**:

- _str | None_ - Current status of the query, or S3 URI where results are stored.

**Raises**:

- `ValueError` - If the query execution ID is unknown or missing.

<a id="wvutils.aws.athena_stop_query"></a>

#### `athena_stop_query`

```python
def athena_stop_query(qeid: str, region_name: AWSRegion) -> None
```

Stop the execution of a query in Athena.

**Arguments**:

- `qeid` _str_ - Query execution ID of the query to stop.
- `region_name` _AWSRegion_ - Region name for Athena.

<a id="wvutils.errors"></a>

# `wvutils.errors`

Custom errors.

This module contains custom exceptions that are used throughout the package.

<a id="wvutils.errors.JSONEncodeError"></a>

## `JSONEncodeError` Objects

```python
class JSONEncodeError(TypeError)
```

Raised when JSON encoding fails.

<a id="wvutils.errors.JSONDecodeError"></a>

## `JSONDecodeError` Objects

```python
class JSONDecodeError(TypeError, RapidJSONDecodeError)
```

Raised when JSON decoding fails.

<a id="wvutils.errors.PickleEncodeError"></a>

## `PickleEncodeError` Objects

```python
class PickleEncodeError(TypeError, pickle.PicklingError)
```

Raised when pickling fails.

<a id="wvutils.errors.PickleDecodeError"></a>

## `PickleDecodeError` Objects

```python
class PickleDecodeError(TypeError, pickle.UnpicklingError)
```

Raised when unpickling fails.

<a id="wvutils.errors.HashEncodeError"></a>

## `HashEncodeError` Objects

```python
class HashEncodeError(TypeError, ValueError, AttributeError)
```

Raised when hashing fails.

<a id="wvutils.path"></a>

# `wvutils.path`

Utilities for working with paths.

This module provides utilities for working with paths.

<a id="wvutils.path.is_pathlike"></a>

#### `is_pathlike`

```python
def is_pathlike(potential_path: Any) -> bool
```

Check if an object is path-like.

**Arguments**:

- `potential_path` _Any_ - Object to check.

**Returns**:

- _bool_ - True if the object is path-like, otherwise False.

<a id="wvutils.path.stringify_path"></a>

#### `stringify_path`

```python
def stringify_path(file_path: FilePath) -> str
```

Stringify a path-like object.

**Arguments**:

- `file_path` _FilePath_ - Path-like object to stringify.

**Returns**:

- _str_ - Path-like object as a string.

<a id="wvutils.path.ensure_abspath"></a>

#### `ensure_abspath`

```python
def ensure_abspath(file_path: str) -> str
```

Make a path absolute if it is not already.

**Arguments**:

- `file_path` _str_ - Path to ensure is absolute.

**Returns**:

- _str_ - Absolute path.

<a id="wvutils.path.resolve_path"></a>

#### `resolve_path`

```python
def resolve_path(file_path: FilePath) -> str
```

Stringify and resolve a path-like object.

**Arguments**:

- `file_path` _FilePath_ - Path-like object to resolve.

**Returns**:

- _str_ - Absolute path of the path-like object as a string.

<a id="wvutils.path.xdg_cache_path"></a>

#### `xdg_cache_path`

```python
def xdg_cache_path() -> str
```

Base directory to store user-specific non-essential data files.

This should be '${HOME}/.cache', but the 'HOME' environment variable may not exist on non-POSIX-compliant systems.
On POSIX-compliant systems, the XDG base directory specification is followed exactly since '~' expands to '$HOME' if it is present.

**Returns**:

- _str_ - Path for XDG cache.

<a id="wvutils.proxies"></a>

# `wvutils.proxies`

Utilities for working with proxies.

This module provides utilities for working with proxies.

<a id="wvutils.proxies.ProxyManager"></a>

## `ProxyManager` Objects

```python
class ProxyManager()
```

Manages a list of proxies.

This class manages a list of proxies, allowing for randomization, re-use, etc.

<a id="wvutils.proxies.ProxyManager.add_proxies"></a>

#### `ProxyManager.add_proxies`

```python
def add_proxies(proxies: list[str], include_duplicates: bool = False) -> None
```

Add additional proxy addresses.

**Arguments**:

- `proxies` _list[str]_ - List of proxy addresses.

<a id="wvutils.proxies.ProxyManager.set_proxies"></a>

#### `ProxyManager.set_proxies`

```python
def set_proxies(proxies: list[str]) -> None
```

Set the proxy addresses.

Note: This will clear all existing proxies.

**Arguments**:

- `proxies` _list[str]_ - List of proxy addresses.

<a id="wvutils.proxies.ProxyManager.can_cycle"></a>

#### `ProxyManager.can_cycle`

```python
@property
def can_cycle() -> bool
```

Check if can cycle to the next proxy address.

**Returns**:

- _bool_ - True if can cycle, False otherwise.

<a id="wvutils.proxies.ProxyManager.cycle"></a>

#### `ProxyManager.cycle`

```python
def cycle() -> None
```

Attempt to cycle to the next proxy address.

<a id="wvutils.proxies.ProxyManager.proxy"></a>

#### `ProxyManager.proxy`

```python
@property
def proxy() -> str | None
```

Current proxy address.

**Returns**:

- _str | None_ - Current proxy, or None if no proxies.

<a id="wvutils.proxies.https_to_http"></a>

#### `https_to_http`

```python
def https_to_http(address: str) -> str
```

Convert a HTTPS proxy address to HTTP.

**Arguments**:

- `address` _str_ - HTTPS proxy address.

**Returns**:

- _str_ - HTTP proxy address.

<a id="wvutils.proxies.prepare_http_proxy_for_requests"></a>

#### `prepare_http_proxy_for_requests`

```python
def prepare_http_proxy_for_requests(address: str) -> dict[str, str]
```

Prepare a HTTP(S) proxy address for use with the 'requests' library.

**Arguments**:

- `address` _str_ - HTTP(S) proxy address.

**Returns**:

- _dict[str, str]_ - Dictionary of HTTP and HTTPS proxy addresses.

**Raises**:

- `ValueError` - If the address does not start with 'http(s)://'.

<a id="wvutils.args"></a>

# `wvutils.args`

Utilities for parsing arguments from the command line.

This module provides utilities for parsing arguments from the command line.

<a id="wvutils.args.nonempty_string"></a>

#### `nonempty_string`

```python
def nonempty_string(name: str) -> Callable
```

Ensure a string is non-empty.

Example Usage:

```python
subparser.add_argument(
    "hashtag",
    type=nonempty_string("hashtag"),
    help="A hashtag (without #)",
)
```

**Arguments**:

- `name` _str_ - Name of the function, used for debugging.

**Returns**:

- _Callable_ - The decorated function.

<a id="wvutils.args.safechars_string"></a>

#### `safechars_string`

```python
def safechars_string(
    name: str,
    allowed_chars: str | set[str] | tuple[str] | list[str] | None = None
) -> Callable
```

Ensure a string contains only safe characters.

Example Usage:

```python
subparser.add_argument(
    "--session-key",
    type=safechars_string,
    help="Key to share a single token across processes",
)
```

**Arguments**:

- `name` _str_ - Name of the function, used for debugging.
- `allowed_chars` _str | set[str] | tuple[str] | list[str] | None, optional_ - Custom characters used to validate the function name. Defaults to None.

**Returns**:

- _Callable_ - The decorated function.

<a id="wvutils.general"></a>

# `wvutils.general`

General utilities for working with Python.

This module provides general utilities for working with Python.

<a id="wvutils.general.count_lines_in_file"></a>

#### `count_lines_in_file`

```python
def count_lines_in_file(file_path: FilePath) -> int
```

Count the number of lines in a file.

**Notes**:

  All files have at least 1 line (# of lines = # of newlines + 1).

**Arguments**:

- `file_path` _FilePath_ - Path of the file to count lines in.

**Returns**:

- _int_ - Total number of lines in the file.

<a id="wvutils.general.sys_set_recursion_limit"></a>

#### `sys_set_recursion_limit`

```python
def sys_set_recursion_limit() -> None
```

Raise recursion limit to allow for more recurse.

<a id="wvutils.general.gc_set_threshold"></a>

#### `gc_set_threshold`

```python
def gc_set_threshold() -> None
```

Reduce Number of GC Runs to Improve Performance

**Notes**:

  Only applies to CPython.

<a id="wvutils.general.chunker"></a>

#### `chunker`

```python
def chunker(seq: Sequence[Any],
            n: int) -> Generator[Sequence[Any], None, None]
```

Iterate a sequence in size `n` chunks.

**Arguments**:

- `seq` _Sequence[Any]_ - Sequence of values.
- `n` _int_ - Number of values per chunk.

**Yields**:

- _Sequence[Any]_ - Chunk of values with length <= n.

**Raises**:

- `ValueError` - If `n` is 0 or negative.

<a id="wvutils.general.is_iterable"></a>

#### `is_iterable`

```python
def is_iterable(obj: Any) -> bool
```

Check if an object is iterable.

**Arguments**:

- `obj` _Any_ - Object to check.

**Returns**:

- _bool_ - Whether the object is iterable.

<a id="wvutils.general.rename_key"></a>

#### `rename_key`

```python
def rename_key(obj: dict,
               src_key: str,
               dest_key: str,
               in_place: bool = False) -> dict | None
```

Rename a dictionary key.

**Arguments**:

- `obj` _dict_ - Reference to the dictionary to modify.
- `src` _str_ - Name of the key to rename.
- `dest` _str_ - Name of the key to change to.
- `in_place` _bool, optional_ - Perform in-place using the provided reference. Defaults to False.

**Returns**:

- _dict | None_ - Copy of the dictionary if in_place is False, otherwise None.

<a id="wvutils.general.unnest_key"></a>

#### `unnest_key`

```python
def unnest_key(obj: dict, *keys: str) -> Any | None
```

Fetch a value from a deeply nested dictionary.

**Arguments**:

- `obj` _dict_ - Dictionary to recursively iterate.
- `*keys` _str_ - Ordered keys to fetch.

**Returns**:

- _Any | None_ - The result of the provided keys, or None if any key is not found.

<a id="wvutils.restruct"></a>

# `wvutils.restruct`

Utilities for restructuring data.

This module provides utilities for restructuring data, including serialization and hashing.

JSON

| Python                                 | JSON   |
| :------------------------------------- | :----- |
| dict                                   | object |
| list, tuple                            | array  |
| str                                    | string |
| int, float, int- & float-derived enums | number |
| True                                   | true   |
| False                                  | false  |
| None                                   | null   |

Hash

> No content.

Pickle

> An important difference between cloudpickle and pickle is that cloudpickle can serialize a function or class by value, whereas pickle can only serialize it by reference.
> Serialization by reference treats functions and classes as attributes of modules, and pickles them through instructions that trigger the import of their module at load time.
> Serialization by reference is thus limited in that it assumes that the module containing the function or class is available/importable in the unpickling environment.
> This assumption breaks when pickling constructs defined in an interactive session, a case that is automatically detected by cloudpickle, that pickles such constructs by value.

Read more: https://github.com/cloudpipe/cloudpickle/blob/master/README.md#overriding-pickles-serialization-mechanism-for-importable-constructs

<a id="wvutils.restruct.json_dumps"></a>

#### `json_dumps`

```python
def json_dumps(obj: JSONEncodable) -> str
```

Encode an object as JSON.

**Arguments**:

- `obj` _JSONEncodable_ - Object to encode.

**Returns**:

- _str_ - Object encoded as JSON.

**Raises**:

- `JSONEncodeError` - If the object could not be encoded.

<a id="wvutils.restruct.jsonl_dumps"></a>

#### `jsonl_dumps`

```python
def jsonl_dumps(objs: Iterable[JSONEncodable]) -> str
```

Encode objects as JSONL.

**Arguments**:

- `objs` _Iterable[JSONEncodable]_ - Objects to encode.

**Returns**:

- _str_ - Objects encoded as JSONL.

**Raises**:

- `JSONEncodeError` - If the object could not be encoded.

<a id="wvutils.restruct.json_dump"></a>

#### `json_dump`

```python
def json_dump(file_path: str, obj: JSONEncodable) -> None
```

Encode an object as JSON and write it to a file.

**Arguments**:

- `file_path` _str_ - Path of the file to open.
- `obj` _JSONEncodable_ - Object to encode.

**Raises**:

- `JSONEncodeError` - If the object could not be encoded.

<a id="wvutils.restruct.jsonl_dump"></a>

#### `jsonl_dump`

```python
def jsonl_dump(file_path: str, objs: Iterable[JSONEncodable]) -> None
```

Encode objects as JSONL and write them to a file.

**Arguments**:

- `file_path` _str_ - Path of the file to open.
- `objs` _Iterable[JSONEncodable]_ - Objects to encode.

**Raises**:

- `JSONEncodeError` - If the object could not be encoded.

<a id="wvutils.restruct.json_loads"></a>

#### `json_loads`

```python
def json_loads(encoded_obj: str) -> JSONEncodable
```

Decode a JSON-encoded object.

**Arguments**:

- `encoded_obj` _str_ - Object to decode.

**Returns**:

- _JSONEncodable_ - Decoded object.

**Raises**:

- `JSONDecodeError` - If the object could not be decoded.

<a id="wvutils.restruct.json_load"></a>

#### `json_load`

```python
def json_load(file_path: FilePath) -> JSONEncodable
```

Decode a file containing a JSON-encoded object.

**Arguments**:

- `file_path` _FilePath_ - Path of the file to open.

**Returns**:

- _JSONEncodable_ - Decoded object.

**Raises**:

- `JSONDecodeError` - If the file could not be decoded.

<a id="wvutils.restruct.jsonl_loader"></a>

#### `jsonl_loader`

```python
def jsonl_loader(
        file_path: FilePath,
        *,
        allow_empty_lines: bool = True
) -> Generator[JSONEncodable, None, None]
```

Decode a file containing JSON-encoded objects, one per line.

**Arguments**:

- `file_path` _FilePath_ - Path of the file to open.
- `allow_empty_lines` _bool, optional_ - Whether to allow empty lines. Defaults to True.

**Yields**:

- _JSONEncodable_ - Decoded object.

**Raises**:

- `JSONDecodeError` - If the line could not be decoded, or if an empty line was found and `allow_empty_lines` is False.

<a id="wvutils.restruct.squeegee_loader"></a>

#### `squeegee_loader`

```python
def squeegee_loader(
        file_path: FilePath) -> Generator[JSONEncodable, None, None]
```

Automatically decode a file containing JSON-encoded objects.

Supports multiple formats (JSON, JSONL, JSONL of JSONL, etc).

**Arguments**:

- `file_path` _FilePath_ - Path of the file to open.

**Yields**:

- _JSONEncodable_ - Decoded object.

**Raises**:

- `JSONDecodeError` - If the line could not be decoded.

<a id="wvutils.restruct.gen_hash"></a>

#### `gen_hash`

```python
def gen_hash(obj: MD5Hashable) -> str | None
```

Create an MD5 hash from a hashable object.

Note: Tuples and sets are not hashable, so they are converted to lists.

**Arguments**:

- `obj` _MD5Hashable_ - Object to hash.

**Returns**:

- _str | None_ - MD5 hash of the object, or None if object was an empty iterable.

**Raises**:

- `HashEncodeError` - If the object could not be encoded.

<a id="wvutils.restruct.pickle_dump"></a>

#### `pickle_dump`

```python
def pickle_dump(file_path: FilePath, obj: PickleSerializable) -> None
```

Serialize an object as a pickle and write it to a file.

**Arguments**:

- `file_path` _FilePath_ - Path of the file to write.
- `obj` _JSONEncodable_ - Object to serialize.

**Raises**:

- `PickleEncodeError` - If the object could not be encoded.

<a id="wvutils.restruct.pickle_dumps"></a>

#### `pickle_dumps`

```python
def pickle_dumps(obj: PickleSerializable) -> bytes
```

Serialize an object as a pickle.

**Arguments**:

- `obj` _PickleSerializable_ - Object to serialize.

**Returns**:

- _bytes_ - Serialized object.

**Raises**:

- `PickleEncodeError` - If the object could not be encoded.

<a id="wvutils.restruct.pickle_load"></a>

#### `pickle_load`

```python
def pickle_load(file_path: FilePath) -> PickleSerializable
```

Deserialize a pickle-serialized object from a file.

Note: Not safe for large files.

**Arguments**:

- `file_path` _FilePath_ - Path of the file to open.

**Returns**:

- _PickleSerializable_ - Deserialized object.

**Raises**:

- `PickleDecodeError` - If the object could not be decoded.

<a id="wvutils.restruct.pickle_loads"></a>

#### `pickle_loads`

```python
def pickle_loads(serialized_obj: bytes) -> PickleSerializable
```

Deserialize a pickle-serialized object.

**Arguments**:

- `serialized_obj` _bytes_ - Object to deserialize.

**Returns**:

- _PickleSerializable_ - Deserialized object.

**Raises**:

- `PickleDecodeError` - If the object could not be decoded.


---

