import unittest

from wvutils.args import nonempty_string, safechars_string


class TestStringMethods(unittest.TestCase):
    def test_nonempty_string(self):
        # Test using a non-empty string
        self.assertEqual(nonempty_string("test")("a"), "a")
        # Test using a non-empty string surrounded by whitespace
        self.assertEqual(nonempty_string("test")(" a "), "a")
        # Test using an empty string (should raise ValueError)
        with self.assertRaises(ValueError):
            nonempty_string("test")("")

    def test_safechars_string(self):
        # Test using a character that is allowed by default
        self.assertEqual(safechars_string("test")("a"), "a")
        # Test using a character that is not allowed by default
        with self.assertRaises(ValueError):
            safechars_string("test")("$")

        # Test using a character that is allowed using custom allowed_chars
        self.assertEqual(safechars_string("test", allowed_chars="abc")("a"), "a")
        # Test using a character that is not allowed using custom allowed_chars
        with self.assertRaises(ValueError):
            safechars_string("test", allowed_chars="abc")("d")
