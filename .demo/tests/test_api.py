"""Tests unitaires de l'API pywebview."""

import platform
import unittest
from unittest.mock import patch

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api import Api


class TestApi(unittest.TestCase):
    def setUp(self) -> None:
        self.api = Api()

    def test_get_info_structure(self) -> None:
        info = self.api.get_info()
        self.assertIsInstance(info, dict)
        self.assertEqual(info["version"], "0.1.0")
        self.assertEqual(info["platform"], platform.system())
        self.assertEqual(info["arch"], platform.machine())
        self.assertEqual(info["electron"], "pywebview")
        self.assertEqual(info["chrome"], "WebView2")
        self.assertEqual(info["node"], "")

    @patch("api.webbrowser.open")
    def test_open_external_accepts_http(self, open_mock) -> None:
        self.assertTrue(self.api.open_external("https://example.com"))
        open_mock.assert_called_once_with("https://example.com")

    @patch("api.webbrowser.open")
    def test_open_external_accepts_https_uppercase(self, open_mock) -> None:
        self.assertTrue(self.api.open_external("HTTPS://EXAMPLE.COM"))
        open_mock.assert_called_once_with("HTTPS://EXAMPLE.COM")

    @patch("api.webbrowser.open")
    def test_open_external_rejects_invalid_values(self, open_mock) -> None:
        invalid = [
            "file:///etc/passwd",
            "javascript:alert(1)",
            "file:///C:/x",
            "data:text/html,x",
            "ftp://x",
            "",
            None,
            123,
        ]
        for value in invalid:
            with self.subTest(value=value):
                self.assertFalse(self.api.open_external(value))
        open_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
