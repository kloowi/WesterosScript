from __future__ import annotations

from dataclasses import asdict, dataclass

from westerosscript.explain import NarrationLevel
from westerosscript.compiler import analyze_source


@dataclass(frozen=True)
class AnalyzeUiResult:
    ok: bool
    output: str
    diagnostics: str
    ledger: str
    runtime: str


class WesterosApi:
    def analyze(self, source: str, narration: str = "full") -> dict:
        level = NarrationLevel(narration) if narration in {lvl.value for lvl in NarrationLevel} else NarrationLevel.FULL
        res = analyze_source(
            source,
            narration=level,
            print_tokens=False,
            print_ast=False,
            print_ledger=False,
            filename="<ui>",
            capture_output=True,
            run=True,
        )
        out = res.output or ""
        diags = _extract_diagnostics(out)
        return asdict(
            AnalyzeUiResult(
                ok=res.ok,
                output=out,
                diagnostics=diags,
                ledger=res.ledger_text or "",
                runtime=res.runtime_output or "",
            )
        )


def _extract_diagnostics(text: str) -> str:
    # Diagnostics are printed as blocks starting with [MAESTER WARNING] or [FATAL BETRAYAL].
    # Keep the extraction simple and robust: return from the first diagnostic marker onwards.
    markers = ["[MAESTER WARNING]", "[FATAL BETRAYAL]"]
    idxs = [text.find(m) for m in markers if text.find(m) != -1]
    if not idxs:
        return ""
    start = min(idxs)
    return text[start:].strip() + "\n"

