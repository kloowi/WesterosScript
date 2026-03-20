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
        self._scope_depth: int = 0  # Track scope depth during analysis (don't modify ledger stack)
        self._functions: dict[str, ast.FuncDecl] = {}  # Store function definitions for lookup

    def _push_scope(self) -> None:
        """Push a new scope level during semantic analysis."""
        self._scope_depth += 1
        self.ledger._current_level = self._scope_depth
        # Extend offset stack if needed
        while len(self.ledger._offset_stack) <= self._scope_depth:
            self.ledger._offset_stack.append(0)
        # Reset offset for this level
        self.ledger._offset_stack[self._scope_depth] = 0

    def _pop_scope(self) -> None:
        """Pop scope level during semantic analysis."""
        self._scope_depth -= 1
        self.ledger._current_level = self._scope_depth

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
            if self.diags.has_fatal:
                return
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
                self.diags.fatal(
                    f"Undeclared variable {stmt.name!r}. The variable must be declared before assignment.\n\n"
                    "The Citadel does not recognize this decree."
                )
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

            # Don't call define() for assignments - that would re-declare and mess up offsets.
            # Just type-check; interpretation will handle the actual value update.
            return

        if isinstance(stmt, ast.Raven):
            # Analysis-only: just typecheck the expression
            self._eval(stmt.value)
            return

        if isinstance(stmt, ast.Block):
            # Increase scope depth for semantic analysis
            self._push_scope()
            try:
                for s in stmt.statements:
                    if self.diags.has_fatal:
                        break
                    self._stmt(s)
            finally:
                self._pop_scope()
            return

        if isinstance(stmt, ast.Council):
            self.explainer.say("CITADEL", "The council convenes: conditions will be examined.")
            for cond, block in stmt.branches:
                self._ensure_oath(cond)
                if self.diags.has_fatal:
                    return
                # Each branch is a block with its own scope
                self._push_scope()
                try:
                    self._stmt(block)
                finally:
                    self._pop_scope()
            if stmt.otherwise_block is not None:
                self._push_scope()
                try:
                    self._stmt(stmt.otherwise_block)
                finally:
                    self._pop_scope()
            return

        if isinstance(stmt, ast.WhileWinter):
            self.explainer.say("CITADEL", "Winter persists: the loop condition will be examined.")
            self._ensure_oath(stmt.condition)
            if self.diags.has_fatal:
                return
            # Loop body is a scope
            self._push_scope()
            try:
                self._stmt(stmt.body)
            finally:
                self._pop_scope()
            return

        if isinstance(stmt, ast.ForEachHouse):
            self.explainer.say("CITADEL", "The realm marches in order: a for_each_house loop is proposed.")
            start_v, start_t = self._eval(stmt.start)
            end_v, end_t = self._eval(stmt.end)
            if self.diags.has_fatal:
                return

            if start_t not in {ast.TypeName.COIN, ast.TypeName.STAG} or end_t not in {
                ast.TypeName.COIN,
                ast.TypeName.STAG,
            }:
                self.diags.fatal("for_each_house bounds must be numeric wealth (coin or stag).")
                return

            # Create loop scope for loop variable and body
            self._push_scope()
            try:
                # Milestone behavior: loop variable is always recorded as coin (integer marching orders).
                start_i = int(start_v)
                self.explainer.say("CITADEL", f"Recording loop variable {stmt.name!r} into the Great Ledger as 'coin'.")
                self.ledger.define(stmt.name, ast.TypeName.COIN, start_i)

                # Typecheck the body in the new (loop) scope.
                self._stmt(stmt.body)
            finally:
                self._pop_scope()
            return

        if isinstance(stmt, ast.BreakChain) or isinstance(stmt, ast.ContinueMarch):
            # Control-flow markers are fine during analysis (runtime semantics not implemented yet).
            return

        if isinstance(stmt, ast.FuncDecl):
            self.explainer.say("CITADEL", f"A new decree '{stmt.name}' is recorded with {len(stmt.params)} parameters.")
            # Record function signature
            param_str = ", ".join(f"{t.value} {n}" for t, n in stmt.params)
            self.explainer.say("CITADEL", f"Function signature: {stmt.return_type.value} {stmt.name}({param_str})")
            # Store function for later lookup
            self._functions[stmt.name] = stmt
            # Create function scope and analyze body
            self._push_scope()
            try:
                # Add parameters to scope
                for param_type, param_name in stmt.params:
                    self.ledger.define(param_name, param_type, None)
                # Analyze function body
                self._stmt(stmt.body)
            finally:
                self._pop_scope()
            return

        if isinstance(stmt, ast.Deliver):
            self.explainer.say("CITADEL", "A raven returns from a decree with treasure.")
            # In semantic analysis, we just skip evaluating the return value
            # (at runtime it will be evaluated with parameters bound)
            if stmt.value is not None and isinstance(stmt.value, ast.Identifier):
                # Check that the identifier exists in scope
                sym = self.ledger.get(stmt.value.name)
                if sym is None:
                    self.diags.fatal(
                        f"Undeclared variable {stmt.value.name!r}. The variable must be declared before use.\n\n"
                        "The Citadel does not recognize this decree."
                    )
            return

        self.diags.fatal(f"Unsupported statement type: {type(stmt).__name__}")

    def _eval(self, expr: ast.Expr) -> tuple[object, ast.TypeName]:
        if isinstance(expr, ast.Literal):
            v = expr.value
            if isinstance(v, int):
                return v, ast.TypeName.COIN
            if isinstance(v, float):
                return v, ast.TypeName.STAG
            if isinstance(v, str):
                # Single character = OATH (char type), otherwise = SCROLL (string)
                if len(v) == 1:
                    return v, ast.TypeName.OATH
                return v, ast.TypeName.SCROLL
            return v, ast.TypeName.UNKNOWN

        if isinstance(expr, ast.Identifier):
            sym = self.ledger.get(expr.name)
            if sym is None:
                self.diags.fatal(
                    f"Undeclared variable {expr.name!r}. The variable must be declared before use.\n\n"
                    "The Citadel does not recognize this decree."
                )
                return None, ast.TypeName.UNKNOWN
            return sym.value, sym.type_name

        if isinstance(expr, ast.Binary):
            left_v, left_t = self._eval(expr.left)
            right_v, right_t = self._eval(expr.right)
            if self.diags.has_fatal:
                return None, ast.TypeName.UNKNOWN

            if left_t not in {ast.TypeName.COIN, ast.TypeName.STAG, ast.TypeName.ESSENCE} or right_t not in {
                ast.TypeName.COIN,
                ast.TypeName.STAG,
                ast.TypeName.ESSENCE,
            }:
                self.diags.fatal(f"Operator {expr.op!r} requires numeric wealth.")
                return None, ast.TypeName.UNKNOWN

            # promote to float if needed
            as_float = left_t in {ast.TypeName.STAG, ast.TypeName.ESSENCE} or right_t in {ast.TypeName.STAG, ast.TypeName.ESSENCE}
            a = float(left_v) if as_float else int(left_v)
            b = float(right_v) if as_float else int(right_v)

            if expr.op == "unite":
                out = a + b
            elif expr.op == "clash":
                out = a - b
            elif expr.op == "forge":
                out = a * b
            elif expr.op == "divide_realm":
                if b == 0:
                    self.diags.fatal("Division by zero: cannot divide by zero.")
                    return None, ast.TypeName.UNKNOWN
                out = a / b
                as_float = True
            else:
                self.diags.fatal(f"Unknown operator {expr.op!r}.")
                return None, ast.TypeName.UNKNOWN

            return (float(out), ast.TypeName.ESSENCE if (left_t == ast.TypeName.ESSENCE or right_t == ast.TypeName.ESSENCE) else ast.TypeName.STAG) if as_float else (int(out), ast.TypeName.COIN)

        if isinstance(expr, ast.Compare):
            left_v, left_t = self._eval(expr.left)
            right_v, right_t = self._eval(expr.right)
            if self.diags.has_fatal:
                return None, ast.TypeName.UNKNOWN

            # comparisons are numeric-only for now
            if left_t not in {ast.TypeName.COIN, ast.TypeName.STAG, ast.TypeName.ESSENCE} or right_t not in {
                ast.TypeName.COIN,
                ast.TypeName.STAG,
                ast.TypeName.ESSENCE,
            }:
                self.diags.fatal(f"Comparison {expr.op!r} requires numeric wealth.")
                return None, ast.TypeName.UNKNOWN

            a = float(left_v) if left_t in {ast.TypeName.STAG, ast.TypeName.ESSENCE} else int(left_v)
            b = float(right_v) if right_t in {ast.TypeName.STAG, ast.TypeName.ESSENCE} else int(right_v)

            if expr.op == "equals":
                return a == b, ast.TypeName.SCROLL
            if expr.op == "greater_than":
                return a > b, ast.TypeName.SCROLL
            if expr.op == "less_than":
                return a < b, ast.TypeName.SCROLL

            self.diags.fatal(f"Unknown comparison operator {expr.op!r}.")
            return None, ast.TypeName.UNKNOWN

        if isinstance(expr, ast.FuncCall):
            # Look up function to get return type
            if expr.name in self._functions:
                func_decl = self._functions[expr.name]
                # Evaluate arguments for type checking
                for arg in expr.args:
                    self._eval(arg)
                # Return the function's return type
                return None, func_decl.return_type
            else:
                self.diags.fatal(f"Undeclared function {expr.name!r}.")
                return None, ast.TypeName.UNKNOWN

        self.diags.fatal(f"Unsupported expression type: {type(expr).__name__}")
        return None, ast.TypeName.UNKNOWN

    def _ensure_oath(self, expr: ast.Expr) -> None:
        """Ensure an expression is valid for a condition (comparisons allowed)."""
        if isinstance(expr, ast.Compare):
            # Comparisons are valid for conditions
            return
        # For other expressions, check that they evaluate to at least a proper type
        _v, t = self._eval(expr)
        if self.diags.has_fatal:
            return


def _is_compatible(target: ast.TypeName, value_type: ast.TypeName, value: object) -> bool:
    if target == ast.TypeName.COIN:
        return value_type == ast.TypeName.COIN
    if target == ast.TypeName.STAG:
        return value_type in {ast.TypeName.COIN, ast.TypeName.STAG}
    if target == ast.TypeName.ESSENCE:
        return value_type in {ast.TypeName.COIN, ast.TypeName.STAG, ast.TypeName.ESSENCE}
    if target == ast.TypeName.SCROLL:
        return value_type == ast.TypeName.SCROLL
    if target == ast.TypeName.OATH:
        # OATH (char) accepts single character strings
        return value_type == ast.TypeName.OATH and isinstance(value, str) and len(value) == 1
    return False


def _coerce(target: ast.TypeName, value: object) -> object:
    if target in {ast.TypeName.STAG, ast.TypeName.ESSENCE} and isinstance(value, int):
        return float(value)
    # OATH (char) needs to be a single character, already validated by _is_compatible
    return value

