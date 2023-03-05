import gc
import sys
import tempfile
import unittest

from wvutils.utils import (
    chunker,
    count_lines_in_file,
    gc_set_threshold,
    is_iterable,
    rename_key,
    sys_set_recursion_limit,
    unnest_key,
)


class TestCountLinesInFile(unittest.TestCase):
    def test_empty_file(self):
        with tempfile.NamedTemporaryFile() as fp:
            self.assertEqual(count_lines_in_file(fp.name), 1)

    def test_single_line_file(self):
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(b"This is a single line")
            fp.seek(0)
            self.assertEqual(count_lines_in_file(fp.name), 1)

    def test_multiple_lines_file(self):
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(
                b"This is the first line\nThis is the second line\nThis is the third line"
            )
            fp.seek(0)
            self.assertEqual(count_lines_in_file(fp.name), 3)

    def test_file_with_newline_at_end(self):
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(
                b"This is the first line\nThis is the second line\nThis is the third line\n"
            )
            fp.seek(0)
            self.assertEqual(count_lines_in_file(fp.name), 4)


class TestSysSetRecursionLimit(unittest.TestCase):
    def test_recursion_limit(self):
        prev_limit = sys.getrecursionlimit()
        sys_set_recursion_limit()
        self.assertEqual(sys.getrecursionlimit(), 10000)
        sys.setrecursionlimit(prev_limit)


class TestGCSetThreshold(unittest.TestCase):
    def test_gc_threshold(self):
        prev_threshold = gc.get_threshold()
        gc_set_threshold()
        self.assertEqual(gc.get_threshold(), (50000, 500, 1000))
        gc.set_threshold(*prev_threshold)


class TestChunker(unittest.TestCase):
    def test_empty_sequence(self):
        self.assertEqual(list(chunker([], 2)), [])

    def test_n_greater_than_sequence_length(self):
        self.assertEqual(list(chunker([1, 2, 3], 4)), [[1, 2, 3]])

    def test_n_equal_to_sequence_length(self):
        self.assertEqual(list(chunker([1, 2, 3], 3)), [[1, 2, 3]])

    def test_n_less_than_sequence_length(self):
        self.assertEqual(list(chunker([1, 2, 3, 4, 5], 2)), [[1, 2], [3, 4], [5]])

    def test_n_is_zero(self):
        with self.assertRaises(ValueError):
            list(chunker([1, 2, 3], 0))

    def test_n_is_negative(self):
        with self.assertRaises(ValueError):
            list(chunker([1, 2, 3], -1))


class TestIsIterable(unittest.TestCase):
    def test_string(self):
        self.assertTrue(is_iterable("hello world"))

    def test_list(self):
        self.assertTrue(is_iterable([1, 2, 3]))

    def test_tuple(self):
        self.assertTrue(is_iterable((1, 2, 3)))

    def test_set(self):
        self.assertTrue(is_iterable({1, 2, 3}))

    def test_dict(self):
        self.assertTrue(is_iterable({"a": 1, "b": 2, "c": 3}))

    def test_int(self):
        self.assertFalse(is_iterable(1))

    def test_float(self):
        self.assertFalse(is_iterable(1.0))

    def test_None(self):
        self.assertFalse(is_iterable(None))

    def test_bool(self):
        self.assertFalse(is_iterable(True))

    def test_custom_iterable(self):
        class CustomIterable:
            def __init__(self, data: list):
                self.data = data
                self.index = 0

            def __iter__(self):
                return self

            def __next__(self):
                if self.index >= len(self.data):
                    raise StopIteration
                result = self.data[self.index]
                self.index += 1
                return result

        custom_iterable = CustomIterable([1, 2, 3])
        self.assertTrue(is_iterable(custom_iterable))


