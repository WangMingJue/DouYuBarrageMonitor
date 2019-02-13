import threading

from django.conf import settings

from webServer.models import Barrage
from LogContent.MyLog import get_logger
from datetime import datetime
import requests


class SaveBarrageThread(threading.Thread):

    def __init__(self, douyu_id, room_id, douyu_name, barrage_content, user_level, user_image):
        threading.Thread.__init__(self)
        self.douyu_id = douyu_id
        self.room_id = room_id
        self.douyu_name = douyu_name
        self.barrage_content = barrage_content
        self.user_level = user_level
        self.user_image = user_image

    def get_room_status(self):
        # get live room status by html of douyu search result
        res = requests.get('https://www.douyu.com/search/?kw={}'.format(settings.APP_ROOM_ID))
        res.encoding = 'utf-8'
        if 'icon_live' in res.text:
            room_status = 1
        else:
            room_status = 2
        return room_status

    def run(self):
        now = datetime.now()
        # now = (datetime.now() + timedelta(hours=1))
        try:
            bar = Barrage()
            bar.douyu_id = self.douyu_id
            bar.douyu_name = self.douyu_name
            bar.barrage_content = self.barrage_content
            bar.user_level = self.user_level
            bar.user_image = self.user_image
            bar.room_id = self.room_id
            bar.barrage_time = now.strftime("%Y-%m-%d %H:%M:%S")
            bar.barrage_date = now.strftime("%Y-%m-%d")
            bar.room_status = self.get_room_status()
            bar.save()
        except Exception as e:
            get_logger().error("Save Barrage Fail")
            get_logger().error(e)
