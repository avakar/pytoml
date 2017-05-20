from __future__ import unicode_literals

import sys
if sys.version_info < (2, 7):
    from StringIO import StringIO
else:
    from io import StringIO
    
import pytest

import pytoml as toml


def test_name_of_fileobj_is_used_in_errors():
    source = StringIO("[")
    source.name = "<source>"
    error = pytest.raises(toml.TomlError, lambda: toml.load(source))
    assert error.value.filename == "<source>"


def test_when_fileobj_has_no_name_attr_then_repr_of_fileobj_is_used_in_errors():
    source = StringIO("[")
    error = pytest.raises(toml.TomlError, lambda: toml.load(source))
    assert error.value.filename == repr(source)
