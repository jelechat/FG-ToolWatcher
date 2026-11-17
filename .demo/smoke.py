"""Test de lancement automatique : rendu SPA + réponse du bridge, puis fermeture."""

import sys
import time
import traceback

import webview

from app import create_window


PROBE_JS = (
    "document.querySelector('#root') !== null"
    " && document.querySelector('#root').children.length > 0"
    " && typeof window.pywebview.api.open_external === 'function'"
    " && typeof window.toolwatcher.openExternal === 'function'"
)


def main() -> int:
    try:
        window = create_window()
        state = {"ok": False, "diag": ""}

        def probe() -> None:
            deadline = time.monotonic() + 10.0
            while time.monotonic() < deadline:
                try:
                    value = window.evaluate_js(PROBE_JS)
                except Exception as exc:  # pragma: no cover - diagnostic
                    value = f"<exception: {exc}>"
                if value is True:
                    state["ok"] = True
                    window.destroy()
                    return
                state["diag"] = (
                    f"probe={value!r}; url={getattr(window, 'url', '?')}"
                )
                time.sleep(0.25)
            if not state["ok"]:
                window.destroy()

        webview.start(func=probe, http_server=True, debug=False)

        if state["ok"]:
            return 0
        print(f"Smoke failed: {state['diag']}", file=sys.stderr)
        return 1
    except Exception:
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
