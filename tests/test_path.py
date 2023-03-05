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


class TestIsPathlike(unittest.TestCase):
    def test_string(self):
        path = "path/to/file"
        self.assertTrue(is_pathlike(path))

    def test_pathlike_object(self):
        class PathLike:
            def __fspath__(self):
                return "path/to/file"

        path = PathLike()
        self.assertTrue(is_pathlike(path))

    def test_non_pathlike_object(self):
        class NonPathLike:
            pass

        obj = NonPathLike()
        self.assertFalse(is_pathlike(obj))


class TestStringifyPath(unittest.TestCase):
    def test_string(self):
        path = "path/to/file"
        self.assertEqual(stringify_path(path), path)

    def test_pathlike_object(self):
        class PathLike:
            def __fspath__(self):
                return "path/to/file"

        path = PathLike()
        self.assertEqual(stringify_path(path), "path/to/file")

    def test_not_pathlike_object(self):
        class NonPathLike:
            pass

        obj = NonPathLike()
        self.assertRaises(TypeError, stringify_path, obj)


class TestEnsureAbspath(unittest.TestCase):
    def test_already_absolute(self):
        path = "/path/to/file"
        self.assertEqual(ensure_abspath(path), path)


class TestResolvePath(unittest.TestCase):
    def test_string(self):
        path = "path/to/file"
        self.assertEqual(resolve_path(path), os.path.abspath(path))

    def test_pathlike_object(self):
        class PathLike:
            def __fspath__(self):
                return "path/to/file"

        path = PathLike()
        self.assertEqual(resolve_path(path), os.path.abspath("path/to/file"))

    def test_not_pathlike_object(self):
        class NonPathLike:
            pass

        obj = NonPathLike()
        self.assertRaises(TypeError, resolve_path, obj)


class TestXdgCachePath(unittest.TestCase):
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

    def test_xdg_cache_path_default(self):
        self.assertEqual(
            xdg_cache_path(),
            os.path.join(os.path.expanduser("~"), ".cache"),
        )
