from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import sys


class NarrationLevel(str, Enum):
    OFF = "off"
    MINIMAL = "minimal"
    FULL = "full"


@dataclass
class Explainer:
    level: NarrationLevel = NarrationLevel.FULL

    @staticmethod
    def _safe_text(text: str) -> str:
        """
        Some Windows consoles default to legacy encodings (e.g. cp1252) that cannot
        print characters like '✓'. Replace unencodable characters rather than crash.
        """
        enc = getattr(sys.stdout, "encoding", None) or "utf-8"
        try:
            text.encode(enc)
            return text
        except UnicodeEncodeError:
            return text.encode(enc, errors="replace").decode(enc, errors="replace")

    def section(self, title: str) -> None:
        if self.level == NarrationLevel.OFF:
            return
        print(self._safe_text(f"\n--- {title} ---\n"))

    def say(self, speaker: str, message: str) -> None:
        if self.level == NarrationLevel.OFF:
            return
        if self.level == NarrationLevel.MINIMAL and speaker not in {"FATAL", "WARNING"}:
            return
        print(self._safe_text(f"[{speaker}] {message}"))

