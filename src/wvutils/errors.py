"""Custom errors.

This module contains custom exceptions that are used throughout the package.
"""

from cloudpickle import pickle
from rapidjson import JSONDecodeError as RapidJSONDecodeError

__all__ = [
    "HashEncodeError",
    "JSONDecodeError",
    "JSONEncodeError",
    "PickleDecodeError",
    "PickleEncodeError",
]


class JSONEncodeError(TypeError):
    """Raised when JSON encoding fails."""


# JSONDecodeError = RapidJSONDecodeError
# OverflowError might need to be included, but excluding until that time comes.
class JSONDecodeError(TypeError, RapidJSONDecodeError):  # OverflowError):
    """Raised when JSON decoding fails."""


class PickleEncodeError(TypeError, pickle.PicklingError):
    """Raised when pickling fails."""


class PickleDecodeError(TypeError, pickle.UnpicklingError):
    """Raised when unpickling fails."""


class HashEncodeError(TypeError, ValueError, AttributeError):
    """Raised when hashing fails."""
