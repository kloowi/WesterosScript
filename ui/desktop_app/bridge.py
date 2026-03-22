from __future__ import annotations

import json
import re
import textwrap
from dataclasses import asdict, dataclass, fields, is_dataclass
from pathlib import Path

from westerosscript import ast
from westerosscript.explain import NarrationLevel
from westerosscript.compiler import analyze_source
from westerosscript.errors import Severity
from westerosscript.tokens import TokenType


@dataclass(frozen=True)
class AnalyzeUiResult:
    ok: bool
    output: str
    lexical: str
    syntax: str
    semantic: str
    diagnostics: str
    ledger: str
    runtime: str
    ast: str


class WesterosApi:
    def __init__(self) -> None:
        self._window: object | None = None
        self._open_dialog_kind: object | None = None
        self._save_dialog_kind: object | None = None
        self._repo_root = Path(__file__).resolve().parents[2]

    def attach_window(self, window: object, open_dialog_kind: object, save_dialog_kind: object) -> None:
        self._window = window
        self._open_dialog_kind = open_dialog_kind
        self._save_dialog_kind = save_dialog_kind

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
        lexical_out = _build_lexical_output(res)
        syntax_out = _build_syntax_output(res)
        semantic_out = _build_semantic_output(res)
        diags = _build_ui_diagnostics(res)
        return asdict(
            AnalyzeUiResult(
                ok=res.ok,
                output=out,
                lexical=lexical_out,
                syntax=syntax_out,
                semantic=semantic_out,
                diagnostics=diags,
                ledger=res.ledger_text or "",
                runtime=res.runtime_output or "",
                ast=_ast_to_json(res.program),
            )
        )

    def open_file(self, selected_path: str | None = None) -> dict:
        path_text = selected_path.strip() if selected_path else ""
        if path_text:
            target = Path(path_text).expanduser()
        else:
            dialog_path = self._choose_open_path()
            if dialog_path is None:
                return {"ok": False, "canceled": True, "message": "Open canceled."}
            target = dialog_path

        if target.suffix.lower() != ".wss":
            return {"ok": False, "canceled": False, "message": "Only .wss files can be opened."}

        try:
            source = target.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return {
                "ok": False,
                "canceled": False,
                "message": "Unable to read file as UTF-8. Please save it as UTF-8 and try again.",
            }
        except OSError as exc:
            return {"ok": False, "canceled": False, "message": f"Unable to open file: {exc}"}

        return {
            "ok": True,
            "canceled": False,
            "path": str(target.resolve()),
            "name": target.name,
            "source": source,
        }

    def save_file_as(self, source: str, suggested_name: str = "script.wss") -> dict:
        target = self._choose_save_path(suggested_name)
        if target is None:
            return {"ok": False, "canceled": True, "message": "Save canceled."}

        try:
            target.write_text(source, encoding="utf-8")
        except OSError as exc:
            return {"ok": False, "canceled": False, "message": f"Unable to save file: {exc}"}

        return {
            "ok": True,
            "canceled": False,
            "path": str(target.resolve()),
            "name": target.name,
            "message": f"Saved {target.name}.",
        }

    def _choose_open_path(self) -> Path | None:
        if self._window is None or self._open_dialog_kind is None:
            return None

        picked = None
        try:
            picked = self._window.create_file_dialog(
                self._open_dialog_kind,
                allow_multiple=False,
                directory=str(self._repo_root),
                file_types=("WesterosScript (*.wss)", "*.wss"),
            )
        except TypeError:
            picked = self._window.create_file_dialog(self._open_dialog_kind)

        path = self._coerce_dialog_path(picked)
        return path.expanduser() if path is not None else None

    def _choose_save_path(self, suggested_name: str) -> Path | None:
        if self._window is None or self._save_dialog_kind is None:
            return None

        safe_name = suggested_name.strip() or "script.wss"
        if safe_name.lower().endswith(".ws"):
            safe_name = f"{safe_name[:-3]}.wss"
        if not safe_name.lower().endswith(".wss"):
            safe_name = f"{safe_name}.wss"

        picked = None
        try:
            picked = self._window.create_file_dialog(
                self._save_dialog_kind,
                save_filename=safe_name,
                directory=str(self._repo_root),
                file_types=("WesterosScript (*.wss)", "*.wss"),
            )
        except TypeError:
            picked = self._window.create_file_dialog(self._save_dialog_kind, save_filename=safe_name)

        path = self._coerce_dialog_path(picked)
        if path is None:
            return None
        out = path.expanduser()
        if out.suffix.lower() != ".wss":
            out = out.with_suffix(".wss")
        return out

    @staticmethod
    def _coerce_dialog_path(picked: object) -> Path | None:
        if not picked:
            return None
        if isinstance(picked, (list, tuple)):
            first = picked[0] if picked else None
            return Path(str(first)) if first else None
        return Path(str(picked))


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
    # Legacy compatibility field for older UI code paths.
    lexical = _build_lexical_output(res)
    syntax = _build_syntax_output(res)
    semantic = _build_semantic_output(res)
    return f"{lexical}\n{syntax}\n{semantic}".strip() + "\n"


