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

from django.conf import settings
from datetime import datetime
from LogContent.MyLog import get_logger
from webServer.BarrageContent.SaveBarrageThread import SaveBarrageThread
from webServer.BarrageContent.NetworkContent import *

now = datetime.now()

# get regular expression of username and barrage information
# danmu = re.compile(b'type@=chatmsg.*?/nn@=(.*?)/txt@=(.*?)/')
danmu = re.compile(b'type@=chatmsg.*?/uid@=(.*?)/nn@=(.*?)/txt@=(.*?)/cid@=(.*?)/ic@=(.*?)/level@=(.*?)/')


class BarrageThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.is_stop = False
        self.threads = []

    def stop(self):
        self.is_stop = True
        for i in self.threads:
            i.stop()

    def run(self):
        roomid = settings.APP_ROOM_ID
        msg = 'type@=loginreq/roomid@={}/\0'.format(roomid)
        sendmsg(msg)
        msg_more = 'type@=joingroup/rid@={}/gid@=-9999/\0'.format(roomid)
        sendmsg(msg_more)

        print('---------------welcome to live room of {}---------------'.format(get_name(roomid)))
        while True:
            if self.is_stop:
                break
            keeplive()
            data = client.recv(1024)
            danmu_more = danmu.findall(data)
            if not data:
                break
            else:
                with open('{1}-{0}message.txt'.format(now.strftime("%Y-%m-%d"), roomid), 'a+') as f:
                    try:
                        for i in danmu_more:
                            dmDict = {'USERID': i[0].decode(encoding='utf-8', errors='ignore'),
                                      'USERNAME': i[1].decode(encoding='utf-8', errors='ignore'),
                                      'BARRAGEINFO': i[2].decode(encoding='utf-8', errors='ignore'),
                                      'BARRAGEID': i[3].decode(encoding='utf-8', errors='ignore'),
                                      'USERIMAGE': i[4].decode(encoding='utf-8', errors='ignore'),
                                      'USERLEVEL': i[5].decode(encoding='utf-8', errors='ignore'),
                                      }
                            dmJsonStr = json.dumps(dmDict, ensure_ascii=False) + '\n'
                            get_logger().debug(dmJsonStr)
                            f.write(dmJsonStr)
                            self.parser_barrage(dmDict['USERID'], dmDict['USERNAME'].strip(),
                                                dmDict['BARRAGEINFO'].strip(),
                                                dmDict['USERLEVEL'].strip(), dmDict['USERIMAGE'].strip())
                    except Exception as e:
                        get_logger().warn("An error occurred while write barrage info to file and database")
                        get_logger().warn(e)
                        continue

    def parser_barrage(self, douyu_id, douyu_name, barrage_content, user_level, user_image):
        thread = SaveBarrageThread(douyu_id, settings.APP_ROOM_ID, douyu_name, barrage_content, user_level, user_image)
        thread.start()
        self.threads.append(thread)
