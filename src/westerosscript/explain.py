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
        if text.isascii():
            return text
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

    def recovery_action(self, speaker: str, action_type: str, detail: str) -> None:
        """
        Narrate a recovery action taken during parsing/lexing.
        
        Args:
            speaker: Who detected the error (MAESTER, COUNCIL, etc.)
            action_type: Type of recovery (AUTO_INSERT, PANIC_SKIP)
            detail: Description of what was recovered (e.g., "missing '!'" or "invalid '@#$'")
        """
        if self.level == NarrationLevel.OFF:
            return
        
        messages = {
            "AUTO_INSERT": f"I noticed {detail}. I shall insert the missing token and continue.",
            "PANIC_SKIP": f"I encountered {detail}. I shall discard it and continue my examination.",
        }
        
        message = messages.get(action_type, f"Recovery: {action_type} - {detail}")
        print(self._safe_text(f"[{speaker}] {message}"))

    def recovery_summary(self, total_errors: int, recovery_count: int, auto_insert_count: int, panic_skip_count: int) -> None:
        """
        Print a summary of all recovery actions taken during compilation.
        """
        if self.level == NarrationLevel.OFF:
            return
        
        if total_errors == 0:
            print(self._safe_text("[MAESTER] ✓ No errors encountered. The realm is in harmony."))
            return
        
        self.section("RECOVERY ACTIONS TAKEN")
        
        if recovery_count == 0:
            print(self._safe_text(f"[MAESTER] The realm encountered {total_errors} error(s), but I could not recover from them."))
        else:
            print(self._safe_text(f"[MAESTER] The realm encountered {total_errors} error(s). I successfully recovered from {recovery_count}:"))
            if auto_insert_count > 0:
                print(self._safe_text(f"  • Phrase-Level Recovery (AUTO_INSERT): {auto_insert_count} delimiter(s) inserted"))
            if panic_skip_count > 0:
                print(self._safe_text(f"  • Panic Mode Recovery (PANIC_SKIP): {panic_skip_count} invalid token(s) discarded"))


