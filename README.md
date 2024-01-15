# flake8-future-annotations

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![PyPI version](https://badge.fury.io/py/flake8-future-annotations.svg)](https://badge.fury.io/py/flake8-future-annotations)
[![GitHub license](https://img.shields.io/github/license/TylerYep/flake8-future-annotations)](https://github.com/TylerYep/flake8-future-annotations/blob/main/LICENSE)
[![Downloads](https://pepy.tech/badge/flake8-future-annotations)](https://pepy.tech/project/flake8-future-annotations)

Verifies python 3.8+ files use `from __future__ import annotations` if a type is used in the module that can be rewritten using [PEP 563](https://www.python.org/dev/peps/pep-0563/).

Pairs well with [pyupgrade](https://github.com/asottile/pyupgrade) with the `--py37-plus` flag or higher, since pyupgrade only replaces type annotations with the PEP 563 rules if `from __future__ import annotations` is present.

[The flake8-future-annotations plugin, along with autofixes, is now available in Ruff!](https://github.com/astral-sh/ruff/issues/3072)

## flake8 codes

| Code  | Description                                                               |
| ----- | ------------------------------------------------------------------------- |
| FA100 | Missing import if a type used in the module can be rewritten using PEP563 |
| FA101 | Missing import when no rewrite using PEP563 is available (see config)     |
| FA102 | Missing import when code uses simplified types (list, dict, set, etc)     |

## Example

```python
import typing as t
from typing import List

def function(a_dict: t.Dict[str, t.Optional[int]]) -> None:
    a_list: List[str] = []
    a_list.append("hello")
```

As a result, this plugin will emit:

```
hello.py:1:1: FA100 Missing from __future__ import annotations but imports: List, t.Dict, t.Optional
```

After adding the future annotations import, running `pyupgrade` allows the code to be automatically rewritten as:

```python
from __future__ import annotations

def function(a_dict: dict[str, int | None]) -> None:
    a_list: list[str] = []
    a_list.append("hello")
```

## Configuration

If the `--force-future-annotations` option is set, missing `from __future__ import annotations` will be reported regardless of a rewrite available according to PEP 563; in this case, code FA101 is used instead of FA100.

If the `--check-future-annotations` option is set, missing `from __future__ import annotations` will be reported because the following code will error on Python versions older than 3.10 (this check should not be enabled on Python 3.10+):

```python
def function(a_dict: dict[str, int | None]) -> None:
    a_list: list[str] = []
    a_list.append("hello")
```

```
hello.py:1:1: FA102 Missing from __future__ import annotations but uses simplified type annotations: dict, list, union
```
