from __future__ import annotations

import argparse
import sys

from westerosscript.compiler import analyze_source
from westerosscript.explain import NarrationLevel


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="wss", description="WesterosScript compiler (analysis-only).")
    sub = p.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Lex + parse + semantic analysis.")
    analyze.add_argument("path", help="Path to a .wss/.ws source file.")
    analyze.add_argument(
        "--narration",
        choices=[lvl.value for lvl in NarrationLevel],
        default=NarrationLevel.FULL.value,
        help="Narration verbosity.",
    )
    analyze.add_argument("--print-tokens", action="store_true", help="Print tokens after lexing.")
    analyze.add_argument("--print-ast", action="store_true", help="Print AST after parsing.")
    analyze.add_argument("--print-ledger", action="store_true", default=True, help="Print symbol table.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.command == "analyze":
        try:
            with open(args.path, "r", encoding="utf-8") as f:
                source = f.read()
        except OSError as e:
            print(f"[FATAL] Could not read file: {e}", file=sys.stderr)
            return 2

        result = analyze_source(
            source,
            narration=NarrationLevel(args.narration),
            print_tokens=args.print_tokens,
            print_ast=args.print_ast,
            print_ledger=args.print_ledger,
            filename=args.path,
        )
        return 0 if result.ok else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

