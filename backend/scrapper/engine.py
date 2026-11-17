# backend/scrapper/engine.py
import json
import logging
import os
import random
import time

import cloudscraper
from CORE.engine.components.websites import SiteConfig

LOG = logging.getLogger(__name__)


class WatcherEngine:
    def __init__(self, website: str, item: str) -> None:
        # === variable(s) ===
        self.item = item
        self.website = website

        self.site_config = SiteConfig(file=os.path.join("CORE", "__RESOURCES", "websites.json"), website=website).load()

        # === internal variable(s) ===
        self.SITEMAP_INDEX = self.site_config.get("sitemap_index") or ""
        self.SITEMAP_URLS = list(self.site_config.get("sitemap_manual") or [])

        self.DOMAIN = self.site_config.get("domain", "")
        self.SELECTORS = self.site_config.get("selectors", {})
        self.VAT_RATE = float(self.site_config.get("vat_rate", 1.21))

        self.DB = None
        self.PARSER = None
        self.REQUESTS = None

        # === parameter(s) & option(s) setup for Cloudscraper ===
        self.REQUESTS_HEADERS = {
            'Referer': f'https://www.{self.DOMAIN}/' if self.DOMAIN else '',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive'
        }

    def __str__(self) -> str:
        return f"[WatcherEngine]: using {self.website} as 'Location' with {self.item} as 'Target'."


    # === Public Method(s) ===
    def requests(self):
        if self.REQUESTS is None:
            self.REQUESTS = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
        self.REQUESTS.headers.update(self.REQUESTS_HEADERS)

        return self.REQUESTS


# === PLAYGROUND ===
if __name__ == "__main__":
    test = WatcherEngine(website="FIXAMI", item="something")
    print(test)
