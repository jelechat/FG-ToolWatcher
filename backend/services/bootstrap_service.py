# backend/services/bootstrap_service.py
# by LECHAT Jérôme; creation date: 09/2025, last edit: 11/2026

# INTERNAL(S)
import os
import sys
from pathlib import Path

# === Application Identity ===
APP_NAME: str = "FG-ToolWatcher"
VERSION: float = 1.0

# === internal variable(s) ===
_OS = sys.platform.lower()
_IS_FROZEN = getattr(sys, 'frozen', False)

if not any(_OS.startswith(p) for p in ("win", "linux", "darwin")):
    raise RuntimeError(f"Unsupported operating system: {_OS}.")


# === Public Method(s) ===
def make_dirs() -> None:
    """
    Creates all required user directories in the OS-specific AppData folder.
    Must be called during application startup.
    """
    folders_to_create: tuple[Path, ...] = (
        CONFIG_SUBFOLDER,
        DATA_SUBFOLDER_SOURCE,
        LOGS_SUBFOLDER,
        RESULTS_SUBFOLDER_TEMP
    )

    for folder in folders_to_create:
        folder.mkdir(parents=True, exist_ok=True)


# === Private Method(s) ===
def _get_user_data_dir(app_name: str) -> Path:
    """Resolves the OS-specific local application data directory."""
    home = Path.home()

    if _OS.startswith("win"): # Windows: %LOCALAPPDATA% (cache, local datas, logs)
        local_app_data = os.environ.get("LOCALAPPDATA", home / "AppData" / "Local")
        return Path(local_app_data) / app_name

    elif _OS.startswith("darwin"): # macOS: ~/Library/Application Support
        return home / "Library" / "Application Support" / app_name

    else: # Linux: XDG Base Directory Specification ($XDG_DATA_HOME or ~/.local/share)
        xdg_data = os.environ.get("XDG_DATA_HOME", home / ".local" / "share")
        return Path(xdg_data) / app_name


# === path resolution ===
if _IS_FROZEN:
    PROJECT_ROOT: Path = Path(sys.executable).parent
else:
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]

_SYSTEM_ROOT: Path = Path(getattr(sys, '_MEIPASS', PROJECT_ROOT))

# === system paths (Read-Only) ===
RESOURCES_FOLDER: Path = _SYSTEM_ROOT / "CORE" / "__RESOURCES"
SECRETS_FOLDER: Path = _SYSTEM_ROOT / "CORE" / "__SECRETS"
AI_FOLDER: Path = _SYSTEM_ROOT / "CORE" / "AI"
DATABASE_FOLDER: Path = _SYSTEM_ROOT / "CORE" / "Database"
SEARCH_FOLDER: Path = _SYSTEM_ROOT / "CORE" / "Search"
SERVICE_FOLDER: Path = _SYSTEM_ROOT / "CORE" / "Service"
ASSETS_FOLDER: Path = _SYSTEM_ROOT / "GUI" / "__assets"

# === user paths (Read/Write) ===
USER_FOLDER: Path = _get_user_data_dir(APP_NAME)
CONFIG_SUBFOLDER: Path = USER_FOLDER / "CONFIG"
DATA_SUBFOLDER: Path = USER_FOLDER / "DATA"
DATA_SUBFOLDER_SOURCE: Path = DATA_SUBFOLDER / "SOURCE"
LOGS_SUBFOLDER: Path = USER_FOLDER / "LOGS"
RESULTS_SUBFOLDER: Path = USER_FOLDER / "RESULTS"
RESULTS_SUBFOLDER_TEMP: Path = RESULTS_SUBFOLDER / "TEMP"

CATALOG_CONFIG_PATH: Path = CONFIG_SUBFOLDER / "catalog.json"
USER_CONFIG_PATH: Path = CONFIG_SUBFOLDER / "settings.json"
