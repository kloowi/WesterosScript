from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    FATAL = "fatal"


@dataclass(frozen=True)
class Diagnostic:
    severity: Severity
    message: str
    filename: str | None = None
    line: int | None = None
    col: int | None = None

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
        return f"{prefix}\n\n{loc}{self.message}\n"


@dataclass
class DiagnosticSink:
    diags: list[Diagnostic] = field(default_factory=list)

    @property
    def has_fatal(self) -> bool:
        return any(d.severity == Severity.FATAL for d in self.diags)

    def info(self, message: str, *, filename: str | None = None, line: int | None = None, col: int | None = None) -> None:
        self.diags.append(Diagnostic(Severity.INFO, message, filename, line, col))

    def warn(self, message: str, *, filename: str | None = None, line: int | None = None, col: int | None = None) -> None:
        self.diags.append(Diagnostic(Severity.WARNING, message, filename, line, col))

    def fatal(self, message: str, *, filename: str | None = None, line: int | None = None, col: int | None = None) -> None:
        self.diags.append(Diagnostic(Severity.FATAL, message, filename, line, col))

    def print(self) -> None:
        if not self.diags:
            return
        for d in self.diags:
            print(d.format())

