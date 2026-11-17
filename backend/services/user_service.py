# backend/services/user.py
# by LECHAT Jérôme; creation date: 09/2025, last edit: 10/2026

# INTERNAL(S)
import json
import logging
from pathlib import Path

LOG = logging.getLogger(__name__)


class UserService:
    """
    Manages application settings (user preferences).

    This service ensures configuration files exist with valid default settings
    and provides unified get/set methods for application-wide use.
    """

    DEFAULT_CONFIG: dict[str, str | int | list[str] | None] = {
        'user_firstname': "",
        'user_lastname': "",
        'user_mail': "",
        'websites_to_watch': [],
        'websites_cache_duration_days': 1,
        'system_language': "FR"
    }

    def __init__(self, user_config_path: str | Path) -> None:
        """
        Initializes the UserService.

        Args:
            user_config_path (str | Path): Path to the JSON file storing user preferences.
        """

        # === variable(s) ===
        self.user_config_path = Path(user_config_path)

        # === internal variable(s) ===
        self.user_config: dict[str, str | int | list[str] | None] = self.DEFAULT_CONFIG.copy() # default settings

        # loading/setting user default settings at initialization (first boot)
        self.load()


    # === Public Method(s) ===
    def load(self) -> None:
        """
        Loads user settings from its respective JSON file.
        NOTE: Creates files or adds missing keys if necessary.
        """
        config_loaded = False

        if self.user_config_path.exists():
            try:
                with open(self.user_config_path, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
                    self.user_config.update(loaded_data) # update the default dictionary with the data that was read
                    config_loaded = True
            except Exception as e:
                LOG.error(f"Corrupted or unreadable configuration file ({self.user_config_path}) : {e}")
                # if an error occurs, `self.user_config` retains its default values

        # checking for Missing Keys
        updated = False
        for key, default_value in self.DEFAULT_CONFIG.items():
            if key not in self.user_config:
                self.user_config[key] = default_value
                updated = True

        if not config_loaded:
            LOG.info(f"Configuration file not found. Creating default settings: {self.user_config_path}.")
            self.save()
        elif updated:
            LOG.info("Configuration update (addition of new default keys).")
            self.save()

    def save(self) -> None:
        """
        Saves the current user settings to the configuration file.
        """

        try:
            # Création du dossier parent s'il n'existe pas
            self.user_config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.user_config_path, "w", encoding="utf-8") as f:
                json.dump(self.user_config, f, indent=4, ensure_ascii=False)

            LOG.debug(f"Successfully saved user preferences in {self.user_config_path}.")

        except Exception as e:
            LOG.exception(f"Critical error during the user preferences save in {self.user_config_path} : {e}")

    def get(self, key: str, default: str | int | list[str] | None = None) -> str | int | list[str] | None:
        """
        Accesses a configuration value from user settings.

        Args:
            key (str): The configuration key to retrieve.
            default (str | int | list[str]): Fallback value if the key does not exist.

        Returns:
            str | int | list[str] | None: The configuration value or the fallback default.
        """
        return self.user_config.get(key, default)

    def set(self, key: str, value: str | int | list[str] | None) -> None:
        """
        Modifies a user setting value and saves the configuration immediately.

        Args:
            key (str): The configuration key to modify.
            value (ConfigValue): The new value to set.
        """
        self.user_config[key] = value
        self.save()
