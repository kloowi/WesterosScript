from __future__ import annotations

from westerosscript import ast
from westerosscript.errors import DiagnosticSink
from westerosscript.explain import Explainer
from westerosscript.symbols import GreatLedger


class SemanticAnalyzer:
    def __init__(self, *, ledger: GreatLedger, explainer: Explainer, diags: DiagnosticSink) -> None:
        self.ledger = ledger
        self.explainer = explainer
        self.diags = diags

    def analyze(self, program: ast.Program) -> None:
        self.explainer.section("THE CITADEL RECORDS THE DECREE")
        for stmt in program.statements:
            if self.diags.has_fatal:
                return
            self._stmt(stmt)
        if not self.diags.has_fatal:
            self.explainer.say("CITADEL", "✓ The Citadel approves the structure.")

    def _stmt(self, stmt: ast.Stmt) -> None:
        if isinstance(stmt, ast.VarDecl):
            value, value_type = self._eval(stmt.initializer)
            self.explainer.say("CITADEL", f"The variable {stmt.name!r} is declared as type {stmt.type_name.value!r}.")
            if not _is_compatible(stmt.type_name, value_type, value):
                self.diags.fatal(
                    f"Variable {stmt.name!r} is of type {stmt.type_name.value!r},\n"
                    f"yet the value {value!r} is a {value_type.value}.\n\n"
                    "The Citadel refuses this decree."
                )
                return

            stored_value = _coerce(stmt.type_name, value)
            self.explainer.say("CITADEL", "Types are compatible.")
            self.explainer.say("CITADEL", f"Recording {stmt.name!r} into the Great Ledger.")
            self.ledger.define(stmt.name, stmt.type_name, stored_value)
            return

        if isinstance(stmt, ast.Assign):
            sym = self.ledger.get(stmt.name)
            if sym is None:
                self.diags.fatal(f"Unknown identifier {stmt.name!r}.")
                return

            value, value_type = self._eval(stmt.value)
            if self.diags.has_fatal:
                return

            if not _is_compatible(sym.type_name, value_type, value):
                self.diags.fatal(
                    f"Variable {stmt.name!r} is of type {sym.type_name.value!r},\n"
                    f"yet the value {value!r} is a {value_type.value}.\n\n"
                    "The Citadel refuses this decree."
                )
                return

            stored_value = _coerce(sym.type_name, value)
            self.ledger.define(stmt.name, sym.type_name, stored_value)
            return

        if isinstance(stmt, ast.Raven):
            # Analysis-only: just typecheck the expression
            self._eval(stmt.value)
            return

        if isinstance(stmt, ast.Block):
            for s in stmt.statements:
                if self.diags.has_fatal:
                    return
                self._stmt(s)
            return

        if isinstance(stmt, ast.Council):
            self.explainer.say("CITADEL", "The council convenes: conditions will be examined.")
            for cond, block in stmt.branches:
                self._ensure_oath(cond)
                if self.diags.has_fatal:
                    return
                self._stmt(block)
            if stmt.otherwise_block is not None:
                self._stmt(stmt.otherwise_block)
            return

        if isinstance(stmt, ast.WhileWinter):
            self.explainer.say("CITADEL", "Winter persists: the loop condition will be examined.")
            self._ensure_oath(stmt.condition)
            if self.diags.has_fatal:
                return
            self._stmt(stmt.body)
            return

        if isinstance(stmt, ast.ForEachHouse):
            self.explainer.say("CITADEL", "The realm marches in order: a for_each_house loop is proposed.")
            start_v, start_t = self._eval(stmt.start)
            end_v, end_t = self._eval(stmt.end)
            if self.diags.has_fatal:
                return

            if start_t not in {ast.TypeName.COIN, ast.TypeName.DRAGON_GOLD} or end_t not in {
                ast.TypeName.COIN,
                ast.TypeName.DRAGON_GOLD,
            }:
                self.diags.fatal("for_each_house bounds must be numeric wealth (coin or dragon_gold).")
                return

            # Milestone behavior: loop variable is always recorded as coin (integer marching orders).
            start_i = int(start_v)
            self.explainer.say("CITADEL", f"Recording loop variable {stmt.name!r} into the Great Ledger as 'coin'.")
            self.ledger.define(stmt.name, ast.TypeName.COIN, start_i)

            # Typecheck the body in the current (global) ledger context.
            self._stmt(stmt.body)
            return

        if isinstance(stmt, ast.BreakChain) or isinstance(stmt, ast.ContinueMarch):
            # Control-flow markers are fine during analysis (runtime semantics not implemented yet).
            return

        self.diags.fatal(f"Unsupported statement type: {type(stmt).__name__}")

    def _eval(self, expr: ast.Expr) -> tuple[object, ast.TypeName]:
        if isinstance(expr, ast.Literal):
            v = expr.value
            if isinstance(v, bool):
                return v, ast.TypeName.OATH
            if isinstance(v, int):
                return v, ast.TypeName.COIN
            if isinstance(v, float):
                return v, ast.TypeName.DRAGON_GOLD
            if isinstance(v, str):
                return v, ast.TypeName.SCROLL
            return v, ast.TypeName.UNKNOWN

        if isinstance(expr, ast.Identifier):
            sym = self.ledger.get(expr.name)
            if sym is None:
                self.diags.fatal(f"Unknown identifier {expr.name!r}.")
                return None, ast.TypeName.UNKNOWN
            return sym.value, sym.type_name

        if isinstance(expr, ast.Binary):
            left_v, left_t = self._eval(expr.left)
            right_v, right_t = self._eval(expr.right)
            if self.diags.has_fatal:
                return None, ast.TypeName.UNKNOWN

            if left_t not in {ast.TypeName.COIN, ast.TypeName.DRAGON_GOLD} or right_t not in {
                ast.TypeName.COIN,
                ast.TypeName.DRAGON_GOLD,
            }:
                self.diags.fatal(f"Operator {expr.op!r} requires numeric wealth.")
                return None, ast.TypeName.UNKNOWN

            # promote to float if needed
            as_float = left_t == ast.TypeName.DRAGON_GOLD or right_t == ast.TypeName.DRAGON_GOLD
            a = float(left_v) if as_float else int(left_v)
            b = float(right_v) if as_float else int(right_v)

            if expr.op == "unite":
                out = a + b
            elif expr.op == "clash":
                out = a - b
            elif expr.op == "forge":
                out = a * b
            elif expr.op == "divide_realm":
                out = a / b
                as_float = True
            else:
                self.diags.fatal(f"Unknown operator {expr.op!r}.")
                return None, ast.TypeName.UNKNOWN

            return (float(out), ast.TypeName.DRAGON_GOLD) if as_float else (int(out), ast.TypeName.COIN)

        if isinstance(expr, ast.Compare):
            left_v, left_t = self._eval(expr.left)
            right_v, right_t = self._eval(expr.right)
            if self.diags.has_fatal:
                return None, ast.TypeName.UNKNOWN

            # comparisons are numeric-only for now
            if left_t not in {ast.TypeName.COIN, ast.TypeName.DRAGON_GOLD} or right_t not in {
                ast.TypeName.COIN,
                ast.TypeName.DRAGON_GOLD,
            }:
                self.diags.fatal(f"Comparison {expr.op!r} requires numeric wealth.")
                return None, ast.TypeName.UNKNOWN

            a = float(left_v) if left_t == ast.TypeName.DRAGON_GOLD else int(left_v)
            b = float(right_v) if right_t == ast.TypeName.DRAGON_GOLD else int(right_v)

            if expr.op == "equals":
                return a == b, ast.TypeName.OATH
            if expr.op == "greater_than":
                return a > b, ast.TypeName.OATH
            if expr.op == "less_than":
                return a < b, ast.TypeName.OATH

            self.diags.fatal(f"Unknown comparison operator {expr.op!r}.")
            return None, ast.TypeName.UNKNOWN

        self.diags.fatal(f"Unsupported expression type: {type(expr).__name__}")
        return None, ast.TypeName.UNKNOWN

    def _ensure_oath(self, expr: ast.Expr) -> None:
        _v, t = self._eval(expr)
        if self.diags.has_fatal:
            return
        if t != ast.TypeName.OATH:
            self.diags.fatal("Control structure condition must be an oath (boolean).")


def _is_compatible(target: ast.TypeName, value_type: ast.TypeName, value: object) -> bool:
    if target == ast.TypeName.COIN:
        return value_type == ast.TypeName.COIN
    if target == ast.TypeName.DRAGON_GOLD:
        return value_type in {ast.TypeName.COIN, ast.TypeName.DRAGON_GOLD}
    if target == ast.TypeName.SCROLL:
        return value_type == ast.TypeName.SCROLL
    if target == ast.TypeName.OATH:
        return value_type == ast.TypeName.OATH
    if target == ast.TypeName.LEDGER:
        return False
    return False


def _coerce(target: ast.TypeName, value: object) -> object:
    if target == ast.TypeName.DRAGON_GOLD and isinstance(value, int):
        return float(value)
    return value

