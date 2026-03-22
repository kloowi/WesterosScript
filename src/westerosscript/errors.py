from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    FATAL = "fatal"


class RecoveryStrategy(str, Enum):
    """Error recovery strategies employed by the lexer/parser."""
    NONE = "none"                  # No recovery attempted
    AUTO_INSERT = "auto_insert"    # Delimiter was auto-inserted to allow parsing to continue
    PANIC_SKIP = "panic_skip"      # Invalid token was skipped to resume parsing


@dataclass(frozen=True)
class Diagnostic:
    severity: Severity
    message: str
    filename: str | None = None
    line: int | None = None
    col: int | None = None
    recovery_strategy: RecoveryStrategy = RecoveryStrategy.NONE
    recovery_detail: str | None = None  # What was inserted/skipped (e.g., "missing '!'", "invalid '@#$'")

    def format(self) -> str:
        loc = ""
        # Only show location for real files (not UI placeholder "<ui>")
        if self.filename is not None and self.filename != "<ui>" and self.line is not None and self.col is not None:
            loc = f"{self.filename}:{self.line}:{self.col}: "
        prefix = {
            Severity.INFO: "[INFO]",
            Severity.WARNING: "[MAESTER WARNING]",
            Severity.FATAL: "[FATAL BETRAYAL]",
        }[self.severity]
        formatted = f"{prefix}\n\n{loc}{self.message}\n"
        
        # Append recovery detail if present
        if self.recovery_strategy != RecoveryStrategy.NONE and self.recovery_detail:
            formatted += f"[Recovery: {self.recovery_strategy.value.upper()}] {self.recovery_detail}\n"
        
        return formatted


@dataclass
class DiagnosticSink:
    diags: list[Diagnostic] = field(default_factory=list)
    _has_fatal: bool = False
    _recovery_count: int = 0
    _auto_insert_count: int = 0
    _panic_skip_count: int = 0

    def _append(self, diag: Diagnostic) -> None:
        self.diags.append(diag)
        if diag.severity == Severity.FATAL:
            self._has_fatal = True
        if diag.recovery_strategy != RecoveryStrategy.NONE:
            self._recovery_count += 1
            if diag.recovery_strategy == RecoveryStrategy.AUTO_INSERT:
                self._auto_insert_count += 1
            elif diag.recovery_strategy == RecoveryStrategy.PANIC_SKIP:
                self._panic_skip_count += 1

    @property
    def has_fatal(self) -> bool:
        return self._has_fatal
    
    @property
    def recovery_count(self) -> int:
        """Count diagnostics that used recovery strategies."""
        return self._recovery_count
    
    @property
    def auto_insert_count(self) -> int:
        """Count AUTO_INSERT recovery strategy uses."""
        return self._auto_insert_count
    
    @property
    def panic_skip_count(self) -> int:
        """Count PANIC_SKIP recovery strategy uses."""
        return self._panic_skip_count

    def info(
        self, 
        message: str, 
        *, 
        filename: str | None = None, 
        line: int | None = None, 
        col: int | None = None,
        recovery_strategy: RecoveryStrategy = RecoveryStrategy.NONE,
        recovery_detail: str | None = None
    ) -> None:
        self._append(
            Diagnostic(
                Severity.INFO,
                message,
                filename,
                line,
                col,
                recovery_strategy=recovery_strategy,
                recovery_detail=recovery_detail,
            )
        )

    def warn(
        self, 
        message: str, 
        *, 
        filename: str | None = None, 
        line: int | None = None, 
        col: int | None = None,
        recovery_strategy: RecoveryStrategy = RecoveryStrategy.NONE,
        recovery_detail: str | None = None
    ) -> None:
        self._append(
            Diagnostic(
                Severity.WARNING,
                message,
                filename,
                line,
                col,
                recovery_strategy=recovery_strategy,
                recovery_detail=recovery_detail,
            )
        )

    def fatal(
        self, 
        message: str, 
        *, 
        filename: str | None = None, 
        line: int | None = None, 
        col: int | None = None,
        recovery_strategy: RecoveryStrategy = RecoveryStrategy.NONE,
        recovery_detail: str | None = None
    ) -> None:
        self._append(
            Diagnostic(
                Severity.FATAL,
                message,
                filename,
                line,
                col,
                recovery_strategy=recovery_strategy,
                recovery_detail=recovery_detail,
            )
        )

    def print(self) -> None:
        if not self.diags:
            return
        for d in self.diags:
            print(d.format())

