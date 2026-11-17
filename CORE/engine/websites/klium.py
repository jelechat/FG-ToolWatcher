# CORE/Watchers/klium.py
from typing import List

from CORE.Search.WATCHERengine import WatcherEngine

from CORE.Services.user import UserService


class KLIUMwatcher(WatcherEngine):
    def __init__(self, items: List[dict], config: UserService, progress_callback=None):
        super().__init__("KLIUM", items, config, progress_callback)
