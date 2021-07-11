from __future__ import annotations

import ast
from typing import Any, Iterator

# The code F is required in order for errors to appear.
ERROR_MESSAGE = "F Missing from __future__ import annotations but imports: {}"
SIMPLIFIABLE_TYPES = (
    "DefaultDict",
    "Deque",
    "Dict",
    "FrozenSet",
    "List",
    "Optional",
    "Set",
    "Tuple",
    "Union",
)


class FutureAnnotationsVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.imports_future_annotations = False
        self.typing_imports: list[str] = []

    def visit_ImportFrom(self, node: Any) -> None:
        if node.module == "__future__":
            for alias in node.names:
                if alias.name == "annotations":
                    self.imports_future_annotations = True

        if node.module == "typing":
            for alias in node.names:
                if alias.name in SIMPLIFIABLE_TYPES:
                    self.typing_imports.append(alias.name)


class FutureAnnotationsChecker:
    name = "flake8-future-annotations"
    version = "0.0.2"

    def __init__(self, tree: ast.Module, filename: str) -> None:
        self.tree = tree
        self.filename = filename

    def run(self) -> Iterator[tuple[int, int, str, type]]:
        visitor = FutureAnnotationsVisitor()
        visitor.visit(self.tree)
        if visitor.imports_future_annotations or not visitor.typing_imports:
            return

        imports = ", ".join(visitor.typing_imports)
        yield 5, 10, ERROR_MESSAGE.format(imports), type(self)
