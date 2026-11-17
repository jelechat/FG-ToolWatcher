"""API JS exposée à pywebview sous `window.pywebview.api`."""

import platform
import re
import webbrowser


class Api:
    """Contrat minimal compatible avec l'ancien bridge Electron."""

    _URL_RE = re.compile(r"^https?://", re.IGNORECASE)

    def get_info(self) -> dict:
        """Renvoie les métadonnées de l'application."""
        return {
            "version": "0.1.0",
            "platform": platform.system(),
            "arch": platform.machine(),
            "electron": "pywebview",
            "chrome": "WebView2",
            "node": "",
        }

    def open_external(self, url: str) -> bool:
        """Ouvre une URL externe si elle est HTTP(S)."""
        if not isinstance(url, str) or not self._URL_RE.match(url):
            return False
        try:
            webbrowser.open(url)
            return True
        except Exception:  # pragma: no cover - défense
            return False