def _build_lexical_output(res: object) -> str:
    lines: list[str] = []
    lines.append("[MAESTER] Reads every token before any judgment.")

    visible_tokens = [t for t in res.tokens if t.type != TokenType.EOF]
    if visible_tokens:
        for idx, tok in enumerate(visible_tokens, start=1):
            token_kind = _token_kind_label(tok.type)
            lexeme = tok.lexeme if tok.lexeme else "<empty>"
            lines.append(f"[STEP] Token {idx}: {token_kind} {lexeme!r}")
    else:
        lines.append("[STEP] No lexical tokens were forged from the source.")

    lex_diags = res.diagnostics[: res.lexical_diags_end]
    if res.lexical_ok:
        lines.append(f"[OK] The Maester forged {len(visible_tokens)} tokens.")
    else:
        lines.append("[FATAL BETRAYAL] The Maester could not complete token forging.")

    for d in lex_diags:
        prefix = "[MAESTER WARNING]" if d.severity == Severity.WARNING else "[FATAL BETRAYAL]"
        lines.append(f"{prefix} {_compact_message(d.message)}")

    return "\n".join(lines).strip() + "\n"


def _build_syntax_output(res: object) -> str:
    lines: list[str] = []
    lines.append("[COUNCIL] Verifies decree structure and statement order.")

    statements = res.program.statements if res.program is not None else []
    if statements:
        for idx, stmt in enumerate(statements, start=1):
            lines.append(f"[STEP] Statement {idx}: {_syntax_statement_line(stmt)}")
    else:
        lines.append("[STEP] No complete statements were sealed by the parser.")

    syntax_diags = res.diagnostics[res.lexical_diags_end : res.syntax_diags_end]
    if res.syntax_ok:
        lines.append(f"[OK] The Council sealed {len(statements)} statements.")
    else:
        lines.append("[FATAL BETRAYAL] The Council rejected the decree structure.")

    for d in syntax_diags:
        prefix = "[MAESTER WARNING]" if d.severity == Severity.WARNING else "[FATAL BETRAYAL]"
        lines.append(f"{prefix} {_compact_message(d.message)}")

    return "\n".join(lines).strip() + "\n"


def _build_semantic_output(res: object) -> str:
    lines: list[str] = []
    lines.append("[CITADEL] Confirms meaning, types, and symbol consistency.")

    semantic_lines = _semantic_events(res.program)
    if semantic_lines:
        for idx, event in enumerate(semantic_lines, start=1):
            lines.append(f"[STEP] Semantic {idx}: {event}")
    else:
        lines.append("[STEP] No semantic checks executed because earlier phases stopped progression.")

    semantic_diags = res.diagnostics[res.syntax_diags_end :]
    if res.semantic_ok:
        lines.append(f"[OK] The Citadel cleared {len(semantic_lines)} semantic checks.")
    else:
        lines.append("[FATAL BETRAYAL] The Citadel refused one or more decrees.")

    for d in semantic_diags:
        prefix = "[MAESTER WARNING]" if d.severity == Severity.WARNING else "[FATAL BETRAYAL]"
        lines.append(f"{prefix} {_compact_message(d.message)}")

    return "\n".join(lines).strip() + "\n"


def _syntax_statement_line(stmt: ast.Stmt) -> str:
    if isinstance(stmt, ast.VarDecl):
        const_prefix = "constant " if stmt.is_constant else ""
        return f"{const_prefix}Declaration for {stmt.name!r} with assignment rune present."
    if isinstance(stmt, ast.Assign):
        return f"assignment updates {stmt.name!r} with a parsed expression and terminator."
    if isinstance(stmt, ast.Raven):
        return "Raven output statement with one expression payload."
    if isinstance(stmt, ast.Council):
        branches = len(stmt.branches)
        has_otherwise = "with otherwise" if stmt.otherwise_block is not None else "without otherwise"
        return f"council branch statement with {branches} branch condition(s), {has_otherwise}."
    if isinstance(stmt, ast.WhileWinter):
        return "while_winter loop with one condition and one scoped body."
    if isinstance(stmt, ast.ForEachHouse):
        return f"for_each_house loop over {stmt.name!r} with start/end range and body block."
    if isinstance(stmt, ast.BreakChain):
        return "break_chain control statement with terminator."
    if isinstance(stmt, ast.ContinueMarch):
        return "continue_march control statement with terminator."
    if isinstance(stmt, ast.FuncDecl):
        return f"decree {stmt.name!r} with {len(stmt.params)} parameter(s) and scoped body."
    if isinstance(stmt, ast.Deliver):
        return "deliver return statement with valid terminator."
    if isinstance(stmt, ast.Block):
        return f"block scope containing {len(stmt.statements)} nested statement(s)."
    return f"parsed {stmt.__class__.__name__} statement."


