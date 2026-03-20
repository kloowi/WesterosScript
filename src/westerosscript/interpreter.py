from __future__ import annotations

from dataclasses import dataclass, field

from westerosscript import ast
from westerosscript.symbols import GreatLedger, Symbol


class _LoopBreak(Exception):
    pass


class _LoopContinue(Exception):
    pass


@dataclass
class RuntimeResult:
    outputs: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_text(self) -> str:
        if not self.outputs and not self.errors:
            return ""
        lines = []
        lines.extend(self.outputs)
        if self.errors:
            lines.append("")
            for err in self.errors:
                lines.append(f"[Runtime Error] {err}")
        return "\n".join(lines) + "\n"


class Interpreter:
    def __init__(self, *, ledger: GreatLedger) -> None:
        self.ledger = ledger
        self.has_runtime_error = False

    def run(self, program: ast.Program) -> RuntimeResult:
        res = RuntimeResult()
        for stmt in program.statements:
            try:
                self._stmt(stmt, res)
            except _LoopBreak:
                res.errors.append("break_chain used outside of a loop.")
            except _LoopContinue:
                res.errors.append("continue_march used outside of a loop.")
        return res

    def _stmt(self, stmt: ast.Stmt, res: RuntimeResult) -> None:
        if isinstance(stmt, ast.VarDecl):
            # Declarations already stored in ledger by semantic analysis.
            return

        if isinstance(stmt, ast.Assign):
            # Update an existing symbol value in the ledger.
            # First, find which scope has this symbol (from inner to outer)
            sym = self.ledger.get(stmt.name)
            if sym is None:
                # Semantic analysis should have caught this.
                return
            value = self._eval(stmt.value)
            
            # Update the symbol in its original scope, preserving its level/width/offset
            # Search through the scope stack to find and update the symbol
            found = False
            for scope in reversed(self.ledger._scope_stack):
                if stmt.name in scope:
                    # Preserve the original level/width/offset, just update value
                    scope[stmt.name] = Symbol(
                        name=stmt.name,
                        type_name=sym.type_name,
                        value=value,
                        level=sym.level,
                        width=sym.width,
                        offset=sym.offset
                    )
                    found = True
                    break
            
            if not found:
                # Fallback: define in current scope (shouldn't happen if semantic analysis is correct)
                self.ledger.define(stmt.name, sym.type_name, value)
            return

        if isinstance(stmt, ast.Raven):
            value = self._eval(stmt.value)
            if self.has_runtime_error:
                res.errors.append("Cannot output result due to division by zero error.")
                self.has_runtime_error = False  # Reset error flag
            else:
                res.outputs.append(f"[Output] {value}")
            return

        if isinstance(stmt, ast.Block):
            # Enter a new scope for this block, exit when done
            self.ledger.enter_scope("block")
            try:
                for s in stmt.statements:
                    self._stmt(s, res)
            finally:
                self.ledger.exit_scope()
            return

        # Control structures are parsed and type-checked; runtime execution is minimal for now.
        if isinstance(stmt, ast.Council):
            # Execute the first branch whose condition is true; if none, run otherwise.
            for cond, block in stmt.branches:
                if bool(self._eval(cond)):
                    self._stmt(block, res)
                    return
            if stmt.otherwise_block is not None:
                self._stmt(stmt.otherwise_block, res)
            return

        if isinstance(stmt, ast.WhileWinter):
            # Basic while execution with a safety cap to avoid freezing the UI.
            cap = 10_000
            iters = 0
            while bool(self._eval(stmt.condition)):
                try:
                    self._stmt(stmt.body, res)
                except _LoopContinue:
                    pass
                except _LoopBreak:
                    return

                iters += 1
                if iters >= cap:
                    res.outputs.append("[Runtime] Loop cap reached (10,000).")
                    return
            return

        if isinstance(stmt, ast.ForEachHouse):
            # for_each_house marches from start (inclusive) to end (exclusive), auto-incrementing by 1.
            # Create a loop scope to contain the loop variable
            self.ledger.enter_scope("for_each_house_loop")
            try:
                cap = 100_000
                start = int(self._eval(stmt.start))
                end = int(self._eval(stmt.end))
                iters = 0

                i = start
                while i < end:
                    # Store current iteration value in the loop scope
                    self.ledger.define(stmt.name, ast.TypeName.COIN, i)
                    try:
                        self._stmt(stmt.body, res)
                    except _LoopContinue:
                        i += 1
                        continue
                    except _LoopBreak:
                        break

                    i += 1
                    iters += 1
                    if iters >= cap:
                        res.outputs.append("[Runtime] Loop cap reached (100,000).")
                        break
            finally:
                self.ledger.exit_scope()
            return

        if isinstance(stmt, ast.BreakChain):
            raise _LoopBreak()

        if isinstance(stmt, ast.ContinueMarch):
            raise _LoopContinue()

    def _eval(self, expr: ast.Expr) -> object:
        if isinstance(expr, ast.Literal):
            return expr.value

        if isinstance(expr, ast.Identifier):
            sym = self.ledger.get(expr.name)
            return sym.value if sym is not None else None

        if isinstance(expr, ast.Binary):
            a = self._eval(expr.left)
            b = self._eval(expr.right)
            if expr.op == "unite":
                return a + b
            if expr.op == "clash":
                return a - b
            if expr.op == "forge":
                return a * b
            if expr.op == "divide_realm":
                # Check for division by zero
                if b == 0:
                    self.has_runtime_error = True
                    return None  # Return None to signal error
                return a / b
            return None

        if isinstance(expr, ast.Compare):
            a = self._eval(expr.left)
            b = self._eval(expr.right)
            if expr.op == "equals":
                return a == b
            if expr.op == "greater_than":
                return a > b
            if expr.op == "less_than":
                return a < b
            return None

        return None

