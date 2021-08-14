# flake8-future-annotations

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![PyPI version](https://badge.fury.io/py/flake8-future-annotations.svg)](https://badge.fury.io/py/flake8-future-annotations)
[![GitHub license](https://img.shields.io/github/license/TylerYep/flake8-future-annotations)](https://github.com/TylerYep/flake8-future-annotations/blob/main/LICENSE)
[![Downloads](https://pepy.tech/badge/flake8-future-annotations)](https://pepy.tech/project/flake8-future-annotations)

Verifies python 3.7+ files use `from __future__ import annotations` if a type is used in the module that can be rewritten using PEP 563.

Pairs well with [pyupgrade](https://github.com/asottile/pyupgrade) with the `--py37-plus` flag or higher, since pyupgrade only replaces type annotations with the PEP 563 rules if `from __future__ import annotations` is present.

For example:

```python
import typing as t
from typing import List

def function(a_dict: t.Dict[str, t.Optional[int]]) -> None:
    a_list: List[str] = []
    a_list.append("hello")
```
As a result, this plugin will emit:

```
hello.py:1:1: F Missing from __future__ import annotations but imports: List, t.Dict, t.Optional
```

After adding the future annotations import, running `pyupgrade` allows the code to be automatically rewritten as:

```python
from __future__ import annotations

def function(a_dict: dict[str, int | None]) -> None:
    a_list: list[str] = []
    a_list.append("hello")
```
