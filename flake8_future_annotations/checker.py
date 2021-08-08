from __future__ import annotations

import ast
from typing import Iterator

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
    "Type",
)


class FutureAnnotationsVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.typing_aliases: list[str] = []
        self.imports_future_annotations = False
        # e.g. from typing import List, typing.List, t.List
        self.typing_imports: list[str] = []

    def visit_Import(self, node: ast.Import) -> None:
        """
        import typing
        or
        import typing as t

        We want to add typing or t to the list of typing aliases.
        """
        for alias in node.names:
            if alias.name == "typing":
                self.typing_aliases.append("typing")
            if alias.asname is not None:
                self.typing_aliases.append(alias.asname)

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """
        Detect the `from __future__ import annotations` import if present.

        If `from typing import ...` is used, add simplifiable names that were imported.
        """
        if node.module == "__future__":
            for alias in node.names:
                if alias.name == "annotations":
                    self.imports_future_annotations = True

        if node.module == "typing":
            for alias in node.names:
                if alias.name in SIMPLIFIABLE_TYPES:
                    self.typing_imports.append(alias.name)

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """
        If `import typing` or `import typing as t` is used, add simplifiable names
        that were used later on in the code.
        """
        if (
            node.attr in SIMPLIFIABLE_TYPES
            and isinstance(node.value, ast.Name)
            and node.value.id in self.typing_aliases
        ):
            self.typing_imports.append(f"{node.value.id}.{node.attr}")
        self.generic_visit(node)


class FutureAnnotationsChecker:
    name = "flake8-future-annotations"
    version = "0.0.3"

    def __init__(self, tree: ast.Module, filename: str) -> None:
        self.tree = tree
        self.filename = filename

    def run(self) -> Iterator[tuple[int, int, str, type]]:
        visitor = FutureAnnotationsVisitor()
        visitor.visit(self.tree)
        if visitor.imports_future_annotations or not visitor.typing_imports:
            return

        imports = ", ".join(visitor.typing_imports)
        lineno, char_offset = 1, 0
        yield lineno, char_offset, ERROR_MESSAGE.format(imports), type(self)
