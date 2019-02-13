import requests
import socket
from bs4 import BeautifulSoup

# Configure the socket IP and port
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostbyname("openbarrage.douyutv.com")
port = 8601
client.connect((host, port))


def sendmsg(msgstr):
    '''
    Client to send a request to the server function, the integration of sending protocol header function
    msgHead: The protocol header before sending the data, twice the length of the message, and the message type, encryption field, and confidentiality field
    Use a while loop to send specific data, making sure you're sending it all out
    '''
    msg = msgstr.encode('utf-8')
    data_length = len(msg) + 8
    code = 689
    msgHead = int.to_bytes(data_length, 4, 'little') + int.to_bytes(data_length, 4, 'little') + int.to_bytes(code, 4,
                                                                                                             'little')
    client.send(msgHead)
    sent = 0
    while sent < len(msg):
        tn = client.send(msg[sent:])
        sent = sent + tn


def keeplive():
    '''
    Sending heartbeat information to maintain a long TCP connection
    Add \0 to the end of the heartbeat message
    '''
    # msg = 'type@=keeplive/tick@=' + str(int(time.time())) + '/\0'
    msg = 'type@=mrkl/\0'
    sendmsg(msg)


def get_name(roomid):
    '''
    BeautifulSoup is used to get live room titles
    '''
    r = requests.get("http://www.douyu.com/" + roomid)
    soup = BeautifulSoup(r.text, 'lxml')
    return soup.find('h3', {'class', 'Title-headlineH2'}).string
