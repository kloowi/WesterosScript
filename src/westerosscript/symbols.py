from __future__ import annotations

from dataclasses import dataclass

from westerosscript.ast import TypeName


@dataclass
class Symbol:
    name: str
    type_name: TypeName
    value: object


class GreatLedger:
    def __init__(self) -> None:
        self._symbols: dict[str, Symbol] = {}
        self._scope_stack: list[dict[str, Symbol]] = [self._symbols]  # Stack of scopes

    def enter_scope(self, scope_name: str) -> None:
        """Enter a new scope (e.g., for a function)."""
        new_scope: dict[str, Symbol] = {}
        self._scope_stack.append(new_scope)

    def exit_scope(self) -> None:
        """Exit the current scope."""
        if len(self._scope_stack) > 1:
            self._scope_stack.pop()

    def define(self, name: str, type_name: TypeName, value: object) -> None:
        current_scope = self._scope_stack[-1]
        current_scope[name] = Symbol(name=name, type_name=type_name, value=value)

    def get(self, name: str) -> Symbol | None:
        # Search from innermost to outermost scope
        for scope in reversed(self._scope_stack):
            if name in scope:
                return scope[name]
        return None

    def items(self) -> list[Symbol]:
        # Return items from the global scope (first scope in stack)
        return list(self._scope_stack[0].values())

    def to_text(self) -> str:
        lines: list[str] = []
        lines.append("")
        lines.append("--- THE GREAT LEDGER OF THE REALM ---")
        lines.append("")
        if not self._symbols:
            lines.append("(empty)")
            return "\n".join(lines) + "\n"

        rows = [("NAME", "TYPE", "VALUE")]
        for sym in self.items():
            rows.append((sym.name, sym.type_name.value, _format_value(sym.value)))

        widths = [max(len(str(row[i])) for row in rows) for i in range(3)]
        for i, row in enumerate(rows):
            line = f"{str(row[0]).ljust(widths[0])}  {str(row[1]).ljust(widths[1])}  {str(row[2]).ljust(widths[2])}"
            lines.append(line)
            if i == 0:
                lines.append("-" * len(line))
        return "\n".join(lines) + "\n"

    def print(self) -> None:
        print(self.to_text(), end="")


def _format_value(v: object) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)

