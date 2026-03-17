from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def test_valid_code_analyzes_ok() -> None:
    p = _run([sys.executable, "-m", "westerosscript.cli", "analyze", "examples/valid.wss", "--narration", "off"])
    assert p.returncode == 0
    assert "THE GREAT LEDGER OF THE REALM" in p.stdout
    assert "gold" in p.stdout


def test_syntax_error_missing_bang_recovers() -> None:
    p = _run(
        [sys.executable, "-m", "westerosscript.cli", "analyze", "examples/syntax_error_missing_bang.wss", "--narration", "off"]
    )
    # Missing bang is a warning + recovery; should still be ok (no fatal).
    assert p.returncode == 0
    assert "The decree lacks the sacred ending rune '!'" in p.stdout


def test_semantic_error_type_mismatch_fails() -> None:
    p = _run(
        [sys.executable, "-m", "westerosscript.cli", "analyze", "examples/semantic_error_type_mismatch.wss", "--narration", "off"]
    )
    assert p.returncode == 1
    assert "[FATAL BETRAYAL]" in p.stdout


def test_capture_output_mode_includes_ledger() -> None:
    from westerosscript.compiler import analyze_source
    from westerosscript.explain import NarrationLevel

    res = analyze_source("coin gold claims 100!\n", narration=NarrationLevel.OFF, capture_output=True)
    assert res.ok is True
    assert res.output is not None
    assert "THE GREAT LEDGER OF THE REALM" in res.output

