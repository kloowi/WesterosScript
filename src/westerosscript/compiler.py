from __future__ import annotations

from dataclasses import dataclass, field
import io
from contextlib import redirect_stdout

from westerosscript import ast
from westerosscript.errors import Diagnostic, DiagnosticSink, Severity
from westerosscript.explain import Explainer, NarrationLevel
from westerosscript.lexer import Lexer
from westerosscript.parser import Parser, ParsePanic
from westerosscript.semantic import SemanticAnalyzer
from westerosscript.symbols import GreatLedger
from westerosscript.interpreter import Interpreter
from westerosscript.tokens import Token


def _has_fatal(diags: list[Diagnostic], start: int = 0, end: int | None = None) -> bool:
    stop = len(diags) if end is None else end
    for idx in range(start, stop):
        if diags[idx].severity == Severity.FATAL:
            return True
    return False


@dataclass(frozen=True)
class AnalyzeResult:
    ok: bool
    ledger: GreatLedger | None = None
    output: str | None = None
    ledger_text: str | None = None
    runtime_output: str | None = None
    program: ast.Program | None = None
    token_count: int = 0
    statement_count: int = 0
    lexical_ok: bool = False
    syntax_ok: bool = False
    semantic_ok: bool = False
    tokens: list[Token] = field(default_factory=list)
    lexical_diags_end: int = 0
    syntax_diags_end: int = 0
    diagnostics: list[Diagnostic] = field(default_factory=list)


def analyze_source(
    source: str,
    *,
    narration: NarrationLevel = NarrationLevel.FULL,
    print_tokens: bool = False,
    print_ast: bool = False,
    print_ledger: bool = True,
    filename: str = "<source>",
    capture_output: bool = False,
    run: bool = False,
) -> AnalyzeResult:
    buf = io.StringIO() if capture_output else None
    runtime_out: str | None = None
    token_count = 0
    statement_count = 0
    lexical_ok = False
    syntax_ok = False
    semantic_ok = False
    with redirect_stdout(buf) if buf is not None else _nullcontext():
        diags = DiagnosticSink()
        explainer = Explainer(level=narration)

        lexer = Lexer(source, explainer=explainer, diags=diags, filename=filename)
        tokens = lexer.scan_tokens()
        token_count = len(tokens)
        lex_diags_end = len(diags.diags)
        lexical_ok = not _has_fatal(diags.diags, 0, lex_diags_end)

        if print_tokens:
            explainer.section("TOKENS")
            for t in tokens:
                print(t)

        # Stop if lexical analysis produced fatal errors
        if diags.has_fatal:
            diags.print()
            return AnalyzeResult(
                ok=False,
                ledger=None,
                output=buf.getvalue() if buf is not None else None,
                ledger_text=None,
                runtime_output=None,
                program=None,
                token_count=token_count,
                statement_count=0,
                lexical_ok=lexical_ok,
                syntax_ok=False,
                semantic_ok=False,
                tokens=list(tokens),
                lexical_diags_end=lex_diags_end,
                syntax_diags_end=lex_diags_end,
                diagnostics=list(diags.diags),
            )

        # Parse with error recovery; catch ParsePanic if unrecoverable
        program = None
        try:
            parser = Parser(tokens, explainer=explainer, diags=diags, filename=filename)
            program = parser.parse_program()
            statement_count = len(program.statements)
        except ParsePanic:
            pass

        parse_diags_end = len(diags.diags)
        syntax_ok = not _has_fatal(diags.diags, lex_diags_end, parse_diags_end)

        # Print recovery summary after parsing
        if diags.recovery_count > 0:
            explainer.recovery_summary(
                total_errors=len(diags.diags),
                recovery_count=diags.recovery_count,
                auto_insert_count=diags.auto_insert_count,
                panic_skip_count=diags.panic_skip_count,
            )

        if print_ast and program is not None:
            explainer.section("AST")
            print(program)

        # Stop if syntax analysis produced fatal errors
        if diags.has_fatal:
            diags.print()
            return AnalyzeResult(
                ok=False,
                ledger=None,
                output=buf.getvalue() if buf is not None else None,
                ledger_text=None,
                runtime_output=None,
                program=program,
                token_count=token_count,
                statement_count=statement_count,
                lexical_ok=lexical_ok,
                syntax_ok=syntax_ok,
                semantic_ok=False,
                tokens=list(tokens),
                lexical_diags_end=lex_diags_end,
                syntax_diags_end=parse_diags_end,
                diagnostics=list(diags.diags),
            )

        ledger = GreatLedger()
        sema = SemanticAnalyzer(ledger=ledger, explainer=explainer, diags=diags)
        if program is not None:
            sema.analyze(program)

        semantic_diags_start = parse_diags_end
        semantic_ok = not _has_fatal(diags.diags, semantic_diags_start)

        if run and not diags.has_fatal:
            rt = Interpreter(ledger=ledger).run(program)
            runtime_out = rt.to_text()

        if print_ledger:
            ledger.print()

        diags.print()

    ledger_text = ledger.to_text() if capture_output else None
    return AnalyzeResult(
        ok=not diags.has_fatal,
        ledger=ledger,
        output=buf.getvalue() if buf is not None else None,
        ledger_text=ledger_text,
        runtime_output=runtime_out,
        program=program,
        token_count=token_count,
        statement_count=statement_count,
        lexical_ok=lexical_ok,
        syntax_ok=syntax_ok,
        semantic_ok=semantic_ok,
        tokens=list(tokens),
        lexical_diags_end=lex_diags_end,
        syntax_diags_end=parse_diags_end,
        diagnostics=list(diags.diags),
    )


class _nullcontext:
    def __enter__(self):  # noqa: ANN001
        return None

    def __exit__(self, exc_type, exc, tb):  # noqa: ANN001
        return False

