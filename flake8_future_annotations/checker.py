from __future__ import annotations

import ast
from typing import Any, Iterator

# The code FA is required in order for errors to appear.
ERROR_MESSAGE_100 = "FA100 Missing from __future__ import annotations but imports: {}"
ERROR_MESSAGE_101 = "FA101 Missing from __future__ import annotations"
ERROR_MESSAGE_102 = (
    "FA102 Missing from __future__ import annotations but uses simplified "
    "type annotations: {}"
)
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
SIMPLIFIED_TYPES = (
    "defaultdict",
    "deque",
    "dict",
    "frozenset",
    "list",
    "set",
    "tuple",
    "type",
)


class FutureAnnotationsVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.typing_aliases: list[str] = []
        self.imports_future_annotations = False
        # e.g. from typing import List, typing.List, t.List
        self.typing_imports: list[str] = []
        self.simplified_types: set[str] = set()

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

    # Below this line are visits to type annotations.

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if not self.imports_future_annotations and node.annotation is not None:
            self.process_annotation(node.annotation)
        self.generic_visit(node)

    def visit_arg(self, node: ast.arg) -> None:
        if not self.imports_future_annotations and node.annotation is not None:
            self.process_annotation(node.annotation)
        self.generic_visit(node)

    def process_annotation(self, node: ast.expr) -> None:
        if isinstance(node, ast.Name) and node.id in SIMPLIFIED_TYPES:
            self.simplified_types.add(node.id)
        elif isinstance(node, ast.Subscript):
            self.process_annotation(node.value)
            self.process_annotation(node.slice)
        elif isinstance(node, ast.Tuple):
            for sub_node in node.elts:
                self.process_annotation(sub_node)
        elif isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.BitOr):
                self.simplified_types.add("union")
            self.process_annotation(node.left)
            self.process_annotation(node.right)
        elif isinstance(node, ast.Index):
            # Index is only used in Python 3.7 and 3.8, deprecated after.
            self.process_annotation(node.value)  # type: ignore[attr-defined]


class FutureAnnotationsChecker:
    name = "flake8-future-annotations"
    version = "1.1.0"
    force_future_annotations = False
    check_future_annotations = False

    def __init__(self, tree: ast.Module, filename: str) -> None:
        self.tree = tree
        self.filename = filename

    @classmethod
    def parse_options(cls, options: Any) -> None:
        cls.force_future_annotations = options.force_future_annotations
        cls.check_future_annotations = options.check_future_annotations

    @staticmethod
    def add_options(option_manager: Any) -> None:
        option_manager.add_option(
            "--force-future-annotations",
            action="store_true",
            parse_from_config=True,
            help="Force the use of from __future__ import annotations in all files.",
        )
        option_manager.add_option(
            "--check-future-annotations",
            action="store_true",
            parse_from_config=True,
            help=(
                "Verifies <3.10 code with simplified types uses "
                "from __future__ import annotations."
            ),
        )

    def run(self) -> Iterator[tuple[int, int, str, type]]:
        visitor = FutureAnnotationsVisitor()
        visitor.visit(self.tree)
        if visitor.imports_future_annotations:
            return

        lineno, char_offset = 1, 0
        if visitor.typing_imports:
            message = ERROR_MESSAGE_100.format(
                ", ".join(sorted(visitor.typing_imports))
            )
            yield lineno, char_offset, message, type(self)

        elif self.force_future_annotations:
            message = ERROR_MESSAGE_101
            yield lineno, char_offset, message, type(self)

        if self.check_future_annotations and visitor.simplified_types:
            # When this is on by default, check sys.version_info < (3, 10)
            message = ERROR_MESSAGE_102.format(
                ", ".join(sorted(visitor.simplified_types))
            )
            yield lineno, char_offset, message, type(self)
