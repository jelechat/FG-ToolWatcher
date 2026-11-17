# CORE/Watchers/fixami.py
from typing import List

from CORE.Search.WATCHERengine import WatcherEngine

from CORE.Services.user import UserService


class FIXAMIwatcher(WatcherEngine):
    def __init__(self, items: List[dict], config: UserService, progress_callback=None):
        super().__init__("FIXAMI", items, config, progress_callback)
