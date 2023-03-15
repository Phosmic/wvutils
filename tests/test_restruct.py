import json
import os
import pathlib
import tempfile
import unittest
from io import BytesIO

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
    JSONEncodable,
    MD5Hashable,
    PickleSerializable,
)

from wvutils.restruct import (
    gen_hash,
    json_dump,
    json_dumps,
    json_load,
    json_loads,
    jsonl_dump,
    jsonl_dumps,
    jsonl_loader,
    pickle_dump,
    pickle_dumps,
    pickle_load,
    pickle_loads,
    squeegee_loader,
)


class TestJSONDumps(unittest.TestCase):
    def test_str(self):
        self.assertEqual(json_dumps("test"), '"test"')

    def test_int(self):
        self.assertEqual(json_dumps(123), "123")
        self.assertEqual(json_dumps(0), "0")
        self.assertEqual(json_dumps(-123), "-123")

    def test_float(self):
        self.assertEqual(json_dumps(1.23), "1.23")
        self.assertEqual(json_dumps(0.0), "0.0")
        self.assertEqual(json_dumps(-1.23), "-1.23")

    def test_complex(self):
        self.assertEqual(json_dumps(1.23 + 4.56j), '"(1.23+4.56j)"')
        self.assertEqual(json_dumps(0.0 + 0.0j), '"0j"')
        self.assertEqual(json_dumps(-1.23 - 4.56j), '"(-1.23-4.56j)"')

    def test_bool(self):
        self.assertEqual(json_dumps(True), "true")
        self.assertEqual(json_dumps(False), "false")

    def test_set_empty(self):
        self.assertEqual(json_dumps(set()), '"set()"')

    def test_set_of_int(self):
        self.assertEqual(json_dumps({0, 1, 2}), '"{0, 1, 2}"')

    def test_tuple_empty(self):
        self.assertEqual(json_dumps(tuple()), "[]")

    def test_tuple_of_int(self):
        self.assertEqual(json_dumps((1, 2, 3)), "[1,2,3]")

    def test_list_empty(self):
        self.assertEqual(json_dumps([]), "[]")

    def test_list_of_int(self):
        self.assertEqual(json_dumps([1, 2, 3]), "[1,2,3]")

    def test_dict_empty(self):
        self.assertEqual(json_dumps({}), "{}")

    def test_dict_of_int(self):
        self.assertEqual(json_dumps({"a": 1, "b": 2}), '{"a":1,"b":2}')

    def test_dict_of_int_by_int(self):
        self.assertEqual(json_dumps({1: "a", 2: "b"}), "\"{1: 'a', 2: 'b'}\"")

    def test_dict_of_int_by_float(self):
        self.assertEqual(json_dumps({1.0: "a", 2.0: "b"}), "\"{1.0: 'a', 2.0: 'b'}\"")

    def test_dict_of_mixed(self):
        expected = ",".join(
            (
                '{"a":1',
                '"b":2.0',
                '"c":"{1, 2, 3}"',
                '"d":[4,5,6]',
                '"e":[7,8,9]',
                '"f":{"g":10,"h":11}',
                '"j":{"k":"l","m":"n"}',
                '"o":true',
                '"p":false',
                '"q":null',
                '"r":"test"',
                '"s":"test"}',
            )
        )
        actual = json_dumps(
            {
                "a": 1,
                "b": 2.0,
                "c": {1, 2, 3},
                "d": (4, 5, 6),
                "e": [7, 8, 9],
                "f": {"g": 10, "h": 11},
                "j": {"k": "l", "m": "n"},
                "o": True,
                "p": False,
                "q": None,
                "r": b"test",
                "s": bytearray(b"test"),
            }
        )
        self.assertEqual(expected, actual)

    def test_none(self):
        self.assertEqual(json_dumps(None), "null")

    def test_bytes(self):
        self.assertEqual(json_dumps(b"test"), '"test"')

    def test_bytearray(self):
        self.assertEqual(json_dumps(bytearray(b"test")), '"test"')

    def test_inf_raises(self):
        with self.assertRaises(ValueError):
            json_dumps(float("inf"))

        with self.assertRaises(ValueError):
            json_dumps(float("-inf"))

    def test_nan_raises(self):
        with self.assertRaises(ValueError):
            json_dumps(float("nan"))

        with self.assertRaises(ValueError):
            json_dumps(float("-nan"))


