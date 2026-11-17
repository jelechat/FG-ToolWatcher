# backend/utils/formatters.py
# by LECHAT Jérôme; creation date: 10/2026, last edit: 10/2026
import logging

# EXTERNAL
import requests

LOG = logging.getLogger(__name__)


def check_internet_connection(self, timeout: int = 5) -> bool:
    try:
        response = requests.head("https://dns.google", timeout=timeout)
        if response.status_code >= 200:
            LOG.info("Internet connection check successful.")
            return True
    except (requests.ConnectionError, requests.Timeout) as e:
        LOG.exception(f"Internet connection check failed: {e}")

    return False
