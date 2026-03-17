from __future__ import annotations

from ui.desktop_app.bridge import WesterosApi


def main() -> None:
    api = WesterosApi()
    res = api.analyze('coin gold claims 100!\nscroll name claims "Arya"!\n', "off")
    print(res["output"])


if __name__ == "__main__":
    main()

