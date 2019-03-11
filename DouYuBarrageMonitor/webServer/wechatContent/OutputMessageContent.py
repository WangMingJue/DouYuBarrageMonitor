import time
import requests
import json
from DouYuBarrageMonitor.settings import HOST
from datetime import datetime

now = datetime.strftime(datetime.now(), "%Y-%m-%d")

barrage_url_dict = {
    "Barrage#day": F"{HOST}/web/get_barrage_rank/?type=0&time={now}&rank_length=10",
    "Barrage#week": F"{HOST}/web/get_barrage_rank/?type=1&time={now}&rank_length=10",
    "Barrage#month": F"{HOST}/web/get_barrage_rank/?type=2&time={now}&rank_length=10",
    "Barrage#year": F"{HOST}/web/get_barrage_rank/?type=3&time={now}&rank_length=10",
    "Barrage#total": F"{HOST}/web/get_barrage_rank/?type=4&time={now}&rank_length=10",
}


def output_message(fromusername, tousername, input_message):
    result = ""
    if input_message in barrage_url_dict.keys():
        result = get_barrage_rank(barrage_url_dict[input_message])
    elif input_message.startswith("Live#"):
        result = get_other_result(input_message, "{0}/web/get_barrage_live_rank/?name={1}")
    elif input_message.startswith("Score#"):
        result = get_other_result(input_message, "{0}/web/get_signin_score/?name={1}")
    else:
        return "success"
    return F"""
                <xml>
                <ToUserName><![CDATA[{fromusername}]]></ToUserName>
                <FromUserName><![CDATA[{tousername}]]></FromUserName>
                <CreateTime>{time.time()}</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[{result}]]></Content>
                </xml>
                """


def get_other_result(name, url):
    name = name.split("#")
    name = name[1]

    if "get_barrage_live_rank" in url:
        response = requests.get(url.format(HOST, name))
        result = json.loads(response.content)
        return F"\"{result['data'][0]}\"is {result['data'][1]}"
    elif "get_signin_score" in url:
        response = requests.get(url.format(HOST, name))
        result = json.loads(response.content)
        return result['data']


def get_barrage_rank(url):
    response = requests.get(url)
    data = json.loads(response.content)
    result_str = ""
    i = 1
    for da in data['data']:
        result_str += F"{i}\t{da[0][1]}:{da[1]}\n"
        i += 1
    return result_str
