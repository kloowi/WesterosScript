from __future__ import annotations

import json
import re
import textwrap
from dataclasses import asdict, dataclass, fields, is_dataclass

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

