import os
import tempfile
import unittest

from wvutils.path import (
    ensure_abspath,
    is_pathlike,
    resolve_path,
    stringify_path,
    xdg_cache_path,
)


class PathLike:
    def __init__(self, path):
        self.path = path

    def __fspath__(self):
        return self.path


class NonPathLike:
    pass


class TestIsPathlike(unittest.TestCase):
    def test_string(self):
        self.assertTrue(is_pathlike("path/to/file"))

    def test_pathlike_object(self):
        self.assertTrue(is_pathlike(PathLike("path/to/file")))

    def test_non_pathlike_object(self):
        self.assertFalse(is_pathlike(NonPathLike()))


class TestStringifyPath(unittest.TestCase):
    def test_string(self):
        self.assertEqual(
            stringify_path("path/to/file"),
            "path/to/file",
        )

    def test_pathlike_object(self):
        self.assertEqual(
            stringify_path(PathLike("path/to/file")),
            "path/to/file",
        )

    def test_not_pathlike_object(self):
        with self.assertRaises(TypeError):
            stringify_path(NonPathLike())


class TestEnsureAbspath(unittest.TestCase):
    def test_relative_path(self):
        self.assertEqual(
            ensure_abspath("path/to/file"),
            os.path.abspath("path/to/file"),
        )

    def test_already_absolute(self):
        self.assertEqual(ensure_abspath("/path/to/file"), "/path/to/file")


class TestResolvePath(unittest.TestCase):
    # TODO: Add tests for home directory resolving.

    def test_absolute_string_path(self):
        self.assertEqual(
            resolve_path("path/to/file"),
            os.path.abspath("path/to/file"),
        )

    def test_relative_string_path(self):
        self.assertEqual(
            resolve_path("path/to/file"),
            os.path.abspath("path/to/file"),
        )

    def test_absolute_pathlike_path(self):
        self.assertEqual(
            resolve_path(PathLike("path/to/file")),
            os.path.abspath("path/to/file"),
        )

    def test_relative_pathlike_path(self):
        self.assertEqual(
            resolve_path(PathLike("path/to/file")),
            os.path.abspath("path/to/file"),
        )

    def test_nonpathlike(self):
        with self.assertRaises(TypeError):
            resolve_path(NonPathLike())


class TestXdgCachePath(unittest.TestCase):
    def test_xdg_cache_path_default(self):
        self.assertEqual(
            xdg_cache_path(),
            os.path.join(os.path.expanduser("~"), ".cache"),
        )

    def test_xdg_cache_path_environment_variable(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["XDG_CACHE_HOME"] = tmpdir
            self.assertEqual(xdg_cache_path(), tmpdir)
            os.environ.pop("XDG_CACHE_HOME")

    def test_xdg_cache_path_empty_environment_variable(self):
        os.environ["XDG_CACHE_HOME"] = ""
        self.assertEqual(
            xdg_cache_path(),
            os.path.join(os.path.expanduser("~"), ".cache"),
        )
        os.environ.pop("XDG_CACHE_HOME")

    def test_xdg_cache_path_non_absolute_environment_variable(self):
        os.environ["XDG_CACHE_HOME"] = "path/to/cache"
        self.assertEqual(
            xdg_cache_path(),
            os.path.join(os.path.expanduser("~"), ".cache"),
        )
        os.environ.pop("XDG_CACHE_HOME")