class TestJSONDump(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.NamedTemporaryFile(mode="w+t", delete=False)

    def tearDown(self):
        self.temp.close()
        os.remove(self.temp.name)

    def test_str(self):
        json_dump(self.temp.name, "test")
        self.temp.seek(0)
        self.assertEqual(self.temp.read(), '"test"')

    def test_int(self):
        json_dump(self.temp.name, 123)
        self.temp.seek(0)
        self.assertEqual(self.temp.read(), "123")

    def test_float(self):
        json_dump(self.temp.name, 1.23)
        self.temp.seek(0)
        self.assertEqual(self.temp.read(), "1.23")

    def test_complex(self):
        json_dump(self.temp.name, 1.23 + 4.56j)
        self.temp.seek(0)
        self.assertEqual(self.temp.read(), '"(1.23+4.56j)"')

    def test_bool(self):
        json_dump(self.temp.name, True)
        self.temp.seek(0)
        self.assertEqual(self.temp.read(), "true")

    def test_set_empty(self):
        json_dump(self.temp.name, set())
        self.temp.seek(0)
        self.assertEqual(self.temp.read(), '"set()"')

    def test_set_of_int(self):
        json_dump(self.temp.name, {0, 1, 2})
        self.temp.seek(0)
        self.assertEqual(self.temp.read(), '"{0, 1, 2}"')

    def test_tuple_empty(self):
        json_dump(self.temp.name, tuple())
        self.temp.seek(0)
        self.assertEqual(self.temp.read(), "[]")

    def test_tuple_of_int(self):
        json_dump(self.temp.name, (1, 2, 3))
        self.temp.seek(0)
        self.assertEqual(self.temp.read(), "[1,2,3]")

    def test_list_empty(self):
        json_dump(self.temp.name, [])
        self.temp.seek(0)
        self.assertEqual(self.temp.read(), "[]")

    def test_list_of_int(self):
        json_dump(self.temp.name, [1, 2, 3])
        self.temp.seek(0)
        self.assertEqual(self.temp.read(), "[1,2,3]")

    def test_dict_empty(self):
        json_dump(self.temp.name, {})
        self.temp.seek(0)
        self.assertEqual(self.temp.read(), "{}")

    def test_dict_of_int(self):
        json_dump(self.temp.name, {"a": 1, "b": 2})
        self.temp.seek(0)
        self.assertEqual(self.temp.read(), '{"a":1,"b":2}')

    def test_dict_of_int_by_int(self):
        json_dump(self.temp.name, {1: "a", 2: "b"})
        self.temp.seek(0)
        self.assertEqual(self.temp.read(), "\"{1: 'a', 2: 'b'}\"")

    def test_dict_of_int_by_float(self):
        json_dump(self.temp.name, {1.0: "a", 2.0: "b"})
        self.temp.seek(0)
        self.assertEqual(self.temp.read(), "\"{1.0: 'a', 2.0: 'b'}\"")

    def test_none(self):
        json_dump(self.temp.name, None)
        self.temp.seek(0)
        self.assertEqual(self.temp.read(), "null")

    def test_bytes(self):
        json_dump(self.temp.name, b"test")
        self.temp.seek(0)
        self.assertEqual(self.temp.read(), '"test"')

    def test_bytearray(self):
        json_dump(self.temp.name, bytearray(b"test"))
        self.temp.seek(0)
        self.assertEqual(self.temp.read(), '"test"')

    def test_inf_raises(self):
        with self.assertRaises(ValueError):
            json_dump(self.temp.name, float("inf"))

    def test_nan_raises(self):
        with self.assertRaises(ValueError):
            json_dump(self.temp.name, float("nan"))


class TestJSONLDumps(unittest.TestCase):
    def test_str(self):
        objs = ["this", "is", "a", "test"]
        expected = "\n".join(('"this"', '"is"', '"a"', '"test"'))
        actual = jsonl_dumps(objs)
        self.assertEqual(actual, expected)
