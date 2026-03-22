from __future__ import annotations

from dataclasses import dataclass

from westerosscript.ast import TypeName


@dataclass
class Symbol:
    name: str
    type_name: TypeName
    value: object
    level: int = 0  # Scope nesting level (0=global, 1=block, etc.)
    width: int = 0  # Size in bytes (coin=4, stag=4, oath=1, essence=8)
    offset: int = 0  # Byte offset within the scope's frame


class GreatLedger:
    def __init__(self) -> None:
        self._symbols: dict[str, Symbol] = {}
        self._scope_stack: list[dict[str, Symbol]] = [self._symbols]  # Stack of scopes
        self._offset_stack: list[int] = [0]  # Offset counter for each scope level
        self._current_level: int = 0  # Current nesting level

    def enter_scope(self, scope_name: str) -> None:
        """Enter a new scope (e.g., for a function or block)."""
        self._current_level += 1
        new_scope: dict[str, Symbol] = {}
        self._scope_stack.append(new_scope)
        self._offset_stack.append(0)  # Reset offset for new scope

    def exit_scope(self) -> None:
        """Exit the current scope."""
        if len(self._scope_stack) > 1:
            self._scope_stack.pop()
            self._offset_stack.pop()
            self._current_level -= 1

    def define(self, name: str, type_name: TypeName, value: object) -> None:
        current_scope = self._scope_stack[-1]
        width = _get_width(type_name)
        
        # Ensure offset_stack has entry for current level
        while len(self._offset_stack) <= self._current_level:
            self._offset_stack.append(0)
        
        offset = self._offset_stack[self._current_level]
        
        # Create symbol with level, width, and offset
        sym = Symbol(
            name=name,
            type_name=type_name,
            value=value,
            level=self._current_level,
            width=width,
            offset=offset
        )
        current_scope[name] = sym
        
        # Advance offset for the current level
        self._offset_stack[self._current_level] = offset + width

    def get(self, name: str) -> Symbol | None:
        # Search from innermost to outermost scope
        for scope in reversed(self._scope_stack):
            sym = scope.get(name)
            if sym is not None:
                return sym
        return None

    def items(self) -> list[Symbol]:
        # Return items from the global scope (first scope in stack)
        return list(self._scope_stack[0].values())
    
    def all_items(self) -> list[Symbol]:
        # Return all items from all scopes (for detailed listing)
        return [sym for scope in self._scope_stack for sym in scope.values()]

    def to_text(self) -> str:
        lines: list[str] = []
        lines.append("")
        lines.append("--- THE GREAT LEDGER OF THE REALM ---")
        lines.append("")
        
        all_syms = self.all_items()
        if not all_syms:
            lines.append("(empty)")
            return "\n".join(lines) + "\n"

        # Organize by level for display
        by_level: dict[int, list[Symbol]] = {}
        for sym in all_syms:
            if sym.level not in by_level:
                by_level[sym.level] = []
            by_level[sym.level].append(sym)

        rows = [("NAME", "TYPE", "LVL", "WIDTH", "OFFSET")]
        for level in sorted(by_level.keys()):
            for sym in by_level[level]:
                rows.append((
                    sym.name,
                    sym.type_name.value,
                    str(sym.level),
                    str(sym.width),
                    str(sym.offset)
                ))

        widths = [max(len(str(row[i])) for row in rows) for i in range(5)]
        for i, row in enumerate(rows):
            line = "  ".join(str(row[j]).ljust(widths[j]) for j in range(5))
            lines.append(line)
            if i == 0:
                lines.append("-" * len(line))
        
        # Add memory summaries per level
        lines.append("")
        for level in sorted(by_level.keys()):
            total_bytes = sum(sym.width for sym in by_level[level])
            level_name = f"Level {level}"
            lines.append(f"Total {level_name} Memory Required: {total_bytes} Bytes")
        
        return "\n".join(lines) + "\n"

    def print(self) -> None:
        print(self.to_text(), end="")


def _get_width(type_name: TypeName) -> int:
    """Get byte width for a type."""
    return {
        TypeName.COIN: 4,      # int
        TypeName.STAG: 4,      # float
        TypeName.OATH: 1,      # char
        TypeName.ESSENCE: 8,   # double
        TypeName.SCROLL: 8,    # string (pointer size)
        TypeName.UNKNOWN: 0,
    }.get(type_name, 0)

