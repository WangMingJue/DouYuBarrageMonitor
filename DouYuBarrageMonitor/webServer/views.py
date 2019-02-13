# Create your views here.

from django.http.response import HttpResponse
from webServer.BarrageContent.BarrageThread import BarrageThread
from webServer.models import Barrage
import json
from datetime import datetime, timedelta
from collections import Counter
from dateutil.relativedelta import relativedelta

global main_thread
main_thread = BarrageThread()


def start_barrage_service(request):
    global main_thread
    main_thread.start()
    return HttpResponse("start barrage service success")


def stop_barrage_service(request):
    global main_thread
    main_thread.stop()
    return HttpResponse("stop barrage service success")


def get_service_status(request):
    global main_thread
    if main_thread.is_alive():
        return HttpResponse("True")
    else:
        return HttpResponse("False")


def get_barrage(request):
    douyu_id = request.GET.get("douyu_id", None)
    start_time = request.GET.get("start_time", None)
    end_time = request.GET.get("end_time", None)
    if douyu_id is None or start_time is None or end_time is None:
        return HttpResponse("Please Input correctly format")

    start_time = datetime.strptime(start_time, "%Y-%m-%d")
    start_time = datetime(start_time.year, start_time.month, start_time.day, 18)
    end_time = datetime.strptime(end_time, "%Y-%m-%d")
    end_time = datetime(end_time.year, end_time.month, end_time.day, 6)
    bar = Barrage.objects.filter(barrage_date__gt=start_time).filter(barrage_date__lt=end_time).filter(
        douyu_id=douyu_id).filter(room_status=1).values_list('douyu_name', 'barrage_time', 'barrage_content')
    temp = list(bar)
    result_list = []
    for i in temp:
        result_list.append([i[0], i[1].strftime("%Y-%m-%d %H:%M:%S"), i[2]])
    return HttpResponse(json.dumps({"data": result_list}), content_type="application/json")


def get_barrage_rank(request):
    barrage_length = request.GET.get("barrage_length", None)
    get_type = request.GET.get("type", 5)  # 0:day, 1:week, 2:month, 3:year, 4:total
    get_time = request.GET.get("time", None)
    rank_length = request.GET.get("rank_length", None)

    get_time = datetime.strptime(get_time, "%Y-%m-%d")
    if get_time is None:
        get_time = datetime.now()

    start_time = get_time
    get_type = int(get_type)
    if get_type == 0:
        start_time = datetime(start_time.year, start_time.month, start_time.day, 18)
        end_time = (start_time + timedelta(days=1))
        end_time = datetime(end_time.year, end_time.month, end_time.day, 6)
    elif get_type == 1:
        start_time = datetime.strptime(week_get(start_time.date())[0], "%Y-%m-%d")
        start_time = datetime(start_time.year, start_time.month, start_time.day, 18)
        end_time = datetime.strptime(week_get(start_time.date())[7], "%Y-%m-%d")
        end_time = datetime(end_time.year, end_time.month, end_time.day, 6)
    elif get_type == 2:
        start_time = datetime(start_time.year, start_time.month, 1, 18)
        end_time = start_time + relativedelta(months=+1)
        end_time = datetime(end_time.year, end_time.month, end_time.day, 6)
    elif get_type == 3:
        start_time = datetime(start_time.year, 1, 1)
        end_time = datetime(start_time.year + 1, 1, 1)
        start_time = datetime(start_time.year, start_time.month, start_time.day, 18)
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
    te = Barrage.objects.raw(F"""
    SELECT `webServer_barrage`.`barrage_id`,`webServer_barrage`.`douyu_id`, `webServer_barrage`.`douyu_name` FROM `webServer_barrage` WHERE 
    (`webServer_barrage`.`barrage_time` BETWEEN "{start_time}" AND "{end_time}" 
    AND `webServer_barrage`.`room_status` = 1)
    """)
    bar = []
    for i in te:
        bar.append((i.douyu_id, i.douyu_name))
    temp = list(bar)
    if rank_length is None:
        result = Counter(temp).most_common(rank_length)
    else:
        result = Counter(temp).most_common(int(rank_length))
    return HttpResponse(json.dumps({"data": result}), content_type="application/json")


def week_get(vdate):
    dayscount = timedelta(days=vdate.isoweekday())
    dayfrom = vdate - dayscount + timedelta(days=1)
    week7 = []
    i = 0
    while i <= 7:
        week7.append(str(dayfrom + timedelta(days=i)))
        i += 1
    return week7
