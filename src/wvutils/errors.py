"""Custom Errors

This module contains custom errors that are used throughout the package.
"""

from cloudpickle import pickle
from rapidjson import JSONDecodeError as RapidJSONDecodeError

__all__ = [
    "HashEncodeError",
    "JSONDecodeError",
    "JSONDecodeError",
    "JSONEncodeError",
    "PickleDecodeError",
    "PickleEncodeError",
]


class JSONEncodeError(TypeError):
    pass


# JSONDecodeError = RapidJSONDecodeError
# OverflowError might need to be included, but excluding until that time comes.
class JSONDecodeError(TypeError, RapidJSONDecodeError):  # OverflowError):
    pass


class PickleEncodeError(TypeError, pickle.PicklingError):
    pass


class PickleDecodeError(TypeError, pickle.UnpicklingError):
    pass


class HashEncodeError(TypeError, ValueError, AttributeError):
    pass
