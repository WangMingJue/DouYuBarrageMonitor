import requests
from django.conf import settings
import json
import time


class AccessTokenManager:
    def __init__(self):
        self._access_token = None
        self._expires_in = 0
        self._refresh_time = 0

    def _refresh_access_token(self):
        self._refresh_time = time.time()
        response = requests.get(
            "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}".format(
                settings.APPID, settings.APPSECRET))
        response = json.loads(response.content)
        self._access_token = response['access_token']
        self._expires_in = 7200

    def get_access_token(self):
        if time.time() - self._refresh_time > self._expires_in:
            self._refresh_access_token()
        return self._access_token
