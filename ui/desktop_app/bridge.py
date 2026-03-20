from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields, is_dataclass

from westerosscript.explain import NarrationLevel
from westerosscript.compiler import analyze_source


@dataclass(frozen=True)
class AnalyzeUiResult:
    ok: bool
    output: str
    diagnostics: str
    ledger: str
    runtime: str
    ast: str


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
                ast=_ast_to_json(res.program),
            )
        )


def _ast_to_json(program: object | None) -> str:
    if program is None:
        return ""
    return json.dumps(_ast_node_to_dict(program), indent=2)


def _ast_node_to_dict(value: object) -> object:
    if is_dataclass(value):
        payload = {"type": value.__class__.__name__}
        for f in fields(value):
            payload[f.name] = _ast_node_to_dict(getattr(value, f.name))
        return payload
    if isinstance(value, list):
        return [_ast_node_to_dict(item) for item in value]
    if isinstance(value, tuple):
        return [_ast_node_to_dict(item) for item in value]
    if isinstance(value, dict):
        return {str(k): _ast_node_to_dict(v) for k, v in value.items()}
    return value


def _extract_diagnostics(text: str) -> str:
    # Diagnostics are printed as blocks starting with [MAESTER WARNING] or [FATAL BETRAYAL].
    # Keep the extraction simple and robust: return from the first diagnostic marker onwards.
    markers = ["[MAESTER WARNING]", "[FATAL BETRAYAL]"]
    idxs = [text.find(m) for m in markers if text.find(m) != -1]
    if not idxs:
        return ""
    start = min(idxs)
    return text[start:].strip() + "\n"

