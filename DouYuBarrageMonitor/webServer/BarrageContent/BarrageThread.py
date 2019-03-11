# File Usage:
#
# Author:

# File Usage:
#
# Author:
from __future__ import unicode_literals

import re
import json
import threading
import os
from DouYuBarrageMonitor import settings
from datetime import datetime, timedelta
from LogContent.MyLog import get_logger
from webServer.BarrageContent.NetworkContent import MyClient
from webServer.crontab import scheduler_close_task
from webServer.BarrageContent.NetworkContent import get_room_status
from webServer.Tools.MailContent import send_email
from webServer.models import SignIn
from manage import signin_cache, barrage_cache

BASE_DIR = "{0}/{1}".format(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Log")
# get regular expression of username and barrage information
danmu = re.compile(b'type@=chatmsg.*?/uid@=(.*?)/nn@=(.*?)/txt@=(.*?)/cid@=(.*?)/ic@=(.*?)/level@=(.*?)/')


class BarrageThread(threading.Thread):
    _instance_lock = threading.Lock()

    def __init__(self):
        threading.Thread.__init__(self)
        self._is_stop = True

    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(BarrageThread, "_instance"):
    #         with BarrageThread._instance_lock:
    #             if not hasattr(BarrageThread, "_instance"):
    #                 BarrageThread._instance = object.__new__(cls)
    #     return BarrageThread._instance

    def stop_service(self):
        self._is_stop = True

    def get_stop_status(self):
        return self._is_stop

    def run(self):
        client = MyClient()
        self._is_stop = False
        try:
            client.connect()

            roomid = settings.APP_ROOM_ID
            msg = 'type@=loginreq/roomid@={}/\0'.format(roomid)
            client.sendmsg(msg)
            msg_more = 'type@=joingroup/rid@={}/gid@=-9999/\0'.format(roomid)
            client.sendmsg(msg_more)
            now = datetime.now()
            print('---------------welcome to live room of {}---------------'.format(client.get_name(roomid)))
            while True:
                if self._is_stop:
                    get_logger().debug("Stop the barrage service")
                    print(
                        '---------------away from live room of {}---------------'.format(client.get_name(roomid)))
                    break
                client.keeplive()
                data = client.client.recv(1024)
                danmu_more = danmu.findall(data)
                if not data:
                    break
                else:
                    with open('{2}/{1}_{0}_message.txt'.format(now.strftime("%Y-%m-%d"), roomid, BASE_DIR), 'a+') as f:
                        try:
                            for i in danmu_more:
                                nows = datetime.now()
                                dmDict = {'USERID': i[0].decode(encoding='utf-8', errors='ignore'),
                                          'USERNAME': i[1].decode(encoding='utf-8', errors='ignore'),
                                          'BARRAGEINFO': i[2].decode(encoding='utf-8', errors='ignore'),
                                          'BARRAGEID': i[3].decode(encoding='utf-8', errors='ignore'),
                                          'USERIMAGE': i[4].decode(encoding='utf-8', errors='ignore'),
                                          'USERLEVEL': i[5].decode(encoding='utf-8', errors='ignore'),
                                          'ROOMID': settings.APP_ROOM_ID,
                                          'BARRAGETIME': nows.strftime("%Y-%m-%d %H:%M:%S"),
                                          'BARRAGEDATE': nows.strftime("%Y-%m-%d"),
                                          'ROOMSTATUS': get_room_status(),
                                          }
                                dmJsonStr = json.dumps(dmDict, ensure_ascii=False) + '\n'
                                get_logger().debug(dmJsonStr)
                                f.write(dmJsonStr)
                                # save barrage cache
                                barrage_cache.update_cache(dmDict['USERNAME'], dmDict['USERID'])
                                # save sign in cache
                                if "#签到" == dmDict['BARRAGEINFO']:
                                    signin = SignIn()
                                    signin.douyu_id = dmDict['USERID']
                                    signin.douyu_name = dmDict['USERNAME']
                                    signin.room_id = settings.APP_ROOM_ID
                                    signin.sign_in_time = nows.strftime("%Y-%m-%d %H:%M:%S")
                                    signin.sign_in_date = nows.strftime("%Y-%m-%d")
                                    signin_cache.update_cache(dmDict['USERID'], signin.return_model())
                        except Exception as e:
                            get_logger().warn("An error occurred while write barrage info to file and database")
                            get_logger().warn(e)
                            continue
            client.cancel_connect()
        except Exception as e:
            error_msg = "catch barrages fail:{}".format(e)
            get_logger().error(error_msg)
            send_email(error_msg, "catch barrages fail")
            scheduler_close_task()
