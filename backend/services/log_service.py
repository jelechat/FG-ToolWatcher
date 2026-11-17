# backend/services/log_service.py
# by LECHAT Jérôme; creation date: 09/2025, last edit: 11/2026

# INTERNAL(S)
import logging
import sys
from datetime import datetime

# MODULE(S)
from backend.services.bootstrap_service import _IS_FROZEN, LOGS_SUBFOLDER


class LogService:
    """
    Centralized logging configuration service.

    Responsible for initializing and routing application-wide logs based on
    the execution context (file logging for frozen binaries vs. stdout for dev mode).
    """

    LOG_FORMAT: str = "[%(asctime)s] [%(levelname)s] (%(name)s) - %(message)s"
    QUIET_LOGGERS: tuple[str, ...] = (
        "requests",
        "urllib3",
        "cloudscraper",
        "curl_cffi",
        "asyncio",
    )

    @classmethod
    def setup(cls, log_level: int = logging.INFO) -> None:
        """
        Configures the root logger for the entire application.

        This method should be called ONCE at application startup.

        Args:
            log_level (int): Logging threshold level (default: logging.INFO).
        """
        formatter = logging.Formatter(cls.LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")

        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        if root_logger.hasHandlers():
            root_logger.handlers.clear()

        level_name = logging.getLevelName(log_level)

        if _IS_FROZEN: # EXEC MODE: file output (.txt)
            try:
                LOGS_SUBFOLDER.mkdir(parents=True, exist_ok=True)

                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                log_file = LOGS_SUBFOLDER / f"session_{timestamp}.txt"

                file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)

                root_logger.info(f"--- Starting FG-ToolWatcher (EXE Mode | Level: {level_name}) ---")

            except Exception as e:
                sys.stderr.write(f"Unable to initialize log file at {LOGS_SUBFOLDER}: {e}\n")

        else: # DEV MODE: console output
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

            root_logger.info(f"--- Starting FG-ToolWatcher (DEV Mode | Level: {level_name}) ---")

        # silence chatty third-party libraries
        for logger_name in cls.QUIET_LOGGERS:
            logging.getLogger(logger_name).setLevel(logging.WARNING)
