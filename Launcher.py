# Launcher.py
# by LECHAT Jérôme; creation date: 09/2025, latest edit: 11/2026

# INTERNAL(S)
import logging
import sys

# EXTERNAL(S)
from PySide6.QtWidgets import QApplication

# SERVICE(S)
from backend.services.bootstrap_service import *
from backend.services.log_service import setup_logging
from backend.services.translator_service import TranslatorService
from backend.services.user_service import UserService

# GUI
from GUI.Desktop.Client import WatcherGUI

LOG = logging.getLogger(__name__)


def RUN_GUI():
    """
    Launches the FG-ToolWatcher application.
    Sets up logging, initializes configuration services, and starts the GUI.
    """
    LOG.debug("UI starting...")

    try:
        # === Service(s) initialization ===
        user_settings = UserService(user_config_path=USER_CONFIG_PATH) # User settings service
        LOG.debug("UserService initialized.")

        system_languages = TranslatorService() # Language system service
        LOG.debug("TranslatorService initialized.")

        # === SETUP ===
        app = QApplication(sys.argv)
        app.setStyleSheet("* { outline: 0; }")

        window = WatcherGUI(settings=user_settings, languages=system_languages)
        window.show()

        LOG.debug("Window show.")

        # === START ===
        APP = app.exec()
        LOG.debug(f"Exiting app with the following code: {APP}")
        sys.exit(APP)

    except Exception as e:
        LOG.exception(f"A critical error occured on GUI mode: {e}")
        sys.exit(1)


# ========================
#          MAIN
# ========================
if __name__ == "__main__":

    ARGS = sys.argv[1:]

    make_dirs()

    # --- LOGGING configuration ---
    if "--debug" in ARGS:
        LEVEL = logging.DEBUG
        ARGS.remove("--debug")
    else:
        LEVEL = logging.INFO

    setup_logging(log_level=LEVEL)
    LOG = logging.getLogger(__name__)

    # --- Router ---
    if len(ARGS) == 0:
        RUN_GUI()
        sys.exit(0)

    else:
        print(f"Invalid / Unrecognized arguments: {ARGS}")
        print("---------------------------------------------")
        print("Usage(s):")
        print("1) python Launcher.py [--debug]")
        print("---------------------------------------------")
        sys.exit(1)
