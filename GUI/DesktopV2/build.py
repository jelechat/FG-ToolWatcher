"""Build the FG-ToolWatcher desktop client for the current operating system."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
APP_NAME = "FG-ToolWatcher"


def build_renderer() -> None:
    """Build the SolidJS renderer into the web/ directory."""
    npm = shutil.which("npm") or shutil.which("npm.cmd")
    if npm is None:
        raise RuntimeError("npm was not found. Install Node.js and npm first.")

    if os.name == "nt":
        subprocess.run("npm run build", cwd=ROOT, check=True, shell=True)
    else:
        subprocess.run([npm, "run", "build"], cwd=ROOT, check=True)


def package_application() -> Path:
    """Package the app with PyInstaller for the current host OS."""
    arguments = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--name",
        APP_NAME,
        "--icon",
        str(Path("build") / "icon.png"),
        "--add-data",
        f"web{os.pathsep}web",
    ]

    if sys.platform in {"win32", "darwin"}:
        arguments.append("--windowed")

    arguments.append("app.py")
    subprocess.run(arguments, cwd=ROOT, check=True)

    if sys.platform == "win32":
        return ROOT / "dist" / APP_NAME / f"{APP_NAME}.exe"
    if sys.platform == "darwin":
        return ROOT / "dist" / f"{APP_NAME}.app"
    return ROOT / "dist" / APP_NAME / APP_NAME


def platform_name() -> str:
    if sys.platform == "win32":
        return "Windows"
    if sys.platform == "darwin":
        return "macOS"
    if sys.platform.startswith("linux"):
        return "Linux"
    return sys.platform


def main() -> int:
    if sys.platform not in {"win32", "darwin"} and not sys.platform.startswith("linux"):
        print(f"Unsupported build platform: {sys.platform}", file=sys.stderr)
        return 2

    try:
        build_renderer()
        output = package_application()
    except (OSError, subprocess.CalledProcessError, RuntimeError) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        return 1

    print(f"Build complete for {platform_name()}: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
