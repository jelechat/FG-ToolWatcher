# CORE/Watchers/clabots.py
from typing import List

from CORE.Search.WATCHERengine import WatcherEngine

from CORE.Services.user import UserService


class CLABOTSwatcher(WatcherEngine):
    def __init__(self, items: List[dict], config: UserService, progress_callback=None):
        super().__init__("CLABOTS", items, config, progress_callback)
