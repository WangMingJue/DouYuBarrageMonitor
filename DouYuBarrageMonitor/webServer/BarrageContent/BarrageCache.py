# File Usage:
#
# Author:
import threading


class BarrageCache:
    _instance_lock = threading.Lock()

    def __init__(self):
        self._cache = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(BarrageCache, "_instance"):
            with BarrageCache._instance_lock:
                if not hasattr(BarrageCache, "_instance"):
                    BarrageCache._instance = object.__new__(cls)
        return BarrageCache._instance

    def __contains__(self, item):
        return item in self._cache

    def update_cache(self, key, key2):
        if key not in self._cache:
            self._cache[key] = [key2, 1]
        else:
            self._cache[key][1] += 1

    def get_barrage_cache(self):
        return self._cache

    def reset_barrage_cache(self):
        self._cache = {}
