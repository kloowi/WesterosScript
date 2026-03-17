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

    def define(self, name: str, type_name: TypeName, value: object) -> None:
        self._symbols[name] = Symbol(name=name, type_name=type_name, value=value)

    def get(self, name: str) -> Symbol | None:
        return self._symbols.get(name)

    def items(self) -> list[Symbol]:
        return list(self._symbols.values())

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

