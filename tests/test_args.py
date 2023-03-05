import unittest

from wvutils.args import nonempty_string, safechars_string


class TestNonEmptyString(unittest.TestCase):
    def test_nonempty_string(self):
        self.assertEqual(nonempty_string("test")("a"), "a")

    def test_nonempty_surrounded_by_whitespace(self):
        self.assertEqual(nonempty_string("test")(" a "), "a")

    def test_empty(self):
        with self.assertRaises(ValueError):
            nonempty_string("test")("")


class TestSafeCharsString(unittest.TestCase):
    def test_safe_using_default(self):
        self.assertEqual(safechars_string("test")("a"), "a")

    def test_unsafe_using_default(self):
        with self.assertRaises(ValueError):
            safechars_string("test")("$")

    def test_safe_using_custom_allowed_chars_string(self):
        self.assertEqual(
            safechars_string("test", allowed_chars="abc")("a"),
            "a",
        )

    def test_unsafe_using_custom_allowed_chars_string(self):
        with self.assertRaises(ValueError):
            safechars_string("test", allowed_chars="abc")("d")

    def test_safe_using_custom_allowed_chars_set(self):
        self.assertEqual(
            safechars_string("test", allowed_chars={"a", "b", "c"})("a"),
            "a",
        )

    def test_unsafe_using_custom_allowed_chars_set(self):
        with self.assertRaises(ValueError):
            safechars_string("test", allowed_chars={"a", "b", "c"})("d")

    def test_safe_using_custom_allowed_chars_tuple(self):
        self.assertEqual(
            safechars_string("test", allowed_chars=("a", "b", "c"))("a"),
            "a",
        )

    def test_unsafe_using_custom_allowed_chars_tuple(self):
        with self.assertRaises(ValueError):
            safechars_string("test", allowed_chars=("a", "b", "c"))("d")

    def test_safe_using_custom_allowed_chars_list(self):
        self.assertEqual(
            safechars_string("test", allowed_chars=["a", "b", "c"])("a"),
            "a",
        )

    def test_unsafe_using_custom_allowed_chars_list(self):
        with self.assertRaises(ValueError):
            safechars_string("test", allowed_chars=["a", "b", "c"])("d")
