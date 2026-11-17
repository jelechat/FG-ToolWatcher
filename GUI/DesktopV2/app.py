"""Point d'entrée pywebview de FG-ToolWatcher."""

from pathlib import Path

import webview

from api import Api


BASE_DIR = Path(__file__).resolve().parent


def create_window():
    """Crée et renvoie la fenêtre principale avec toute sa configuration."""
    return webview.create_window(
        title="FG-ToolWatcher",
        url=str(BASE_DIR / "web" / "index.html"),
        js_api=Api(),
        width=1440,
        height=900,
        min_size=(1024, 640),
        resizable=False,
        background_color="#1E1E1E",
    )


def main() -> None:
    window = create_window()
    _ = window
    webview.start(http_server=True, debug=False)


if __name__ == "__main__":
    main()
