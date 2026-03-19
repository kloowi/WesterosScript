from __future__ import annotations

from dataclasses import dataclass
import io
from contextlib import redirect_stdout

from westerosscript.errors import DiagnosticSink
from westerosscript.explain import Explainer, NarrationLevel
from westerosscript.lexer import Lexer
from westerosscript.parser import Parser, ParsePanic
from westerosscript.semantic import SemanticAnalyzer
from westerosscript.symbols import GreatLedger
from westerosscript.interpreter import Interpreter


@dataclass(frozen=True)
class AnalyzeResult:
    ok: bool
    ledger: GreatLedger | None = None
    output: str | None = None
    ledger_text: str | None = None
    runtime_output: str | None = None


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
    with redirect_stdout(buf) if buf is not None else _nullcontext():
        diags = DiagnosticSink()
        explainer = Explainer(level=narration)

        lexer = Lexer(source, explainer=explainer, diags=diags, filename=filename)
        tokens = lexer.scan_tokens()

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
            )

        # Parse with error recovery; catch ParsePanic if unrecoverable
        program = None
        try:
            parser = Parser(tokens, explainer=explainer, diags=diags, filename=filename)
            program = parser.parse_program()
        except ParsePanic:
            pass

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
            )

        ledger = GreatLedger()
        sema = SemanticAnalyzer(ledger=ledger, explainer=explainer, diags=diags)
        if program is not None:
            sema.analyze(program)

        if run and not diags.has_fatal:
            rt = Interpreter(ledger=ledger).run(program)
            runtime_out = rt.to_text()

        if print_ledger:
            ledger.print()

        diags.print()

    ledger_text = ledger.to_text()
    return AnalyzeResult(
        ok=not diags.has_fatal,
        ledger=ledger,
        output=buf.getvalue() if buf is not None else None,
        ledger_text=ledger_text if capture_output else None,
        runtime_output=runtime_out,
    )


class _nullcontext:
    def __enter__(self):  # noqa: ANN001
        return None

    def __exit__(self, exc_type, exc, tb):  # noqa: ANN001
        return False

