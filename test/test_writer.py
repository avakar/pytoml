from __future__ import unicode_literals
import pathlib

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


@pytest.mark.parametrize("value", [
    pathlib.PurePath("test-path"),
    pathlib.Path("test-path"),
])
def test_pathlib_path_objects_are_written_as_strings(value):
    path_value = toml.dumps({"value": value})
    assert path_value == 'value = "test-path"\n'
