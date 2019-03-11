# File Usage:
#
# Author:

from datetime import datetime
import threading


class SignInCache:
    _instance_lock = threading.Lock()

    def __init__(self):
        self._cache = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(SignInCache, "_instance"):
            with SignInCache._instance_lock:
                if not hasattr(SignInCache, "_instance"):
                    SignInCache._instance = object.__new__(cls)
        return SignInCache._instance

    def __contains__(self, item):
        return item in self._cache

    def update_cache(self, key, signin):
        if key not in self._cache or not self.is_today(signin[3]):
            self._cache[key] = signin

    def is_today(self, sign_in_date):
        if sign_in_date == datetime.now().strftime("%Y-%m-%d"):
            return True
        else:
            return False

    def get_signin_cache(self):
        return self._cache

    def reset_signin_cache(self):
        self._cache = {}
