from __future__ import annotations
import ast
import inspect
from sopel.config.types import BaseValidated

import cog


class ClassAttrDocVisitor(ast.NodeVisitor):
    """
    Visit the attributes defined on the given class and extract the ones with PEP 257 attribute docstrings
    """
    @staticmethod
    def _is_string_literal(node: ast.Node) -> bool:
        if not isinstance(node, ast.Expr):
            return False

        if not isinstance(const := node.value, ast.Constant):
            return False

        if not isinstance(const.value, str):
            return False

        return True

    @classmethod
    def _assigns_with_doc(klass, cls: ast.ClassDef) -> Iterable[ast.Node]:
        for cur, nxt in zip(cls.body, cls.body[1:]):
            # NOTE: PEP 257 defines attribute docstrings as explicitly after simple (1 target) assignments
            # Note also that this accepts an assignment and string literal separated by any number of blank lines, and
            # I am not sure if these are considered standard-compliant
            if isinstance(cur, ast.Assign) and len(cur.targets) == 1 and klass._is_string_literal(nxt):
                yield (cur, nxt.value.value)

    @classmethod
    def visit(klass, cls: ast.ClassDef, restrict_attrs: dict[str, BaseValidated] | None = None) -> dict[str, str]:
        if not isinstance(cls, ast.ClassDef):
            breakpoint()
            raise ValueError("This visitor works only with class definitions")

        result = {}

        for (assignment, docstr) in klass._assigns_with_doc(cls):
            [tgt] = assignment.targets
            if restrict_attrs and tgt.id not in restrict_attrs.keys():
                continue
            result[tgt.id] = docstr

        return result


def pad_widths(attrs: dict[str, str]) -> tuple[int, int]:
    max_name = 0
    max_doc = 0

    for name, doc in attrs.items():
        max_name = max(max_name, len(name))
        max_doc = max(max_doc, len(doc))

    return (max_name, max_doc)


def class_definition(cls: type) -> ast.ClassDef:
    clssrc = inspect.getsource(cls)
    [clsdef] = ast.parse(clssrc).body

    return clsdef


def generate_config_table(config_cls: type):
    """
    Generate a Markdown table documenting the configuration of a Sopel plugin
    """
    clsdef = class_definition(config_cls)
    config_attrs = dict(inspect.getmembers(config_cls, predicate=lambda value: isinstance(value, BaseValidated)))
    config_fields = ClassAttrDocVisitor.visit(clsdef, restrict_attrs=config_attrs)

    fieldcol = "Field"
    doccol = "Description"
    defcol = "Default (if any)"

    longest_name, longest_doc = pad_widths(config_fields)
    defaults = {name: config_attrs[name].default for name in config_fields.keys()}
    longest_def = max(len(repr(val)) for val in defaults.values())

    longest_name = max(longest_name, len(fieldcol))
    longest_doc = max(longest_doc, len(fieldcol))
    longest_def = max(longest_def, len(defcol))

    name_width = 2 + longest_name
    doc_width = 2 + longest_doc
    def_width = 2 + longest_def

    cog.outl(f"| {fieldcol: <{name_width}} | {doccol: <{doc_width}} | {defcol: <{def_width}} |")
    cog.outl(f"| {'-'*name_width} | {'-'*doc_width} | {'-'*def_width} |")
    for (name, doc) in config_fields.items():
        name_fmtd = f"`{name}`"
        default_fmtd = f"`{defaults[name]!r}`"
        cog.outl(f"| {name_fmtd: <{name_width}} | {doc: <{doc_width}} | {default_fmtd: <{def_width}} |")
