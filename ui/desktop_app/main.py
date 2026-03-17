from __future__ import annotations

import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ui.desktop_app.bridge import WesterosApi  # noqa: E402


def main() -> None:
    api = WesterosApi()

    root = tk.Tk()
    root.title("WesterosScript")
    root.geometry("1000x700")

    outer = ttk.Frame(root, padding=12)
    outer.pack(fill=tk.BOTH, expand=True)

    topbar = ttk.Frame(outer)
    topbar.pack(fill=tk.X)

    title = ttk.Label(topbar, text="WesterosScript Compiler", font=("Noto Serif", 14, "bold"))
    title.pack(side=tk.LEFT)

    analyze_btn = ttk.Button(topbar, text="Analyze")
    analyze_btn.pack(side=tk.RIGHT)

    panes = ttk.PanedWindow(outer, orient=tk.VERTICAL)
    panes.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

    editor = ScrolledText(panes, wrap=tk.NONE, font=("JetBrains Mono", 11))
    editor.insert(
        "1.0",
        'coin gold claims 100!\nscroll name claims "Arya"!\nraven gold!\n',
    )
    panes.add(editor, weight=3)

    output = ScrolledText(panes, wrap=tk.WORD, font=("JetBrains Mono", 10), height=12)
    output.insert("1.0", "(ready)\n")
    panes.add(output, weight=2)

    def run_analyze() -> None:
        src = editor.get("1.0", tk.END)
        res = api.analyze(src, "full")
        output.delete("1.0", tk.END)
        output.insert("1.0", res.get("output", ""))

    analyze_btn.configure(command=run_analyze)
    root.mainloop()


if __name__ == "__main__":
    main()

