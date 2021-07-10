from __future__ import annotations
import ast
from typing import Any, Iterator

ERROR_MESSAGE = "Missing from __future__ import annotations"


class FutureAnnotationsVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.imports_future_annotations = False

    def visit_ImportFrom(self, node: Any) -> None:
        if node.module == "__future__":
            for alias in node.names:
                if alias.name == "annotations":
                    self.imports_future_annotations = True


class FutureAnnotationsChecker:
    name = "flake8-future-annotations"
    version = "0.0.1"

    def __init__(self, tree: ast.Module, filename: str) -> None:
        self.tree = tree
        self.filename = filename

    def run(self) -> Iterator[tuple[int, int, str, type]]:
        visitor = FutureAnnotationsVisitor()
        visitor.visit(self.tree)
        if visitor.imports_future_annotations:
            return

        yield 1, 0, ERROR_MESSAGE, type(self)
