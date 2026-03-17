from __future__ import annotations

from dataclasses import dataclass, field

from westerosscript import ast
from westerosscript.symbols import GreatLedger


@dataclass
class RuntimeResult:
    outputs: list[str] = field(default_factory=list)

    def to_text(self) -> str:
        if not self.outputs:
            return ""
        return "\n".join(self.outputs) + "\n"


class Interpreter:
    def __init__(self, *, ledger: GreatLedger) -> None:
        self.ledger = ledger

    def run(self, program: ast.Program) -> RuntimeResult:
        res = RuntimeResult()
        for stmt in program.statements:
            self._stmt(stmt, res)
        return res

    def _stmt(self, stmt: ast.Stmt, res: RuntimeResult) -> None:
        if isinstance(stmt, ast.VarDecl):
            # Declarations already stored in ledger by semantic analysis.
            return

        if isinstance(stmt, ast.Raven):
            value = self._eval(stmt.value)
            res.outputs.append(f"[Output] {value}")
            return

        if isinstance(stmt, ast.Block):
            for s in stmt.statements:
                self._stmt(s, res)
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
                self._stmt(stmt.body, res)
                iters += 1
                if iters >= cap:
                    res.outputs.append("[Runtime] Loop cap reached (10,000).")
                    return
            return

        if isinstance(stmt, ast.BreakChain) or isinstance(stmt, ast.ContinueMarch):
            # Proper loop control not implemented yet.
            return

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

