# pytoml

This project aims at being a specs-conforming and strict parser for [TOML][1] files.
The parser currently supports [version 0.4.0][2] of the specs.

The project supports Python 2.7 and 3.4+.

Install:

    easy_install pytoml

The interface is the same as for the standard `json` package.

    >>> import pytoml as toml
    >>> toml.loads('a = 1')
    {'a': 1}
    >>> with open('file.toml', 'rb') as fin:
    ...     toml.load(fin)
    {'a': 1}

The `loads` function accepts either a bytes object
(that gets decoded as UTF-8 with no BOM allowed),
or a unicode object.

## Installation

    easy_install pytoml

  [1]: https://github.com/toml-lang/toml
  [2]: https://github.com/toml-lang/toml/blob/master/versions/en/toml-v0.4.0.md
