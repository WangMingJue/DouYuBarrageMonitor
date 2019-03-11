# Create your views here.
import hashlib
import json
import time
from DouYuBarrageMonitor import settings
from django.http.response import HttpResponse
from webServer.BarrageContent.BarrageThread import BarrageThread
from webServer.models import Barrage, SignIn
from datetime import datetime, timedelta
from collections import Counter
from dateutil.relativedelta import relativedelta
from LogContent.MyLog import get_logger
from webServer.crontab import OPEN_TIME
from manage import barrage_cache
from webServer.wechatContent.AccessTokenManager import AccessTokenManager
from webServer.wechatContent.InputMessageContent import parser_input_message
from webServer.wechatContent.OutputMessageContent import output_message

access_token_manager = AccessTokenManager()
barrage_thread_list = []


def get_barrage_thread():
    if len(barrage_thread_list) < 1:
        barrage_thread_list.append(BarrageThread())
    elif len(barrage_thread_list) > 1:
        for i in range(len(barrage_thread_list) - 1):
            barrage_thread_list[i].stop_service()
            del barrage_thread_list[i]
    return barrage_thread_list[0]


def start_barrage_service(request):
    barrage_thread = get_barrage_thread()
    try:
        if barrage_thread.get_stop_status():
            barrage_thread.start()
            message = "start barrage service success"
        else:
            message = "start barrage service success, service have started"
    except Exception as e:
        message = "start barrage service fail:{}".format(e)
    get_logger().debug(message)
    return HttpResponse(message)


def stop_barrage_service(request):
    barrage_thread = get_barrage_thread()
    try:
        if not barrage_thread.get_stop_status():
            barrage_thread.stop_service()
            message = "stop barrage service success"
        else:
            message = "stop barrage service success, service have stopped"
    except Exception as e:
        message = "stop barrage service fail:{}".format(e)

    del barrage_thread_list[0]
    get_logger().debug(message)
    return HttpResponse(message)


def get_service_status(request):
    barrage_thread = get_barrage_thread()
    if barrage_thread.get_stop_status():
        return HttpResponse("False")
    else:
        return HttpResponse("True")


def get_barrage(request):
    douyu_id = request.GET.get("douyu_id", None)
    start_time = request.GET.get("start_time", None)
    end_time = request.GET.get("end_time", None)
    if douyu_id is None or start_time is None or end_time is None:
        return HttpResponse("Please Input correctly format")

    start_time = datetime.strptime(start_time, "%Y-%m-%d")
    start_time = datetime(start_time.year, start_time.month, start_time.day, OPEN_TIME)
    end_time = datetime.strptime(end_time, "%Y-%m-%d")
    end_time = datetime(end_time.year, end_time.month, end_time.day, 6)
    bar = Barrage.objects.filter(barrage_date__gt=start_time).filter(barrage_date__lt=end_time).filter(
        douyu_id=douyu_id).filter(room_status=1).values_list('douyu_name', 'barrage_time', 'barrage_content')
    temp = list(bar)
    result_list = []
    for i in temp:
        result_list.append([i[0], i[1].strftime("%Y-%m-%d %H:%M:%S"), i[2]])
    return HttpResponse(json.dumps({"data": result_list}), content_type="application/json")


def get_barrage_live_rank(request):
    douyu_name = request.GET.get("name", None)
    data = sorted(barrage_cache.get_barrage_cache().items(), key=lambda d: d[1][1], reverse=True)
    i = 1
    for key in data:
        if douyu_name == key[0]:
            return HttpResponse(json.dumps({"data": [douyu_name, i]}), content_type="application/json")
        i += 1
    return HttpResponse(json.dumps({"data": [douyu_name, i]}), content_type="application/json")


def get_signin_score(request):
    douyu_name = request.GET.get("name", None)
    sign_data = SignIn.objects.filter(douyu_name=douyu_name).order_by('-sign_in_time').first()
    if sign_data is None:
        return HttpResponse(json.dumps({"data": "你还没有签到"}), content_type="application/json")
    return HttpResponse(json.dumps({"data": sign_data.sign_in_score}), content_type="application/json")


