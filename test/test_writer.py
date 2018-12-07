from __future__ import unicode_literals

import pytest

import pytoml as toml


@pytest.mark.parametrize("value", [
    float("NaN"),
    float("Inf"),
    -float("Inf"),
])
def test_attempting_to_write_non_number_floats_raises_error(value):
    error = pytest.raises(ValueError, lambda: toml.dumps({"value": value}))
    assert str(error.value) == "{0} is not a valid TOML value".format(value)


def test_pathlib_path_objects_are_written_as_strings():
    pathlib = pytest.importorskip("pathlib")
    path_value = toml.dumps({"value": pathlib.Path("test-path")})
    assert path_value == 'value = "test-path"\n'


def test_pathlib_purepath_objects_are_written_as_strings():
    pathlib = pytest.importorskip("pathlib")
    path_value = toml.dumps({"value": pathlib.PurePath("test-path")})
    assert path_value == 'value = "test-path"\n'


def test_pathlib_purepath_objects_contents_are_escaped():
    pathlib = pytest.importorskip("pathlib")
    path_value = toml.dumps({"value": pathlib.PurePath('C:\\Escape\"this string"')})
    assert path_value == 'value = "C:\\\\Escape\\"this string\\""\n'
