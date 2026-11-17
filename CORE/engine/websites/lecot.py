# CORE/Watchers/lecot.py
from typing import List

from CORE.Search.WATCHERengine import WatcherEngine

from CORE.Services.user import UserService


class LECOTwatcher(WatcherEngine):
    def __init__(self, items: List[dict], config: UserService, progress_callback=None):
        super().__init__("LECOT", items, config, progress_callback)
