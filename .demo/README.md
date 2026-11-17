# FG-ToolWatcher Demo

A desktop UI prototype for FG-ToolWatcher, built with SolidJS and hosted in a native window by pywebview. The packaged application is explicitly branded **FG-ToolWatcher — DEMO** and is not the production client.

> **Demo only:** product, catalog, profile, and settings data is mocked in the renderer. This project is not connected to the production database or scraping backend. Price updates and email delivery are simulated.

## Features

- Product search and price comparison using sample retailer data
- Watched-product catalog and dashboard filters
- Settings and profile screens
- English, French, and Dutch interface translations
- A pywebview bridge for application information and external links

## Technology

- Python 3.11+
- [pywebview](https://pywebview.flowrl.com/)
- SolidJS, TypeScript, and Vite
- PyInstaller

## Project layout

```text
.demo/
├── api.py                         # Python methods exposed to the renderer
├── app.py                         # pywebview application entry point
├── build.py                       # Cross-platform build entry point
├── build/
│   ├── generate_icon.py           # Generates the demo PNG and multi-size ICO
│   └── icon-base.png              # Source image for the application icon
├── src/
│   ├── renderer/                  # SolidJS interface and mock services
│   └── shared/                    # Shared TypeScript domain types
├── tests/                         # Vitest unit tests
├── web/                           # Generated production renderer
├── package.json
└── requirements.txt
```

## Requirements

- Windows 10 or 11 with the Microsoft Edge WebView2 Runtime
- macOS or Linux with the native dependencies required by pywebview
- Python 3.11 or newer
- Node.js and npm

## Setup

Run these commands from the `.demo` directory:

```shell
npm ci
python -m venv .venv
```

Activate the virtual environment, then install the Python dependencies:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS or Linux, activate the environment with:

```shell
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Whenever `requirements.txt` changes, update an existing virtual environment by activating it and running `python -m pip install -r requirements.txt` again. This installs build dependencies such as Pillow, which is used to generate the demo icon.

## Run the desktop demo

Build the renderer and launch the pywebview window:

```shell
npm run build
python app.py
```

For browser-based renderer development, use `npm run dev`. The pywebview bridge is available when the app is launched through `app.py`.

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

After setup, run this single command from `.demo`:

```shell
python build.py
```

If icon generation fails with `ModuleNotFoundError: No module named 'PIL'`, install or update the Python dependencies in the active environment:

```shell
python -m pip install -r requirements.txt
```

The script builds the renderer, regenerates the icon with its red `DEMO` ribbon, detects the current operating system, and packages the app with PyInstaller. Expected outputs:

```text
Windows: dist/FG-ToolWatcher-Demo/FG-ToolWatcher-Demo.exe
macOS:   dist/FG-ToolWatcher-Demo.app
Linux:   dist/FG-ToolWatcher-Demo/FG-ToolWatcher-Demo
```

The window title displays `FG-ToolWatcher — DEMO`, and the application icon carries the same demo label.

PyInstaller is not a cross-compiler: it builds for the operating system on which it runs. To produce releases for multiple operating systems, run `python build.py` on each target OS, such as through separate Windows, macOS, and Linux CI runners.

## Current limitations

- There is no production backend or database connection.
- Product search and price data come from fixed mock fixtures.
- Scraping, price refresh, and email delivery are not performed.
- The Python API currently exposes application information and external-link handling only.
- Native menus and menu-driven navigation are not implemented.
