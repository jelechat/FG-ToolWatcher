# FG-ToolWatcher Desktop Client

DesktopV2 is the primary desktop client UI, built with SolidJS and hosted in a native window by pywebview. Its packaged application uses the official **FG-ToolWatcher** name and icon, without the demo label.

> **Current implementation status:** the UI's product, catalog, profile, and settings services still use mock data. The Python bridge currently provides application information and external-link handling; it is not yet connected to the production database or scraping backend.

## Technology

- Python 3.11+
- [pywebview](https://pywebview.flowrl.com/)
- SolidJS, TypeScript, and Vite
- PyInstaller

## Requirements

- Windows 10 or 11 with the Microsoft Edge WebView2 Runtime
- macOS or Linux with the native dependencies required by pywebview
- Python 3.11 or newer
- Node.js and npm

## Setup

Run these commands from the `GUI/DesktopV2` directory:

```shell
npm ci
python -m venv .venv
```

Activate the virtual environment and install the Python dependencies.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS or Linux:

```shell
source .venv/bin/activate
python -m pip install -r requirements.txt
```

If `requirements.txt` changes, activate the environment and rerun `python -m pip install -r requirements.txt`.

## Run the desktop client

Build the renderer and launch the pywebview window:

```shell
npm run build
python app.py
```

For browser-based renderer development, run `npm run dev`. The pywebview bridge is available when the application is launched through `app.py`.

## Tests and type checking

```shell
npm test
npm run typecheck
```

The optional pywebview smoke check verifies that the interface loads and the bridge is available:

```shell
python smoke.py
```

## Build for the current operating system

From this directory, run:

```shell
python build.py
```

The script builds the renderer, detects the current operating system, and packages the application with PyInstaller. Expected output paths:

```text
Windows: dist/FG-ToolWatcher/FG-ToolWatcher.exe
macOS:   dist/FG-ToolWatcher.app
Linux:   dist/FG-ToolWatcher/FG-ToolWatcher
```

PyInstaller is not a cross-compiler. Build on each target operating system; separate Windows, macOS, and Linux CI runners can produce the corresponding packages.

## Project layout

```text
DesktopV2/
├── api.py                         # Python methods exposed to the renderer
├── app.py                         # pywebview application entry point
├── build.py                       # Cross-platform build entry point
├── build/icon.png                 # Application icon
├── src/
│   ├── renderer/                  # SolidJS interface and service layer
│   └── shared/                    # Shared TypeScript domain types
├── tests/                         # Vitest unit tests
├── web/                           # Generated production renderer
├── package.json
└── requirements.txt
```
