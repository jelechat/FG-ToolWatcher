# backend/services/translator.py
# by LECHAT Jérôme; creation date: 09/2025, latest edit: 11/2026

# INTERNAL(S)
import json
import logging
from pathlib import Path

# MODULE(S)
from backend.services.bootstrap_service import ASSETS_FOLDER

LOG = logging.getLogger(__name__)


class TranslatorService:
    """
    Internationalization (i18n) service.

    Responsible for loading language-specific JSON dictionaries and
    providing translated strings for the graphical user interface.
    Includes an automatic fallback mechanism to a default language
    if the requested file is missing or corrupted.
    """

    FALLBACK_LANG = "fr"

    def __init__(self) -> None:
        """
        Initializes the TranslatorService with empty translations.
        The default language is set to the class fallback language.
        """

        # === internal variable(s) ===
        self.current_lang: str = self.FALLBACK_LANG # default language
        self.translations: dict[str, str] = {}

    def __str__(self) -> str:
        return f"[TranslatorService]: current user's language is: {self.current_lang}."


    # === Public Method(s) ===
    def load_language(self, lang_code: str, _is_fallback: bool = False) -> None:
        """
        Loads the translations from the corresponding {lang_code}.json file.
        If the file is missing or unreadable, falls back to FALLBACK_LANG.

        Args:
            lang_code (str): The language code to load (e.g., 'fr', 'en').
            _is_fallback (bool): Internal flag to prevent infinite fallback recursion.
        """

        file_path = Path(ASSETS_FOLDER) / "i18n" / f"{lang_code}.json"

        # checking existence
        if not file_path.exists():
            LOG.warning(f"Language file '{lang_code}.json' not found at: {file_path}.")
            self._handle_fallback(lang_code, _is_fallback)
            return

        # fetching and parsing
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
            self.current_lang = lang_code
            LOG.debug(f"Language '{lang_code}' successfully loaded ({len(self.translations)} keys).")

        except Exception as e:
            LOG.error(f"The language file '{lang_code}.json' is corrupted or unreadable: {e}")
            self._handle_fallback(lang_code, _is_fallback)

    def get(self, key: str, fallback: str = "") -> str:
        """
        Fetches a specific translation for a given key.

        Args:
            key (str): The JSON key for the requested translation string.
            fallback (str): Optional string to return if the key doesn't exist.

        Returns:
            str: The translated string, the fallback value, or the key itself if neither exists.
        """
        return self.translations.get(key, fallback or key)


    # === Private Method(s) ===
    def _handle_fallback(self, failed_lang: str, is_already_fallback: bool) -> None:
        """
        Internal method to manage the fallback logic safely.
        """

        if is_already_fallback:
            LOG.critical(f"Fallback language '{self.FALLBACK_LANG}' is also missing/corrupted. GUI strings will be empty.")
            return

        if failed_lang != self.FALLBACK_LANG:
            LOG.info(f"Automatically switching to the fallback language ('{self.FALLBACK_LANG}').")
            self.load_language(self.FALLBACK_LANG, _is_fallback=True)
