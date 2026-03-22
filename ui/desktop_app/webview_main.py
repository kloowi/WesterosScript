from __future__ import annotations

import sys
from pathlib import Path

import webview

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ui.desktop_app.bridge import WesterosApi  # noqa: E402


def main() -> None:
    assets_dir = Path(__file__).resolve().parent / "assets"
    index_html = (assets_dir / "index.html").as_uri()

    api = WesterosApi()
    webview.create_window(
        "WesterosScript ",
        index_html,
        js_api=api,
        fullscreen=True,
        width=1024,
        height=768,
        background_color="#1a1007",
    )
    webview.start()


if __name__ == "__main__":
    main()