class TestRenameKey(unittest.TestCase):
    def test_rename_key_with_different_types(self):
        test_cases = [
            (
                {"int_key": 1},
                "int_key",
                "new_int_key",
                {"new_int_key": 1},
            ),
            (
                {"str_key": "test_str"},
                "str_key",
                "new_str_key",
                {"new_str_key": "test_str"},
            ),
            (
                {"bool_key": True},
                "bool_key",
                "new_bool_key",
                {"new_bool_key": True},
            ),
            (
                {"float_key": 3.14},
                "float_key",
                "new_float_key",
                {"new_float_key": 3.14},
            ),
            (
                {"list_key": [1, 2, 3]},
                "list_key",
                "new_list_key",
                {"new_list_key": [1, 2, 3]},
            ),
            (
                {"dict_key": {"nested_key": "value"}},
                "dict_key",
                "new_dict_key",
                {"new_dict_key": {"nested_key": "value"}},
            ),
        ]
        # Test with different types of keys and values
        for obj, src_key, dest_key, expected_result in test_cases:
            self.assertEqual(rename_key(obj, src_key, dest_key), expected_result)

    def test_rename_key_with_different_types_in_place(self):
        test_cases = [
            (
                {"int_key": 1},
                "int_key",
                "new_int_key",
                {"new_int_key": 1},
            ),
            (
                {"str_key": "test_str"},
                "str_key",
                "new_str_key",
                {"new_str_key": "test_str"},
            ),
            (
                {"bool_key": True},
                "bool_key",
                "new_bool_key",
                {"new_bool_key": True},
            ),
            (
                {"float_key": 3.14},
                "float_key",
                "new_float_key",
                {"new_float_key": 3.14},
            ),
            (
                {"list_key": [1, 2, 3]},
                "list_key",
                "new_list_key",
                {"new_list_key": [1, 2, 3]},
            ),
            (
                {"dict_key": {"nested_key": "value"}},
                "dict_key",
                "new_dict_key",
                {"new_dict_key": {"nested_key": "value"}},
            ),
        ]
        # Test with different types of keys and values
        for obj, src_key, dest_key, expected_result in test_cases:
            rename_key(obj, src_key, dest_key, in_place=True)
            self.assertEqual(obj, expected_result)

    def test_rename_key_missing_src_key(self):
        obj = {"key": "value"}
        obj_copy = rename_key(obj, "missing_key", "new_key")
        self.assertEqual(obj_copy, obj)
        self.assertEqual(obj_copy, {"key": "value"})
        self.assertNotIn("new_key", obj_copy)

    def test_rename_key_missing_src_key_in_place(self):
        obj = {"key": "value"}
        obj_copy = rename_key(obj, "missing_key", "new_key")
        self.assertEqual(obj_copy, {"key": "value"})
        self.assertNotIn("new_key", obj_copy)

    def test_rename_key_complex_obj(self):
        obj = {"key": "value", "nested": {"key": "value"}, "list": [1, 2, 3]}
        obj_copy = rename_key(obj, "key", "new_key")
        self.assertEqual(
            obj_copy,
            {"new_key": "value", "nested": {"key": "value"}, "list": [1, 2, 3]},
        )
        self.assertEqual(
            obj,
            {"key": "value", "nested": {"key": "value"}, "list": [1, 2, 3]},
        )

    def test_rename_key_missing_src_key(self):
        obj = {"a": 1, "b": 2, "c": 3}
        obj_copy = rename_key(obj, "missing_key", "new_key")
        self.assertEqual(obj_copy, obj)

    def test_rename_key_existing_dest_key(self):
        obj = {"a": 1, "b": 2, "c": 3}
        obj_copy = rename_key(obj, "b", "a")
        expected_obj = {"a": 2, "c": 3}
        self.assertEqual(obj_copy, expected_obj)

    def test_rename_key_src_and_dest_key_same(self):
        obj = {"a": 1, "b": 2, "c": 3}
        obj_copy = rename_key(obj, "b", "b")
        self.assertEqual(obj, obj_copy)

    def test_rename_key_empty_dict(self):
        obj = {}
        obj_copy = rename_key(obj, "key", "new_key")
        self.assertEqual(obj_copy, {})
        self.assertEqual(obj, {})

    def test_rename_key_with_overwrite(self):
        obj = {"key": "value", "new_key": "overwrite_me"}
        obj_copy = rename_key(obj, "key", "new_key")
        self.assertEqual(obj_copy, {"new_key": "value"})
        self.assertEqual(obj, {"key": "value", "new_key": "overwrite_me"})


class TestUnnestKey(unittest.TestCase):
    def test_unnest_key_valid_input(self):
        obj = {"a": {"b": {"c": 1}}}
        result = unnest_key(obj, "a", "b", "c")
        self.assertEqual(result, 1)

    def test_unnest_key_invalid_input(self):
        obj = {"a": {"b": {"c": 1}}}
        result = unnest_key(obj, "a", "b", "d")
        self.assertIs(result, None)

    def test_unnest_key_empty_input(self):
        obj = {}
        result = unnest_key(obj, "a", "b", "c")
        self.assertIs(result, None)

    def test_unnest_key_valid_input_with_large_nest(self):
        obj = {"a": {"b": {"c": {"d": {"e": {"f": {"g": {"h": 1}}}}}}}}
        result = unnest_key(obj, "a", "b", "c", "d", "e", "f", "g", "h")
        self.assertEqual(result, 1)
