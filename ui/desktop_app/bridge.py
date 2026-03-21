from __future__ import annotations

import json
import re
import textwrap
from dataclasses import asdict, dataclass, fields, is_dataclass

from westerosscript.explain import NarrationLevel
from westerosscript.compiler import analyze_source
from westerosscript.errors import Severity


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
        res = analyze_source(
            source,
            narration=NarrationLevel.OFF,
            print_tokens=False,
            print_ast=False,
            print_ledger=False,
            filename="<ui>",
            capture_output=True,
            run=True,
        )
        out = _build_ui_analysis_output(res)
        diags = _build_ui_diagnostics(res)
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


def _build_ui_analysis_output(res: object) -> str:
    warnings = [d for d in res.diagnostics if d.severity == Severity.WARNING]
    fatals = [d for d in res.diagnostics if d.severity == Severity.FATAL]

    lines: list[str] = []
    lines.append("--- THE MAESTERS EXAMINE THE SCROLL ---")
    if res.lexical_ok:
        lines.append("[MAESTER] ✓ Lexical analysis complete.")
    else:
        lines.append("[FATAL BETRAYAL] Lexical analysis failed.")
    lines.append(f"[MAESTER] Tokens forged: {max(0, res.token_count - 1)}")

    lines.append("")
    lines.append("--- THE SMALL COUNCIL REVIEWS THE DECREE ---")
    if res.syntax_ok:
        lines.append("[COUNCIL] ✓ Syntax structure approved.")
    else:
        lines.append("[FATAL BETRAYAL] Syntax review failed.")
    lines.append(f"[COUNCIL] Statements sealed: {res.statement_count}")

    lines.append("")
    lines.append("--- THE CITADEL RECORDS THE DECREE ---")
    if res.semantic_ok:
        lines.append("[CITADEL] ✓ Semantic checks passed.")
    else:
        lines.append("[FATAL BETRAYAL] Semantic checks failed.")

    if res.ok:
        lines.append("[CITADEL] Realm status: stable and executable.")

    if warnings:
        lines.append("")
        lines.append(f"[MAESTER WARNING] Recovery actions: {len(warnings)}")
        for d in warnings[:3]:
            lines.append(f"[MAESTER] {_compact_message(d.message)}")
        if len(warnings) > 3:
            lines.append(f"[MAESTER] +{len(warnings) - 3} more warning(s).")

    if fatals:
        lines.append("")
        lines.append("[FATAL BETRAYAL] Critical findings:")
        for d in fatals[:3]:
            lines.append(f"[CITADEL] {_compact_message(d.message)}")
        if len(fatals) > 3:
            lines.append(f"[CITADEL] +{len(fatals) - 3} more fatal issue(s).")

    return "\n".join(lines).strip() + "\n"


def _build_ui_diagnostics(res: object) -> str:
    problems = [d for d in res.diagnostics if d.severity in {Severity.WARNING, Severity.FATAL}]
    if not problems:
        return ""

    lines: list[str] = []
    for d in problems:
        prefix = "[MAESTER WARNING]" if d.severity == Severity.WARNING else "[FATAL BETRAYAL]"
        lines.append(f"{prefix} {_compact_message(d.message)}")
    return "\n".join(lines).strip() + "\n"


def _compact_message(msg: str) -> str:
    clean = re.sub(r"\s+", " ", msg).strip()
    first_sentence = clean.split(". ")[0].strip()
    if first_sentence and not first_sentence.endswith((".", "!", "?")):
        first_sentence += "."
    return textwrap.shorten(first_sentence, width=92, placeholder="...")

