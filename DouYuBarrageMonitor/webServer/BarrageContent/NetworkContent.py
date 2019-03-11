import requests
import socket
from bs4 import BeautifulSoup
from DouYuBarrageMonitor import settings
import threading


def get_room_status():
    # get live room status by html of douyu search result
    res = requests.get('https://www.douyu.com/search/?kw={}'.format(settings.APP_ROOM_ID))
    res.encoding = 'utf-8'
    if 'icon_live' in res.text:
        room_status = 1
    else:
        room_status = 2
    return room_status


class MyClient:
    # _instance_lock = threading.Lock()

    def __init__(self):
        # Configure the socket IP and port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = socket.gethostbyname("openbarrage.douyutv.com")
        self.port = 8601

    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(MyClient, "_instance"):
    #         with MyClient._instance_lock:
    #             if not hasattr(MyClient, "_instance"):
    #                 MyClient._instance = object.__new__(cls)
    #     return MyClient._instance

    def connect(self):
        self.client.connect((self.host, self.port))

    def cancel_connect(self):
        self.client.close()

    def sendmsg(self, msgstr):
        """
            Client to send a request to the server function, the integration of sending protocol header function
            msgHead: The protocol header before sending the data, twice the length of the message, and the message type, encryption field, and confidentiality field
            Use a while loop to send specific data, making sure you're sending it all out
        """
        msg = msgstr.encode('utf-8')
        data_length = len(msg) + 8
        code = 689
        msgHead = int.to_bytes(data_length, 4, 'little') + int.to_bytes(data_length, 4, 'little') + int.to_bytes(code,
                                                                                                                 4,
                                                                                                                 'little')
        try:
            self.client.send(msgHead)
        except:
            self.client.close()
        sent = 0
        while sent < len(msg):
            tn = self.client.send(msg[sent:])
            sent = sent + tn

    def keeplive(self):
        """
            Sending heartbeat information to maintain a long TCP connection
            Add \0 to the end of the heartbeat message
        """
        # msg = 'type@=keeplive/tick@=' + str(int(time.time())) + '/\0'
        msg = 'type@=mrkl/\0'
        self.sendmsg(msg)

    def get_name(self, roomid):
        """
        BeautifulSoup is used to get live room titles
        """
        r = requests.get("http://www.douyu.com/" + roomid)
        soup = BeautifulSoup(r.text, 'lxml')
        return soup.find('h3', {'class', 'Title-headlineH2'}).string
