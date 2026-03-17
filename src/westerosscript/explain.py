from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class NarrationLevel(str, Enum):
    OFF = "off"
    MINIMAL = "minimal"
    FULL = "full"


@dataclass
class Explainer:
    level: NarrationLevel = NarrationLevel.FULL

    def section(self, title: str) -> None:
        if self.level == NarrationLevel.OFF:
            return
        print(f"\n--- {title} ---\n")

    def say(self, speaker: str, message: str) -> None:
        if self.level == NarrationLevel.OFF:
            return
        if self.level == NarrationLevel.MINIMAL and speaker not in {"FATAL", "WARNING"}:
            return
        print(f"[{speaker}] {message}")