def get_barrage_rank(request):
    get_logger().info(F"\nrun fuc:get_barrage_rank\t{request.GET}\n")
    douyu_name = request.GET.get("name", None)
    get_type = request.GET.get("type", 5)  # 0:day, 1:week, 2:month, 3:year, 4:total
    get_time = request.GET.get("time", None)
    rank_length = request.GET.get("rank_length", None)

    get_time = datetime.strptime(get_time, "%Y-%m-%d")
    if get_time is None:
        get_time = datetime.now()

    start_time = get_time
    get_type = int(get_type)
    if get_type == 0:
        start_time = datetime(start_time.year, start_time.month, start_time.day, OPEN_TIME)
        end_time = (start_time + timedelta(days=1))
        end_time = datetime(end_time.year, end_time.month, end_time.day, 6)
    elif get_type == 1:
        start_time = datetime.strptime(week_get(start_time.date())[0], "%Y-%m-%d")
        start_time = datetime(start_time.year, start_time.month, start_time.day, OPEN_TIME)
        end_time = datetime.strptime(week_get(start_time.date())[7], "%Y-%m-%d")
        end_time = datetime(end_time.year, end_time.month, end_time.day, 6)
    elif get_type == 2:
        start_time = datetime(start_time.year, start_time.month, 1, OPEN_TIME)
        end_time = start_time + relativedelta(months=+1)
        end_time = datetime(end_time.year, end_time.month, end_time.day, 6)
    elif get_type == 3:
        start_time = datetime(start_time.year, 1, 1)
        end_time = datetime(start_time.year + 1, 1, 1)
        start_time = datetime(start_time.year, start_time.month, start_time.day, OPEN_TIME)
        end_time = datetime(end_time.year, end_time.month, end_time.day, 6)
    elif get_type == 4:
        bar = Barrage.objects.filter(room_status=1).values_list('douyu_id', 'douyu_name')
        temp = list(bar)
        if rank_length is None:
            result = Counter(temp).most_common(rank_length)
        else:
            result = Counter(temp).most_common(int(rank_length))
        return HttpResponse(json.dumps({"data": result}), content_type="application/json")
    else:
        return HttpResponse("Please input correctly type in 0~4")
    # bar = Barrage.objects.filter(barrage_time__gt=start_time).filter(barrage_time__lt=end_time).filter(
    #     room_status=1).values_list('douyu_id', 'douyu_name')
    room_id = settings.APP_ROOM_ID
    te = Barrage.objects.raw(F"""
    SELECT `webServer_barrage`.`barrage_id`,`webServer_barrage`.`douyu_id`, `webServer_barrage`.`douyu_name` FROM `webServer_barrage` WHERE 
    (`webServer_barrage`.`barrage_time` BETWEEN "{start_time}" AND "{end_time}" 
    AND `webServer_barrage`.`room_status` = 1) AND `webServer_barrage`.`room_id` = {room_id}
    """)
    bar = []
    for i in te:
        bar.append((i.douyu_id, i.douyu_name))
    temp = list(bar)
    total_result = Counter(temp).most_common(None)
    data = {}
    if douyu_name is not None:
        i = 0
        for key, value in total_result:
            i += 1
            if douyu_name == key[1]:
                data[douyu_name] = (i, value)
                break
        if douyu_name not in data.keys():
            data[douyu_name] = (i, 0)

    if rank_length is not None:
        result = Counter(temp).most_common(int(rank_length))
        return HttpResponse(json.dumps({"data": result, "people": data}), content_type="application/json")
    return HttpResponse(json.dumps({"data": total_result, "people": data}), content_type="application/json")


def week_get(vdate):
    dayscount = timedelta(days=vdate.isoweekday())
    dayfrom = vdate - dayscount + timedelta(days=1)
    week7 = []
    i = 0
    while i <= 7:
        week7.append(str(dayfrom + timedelta(days=i)))
        i += 1
    return week7


def check_wechat_token(request):
    data = request.GET
    signature = data['signature']
    timestamp = data['timestamp']
    nonce = data['nonce']
    # echostr = data['echostr']
    token = 'dy428250'

    list = [token, timestamp, nonce]
    list.sort()
    s1 = hashlib.sha1()
    s1.update(''.join(list).encode())
    hashcode = s1.hexdigest()
    print(F"handle/GET func: hashcode, signature:{hashcode}  {signature}")
    if hashcode == signature:
        # return HttpResponse(echostr)
        fromusername, tousername, message = parser_input_message(request.body)
        return HttpResponse(output_message(fromusername, tousername, message))
    else:
        return HttpResponse("")