def _semantic_events(program: ast.Program | None) -> list[str]:
    if program is None:
        return []

    events: list[str] = []
    for stmt in program.statements:
        _semantic_stmt_events(stmt, events)
    return events


def _semantic_stmt_events(stmt: ast.Stmt, events: list[str]) -> None:
    if isinstance(stmt, ast.VarDecl):
        events.append(f"Declare {stmt.name!r} as {stmt.type_name.value} and Type-check initializer.")
        _semantic_expr_events(stmt.initializer, events)
        return
    if isinstance(stmt, ast.Assign):
        events.append(f"Resolve existing symbol {stmt.name!r} before assignment.")
        _semantic_expr_events(stmt.value, events)
        events.append(f"Type-check assigned value against {stmt.name!r}.")
        return
    if isinstance(stmt, ast.Raven):
        events.append("Type-check raven payload expression.")
        _semantic_expr_events(stmt.value, events)
        return
    if isinstance(stmt, ast.Block):
        events.append("enter scoped block and validate enclosed statements.")
        for inner in stmt.statements:
            _semantic_stmt_events(inner, events)
        events.append("exit scoped block.")
        return
    if isinstance(stmt, ast.Council):
        events.append("validate council branch condition(s) as legal comparisons or typed values.")
        for cond, block in stmt.branches:
            _semantic_expr_events(cond, events)
            _semantic_stmt_events(block, events)
        if stmt.otherwise_block is not None:
            _semantic_stmt_events(stmt.otherwise_block, events)
        return
    if isinstance(stmt, ast.WhileWinter):
        events.append("validate while_winter condition and loop body scope.")
        _semantic_expr_events(stmt.condition, events)
        _semantic_stmt_events(stmt.body, events)
        return
    if isinstance(stmt, ast.ForEachHouse):
        events.append(f"validate numeric bounds for for_each_house loop {stmt.name!r}.")
        _semantic_expr_events(stmt.start, events)
        _semantic_expr_events(stmt.end, events)
        _semantic_stmt_events(stmt.body, events)
        return
    if isinstance(stmt, ast.FuncDecl):
        events.append(f"record decree {stmt.name!r} signature with {len(stmt.params)} parameter(s).")
        _semantic_stmt_events(stmt.body, events)
        return
    if isinstance(stmt, ast.Deliver):
        events.append("validate deliver statement against current function scope.")
        if stmt.value is not None:
            _semantic_expr_events(stmt.value, events)
        return
    if isinstance(stmt, ast.BreakChain):
        events.append("accept break_chain as loop control marker.")
        return
    if isinstance(stmt, ast.ContinueMarch):
        events.append("accept continue_march as loop control marker.")
        return
    events.append(f"inspect semantic rules for {stmt.__class__.__name__}.")


def _semantic_expr_events(expr: ast.Expr, events: list[str]) -> None:
    if isinstance(expr, ast.Literal):
        events.append(f"Literal {expr.value!r} mapped to a realm type.")
        return
    if isinstance(expr, ast.Identifier):
        events.append(f"Resolve identifier {expr.name!r} from the Great Ledger.")
        return
    if isinstance(expr, ast.Binary):
        events.append(f"evaluate binary operator {expr.op!r} over numeric-compatible operands.")
        _semantic_expr_events(expr.left, events)
        _semantic_expr_events(expr.right, events)
        return
    if isinstance(expr, ast.Compare):
        events.append(f"validate comparison operator {expr.op!r} with numeric operands.")
        _semantic_expr_events(expr.left, events)
        _semantic_expr_events(expr.right, events)
        return
    if isinstance(expr, ast.FuncCall):
        events.append(f"resolve function call {expr.name!r} and validate argument expression(s).")
        for arg in expr.args:
            _semantic_expr_events(arg, events)
        return
    events.append(f"evaluate expression node {expr.__class__.__name__}.")


def _token_kind_label(token_type: TokenType) -> str:
    if token_type in {TokenType.COIN, TokenType.STAG, TokenType.ESSENCE, TokenType.SCROLL, TokenType.OATH}:
        return "Data Type"
    if token_type == TokenType.CLAIMS:
        return "Assignment"
    if token_type == TokenType.IDENTIFIER:
        return "Identifier"
    if token_type == TokenType.NUMBER:
        return "Number"
    if token_type == TokenType.STRING:
        return "String"
    if token_type == TokenType.BANG:
        return "Delimiter"
    if token_type in {TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACE, TokenType.RBRACE}:
        return "Grouping"
    return "Keyword"


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

