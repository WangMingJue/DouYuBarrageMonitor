# File Usage:
#
# Author:
import datetime
import os
import random
import time
import requests
from DouYuBarrageMonitor import settings
from LogContent.MyLog import get_logger
from webServer.models import Barrage, SignIn
from datetime import timedelta, datetime
from webServer.BarrageContent.NetworkContent import get_room_status
from webServer.Tools.MailContent import send_email
from manage import signin_cache, barrage_cache

HOST = settings.HOST
BASE_DIR = "{0}/{1}".format(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "webServer/Log")
global OPEN_TIME
OPEN_TIME = 18


def check_service_status():
    print("*** Start Check Service Status ***")
    response = requests.get("{}/web/get_service_status/".format(HOST)).content
    print("*** Check Service Status Result:{} ***".format(response))
    return response


def start_service():
    print("Start Start Service")
    response = requests.get("{}/web/start_barrage_service/".format(HOST)).content
    print("Start Service Result:{}".format(response))
    return response


def stop_service():
    print("Start Stop Service")
    response = requests.get("{}/web/stop_barrage_service/".format(HOST)).content
    print("Stop Service Result:{}".format(response))
    return response


def scheduler_open_task():
    # First, check whether there is the check-in text of the day
    # (in order to prevent the restart of the live of the day,
    # resulting in the interruption of the check-in data).
    # If there is, it will be loaded into the check-in cache.
    # So does the barrage cache
    now = datetime.now()
    if now.hour < 6:
        now = now - timedelta(hours=6)
    if os.path.exists('{2}/{1}_{0}_sign.txt'.format(now.strftime("%Y-%m-%d"), settings.APP_ROOM_ID, BASE_DIR)):
        with open('{2}/{1}_{0}_sign.txt'.format(now.strftime("%Y-%m-%d"), settings.APP_ROOM_ID, BASE_DIR),
                  'r', encoding='UTF-8') as sign_f:
            for line in sign_f.readlines():
                data = line.split("~")
                signin_cache.update_cache(data[0], eval(data[1].replace("\\", "").replace("\n", "")))
    if os.path.exists('{2}/{1}_{0}_sign.txt'.format(now.strftime("%Y-%m-%d"), settings.APP_ROOM_ID, BASE_DIR)):
        with open('{2}/{1}_{0}_barrage_number.txt'.format(now.strftime("%Y-%m-%d"), settings.APP_ROOM_ID, BASE_DIR),
                  'r', encoding='UTF-8') as number_f:
            for line in number_f.readlines():
                data = line.split("~")
                barrage_cache.get_barrage_cache()[data[0]] = eval(data[1].replace("\\", "").replace("\n", ""))

    print(F"scheduler_open_task:{time.asctime(time.localtime(time.time()))}")
    if b'True' in check_service_status():
        print("Service have started")
        return True
    elif b'False' in check_service_status():
        i = 3
        while i > 1:
            if b'success' in start_service():
                time.sleep(2)
                if b'True' in check_service_status():
                    print("Service Start Success")
                    return True
            i -= 1
    print("Service Start Fail")
    send_email(F"scheduler_open_task:{time.asctime(time.localtime(time.time()))} fail", "open fail")
    return False


def scheduler_close_task():
    # Save the check-in data to the text (room_id_date_signin.txt),
    # and then the check-in bullet screen cache;
    # So does the barrage cache
    now = datetime.now()
    print(signin_cache.get_signin_cache())
    print(barrage_cache.get_barrage_cache())
    get_logger().debug(signin_cache.get_signin_cache())
    get_logger().debug(barrage_cache.get_barrage_cache())
    with open('{2}/{1}_{0}_sign.txt'.format(now.strftime("%Y-%m-%d"), settings.APP_ROOM_ID, BASE_DIR), 'a+') as sign_f:
        for key, value in signin_cache.get_signin_cache().items():
            sign_f.writelines("{0}~{1}\n".format(key, value))
        signin_cache.reset_signin_cache()
    with open('{2}/{1}_{0}_barrage_number.txt'.format(now.strftime("%Y-%m-%d"), settings.APP_ROOM_ID, BASE_DIR),
              'w') as number_f:
        for key, value in barrage_cache.get_barrage_cache().items():
            number_f.writelines("{0}~{1}\n".format(key, value))
        barrage_cache.reset_barrage_cache()

    print(F"scheduler_close_task:{time.asctime(time.localtime(time.time()))}")

    if b'False' in check_service_status():
        print("Service have stopped")
        return True
    elif b'True' in check_service_status():
        i = 3
        while i > 1:
            if b'success' in stop_service():
                time.sleep(2)
                if b'False' in check_service_status():
                    print("Service Stop Success")
                    return True
            i -= 1
    print("Service Stop Fail")
    send_email(F"scheduler_close_task:{time.asctime(time.localtime(time.time()))} fail", "close fail")
    return False


def scheduler_check_task():
    print(">" * 50)
    print(F"scheduler_check_task:{time.asctime(time.localtime(time.time()))}")
    if get_room_status() == 1 and b'False' in check_service_status():
        print("The service was turned off at the wrong time, so it should be turned on")
        scheduler_open_task()
        global OPEN_TIME
        OPEN_TIME = datetime.now().hour
    elif get_room_status() == 2 and b'True' in check_service_status():
        print("The service was turned on at the wrong time, so it should be turned off")
        scheduler_close_task()
    print("<" * 50)


def add_barrage_to_database(room_id, yesterday):
    file_name = "{2}/{0}_{1}_message.txt".format(room_id, yesterday, BASE_DIR)
    if not os.path.exists(file_name):
        message = F"Don't exist:{file_name}"
        print(message)
        get_logger().error(message)
        send_email(
            F"add_barrage_to_database:{time.asctime(time.localtime(time.time()))} fail, Don't exist:{file_name}",
            "write data to database fail")
        return False
    print("Start write barrage {0} data to database".format(file_name))
    with open(file_name, "r+", encoding="UTF-8") as barrage_file:
        for info in barrage_file.readlines():
            info = eval(info)
            try:
                bar = Barrage()
                bar.douyu_id = info["USERID"]
                bar.douyu_name = info["USERNAME"]
                bar.barrage_content = info["BARRAGEINFO"]
                bar.user_level = info["USERLEVEL"]
                bar.user_image = info["USERIMAGE"]
                bar.room_id = info["ROOMID"]
                bar.barrage_time = info["BARRAGETIME"]
                bar.barrage_date = info["BARRAGEDATE"]
                bar.room_status = info["ROOMSTATUS"]
                bar.save()
            except Exception as e:
                get_logger().error("Save Barrage Fail")
                get_logger().error(e)
                return False
    print("End write barrage {0} data to database".format(file_name))
    return True


def add_signin_to_database(room_id, yesterday):
    file_name = "{2}/{0}_{1}_sign.txt".format(room_id, yesterday, BASE_DIR)
    if not os.path.exists(file_name):
        message = F"Don't exist:{file_name}"
        print(message)
        get_logger().error(message)
        send_email(
            F"add_signin_to_database:{time.asctime(time.localtime(time.time()))} fail, Don't exist:{file_name}",
            "write data to database fail")
        return False
    print("Start write signin {0} data to database".format(file_name))
    with open(file_name, "r+", encoding="UTF-8") as signin_file:
        for line in signin_file.readlines():
            data = line.split("~")
            douyu_id, room_id, sign_in_time, sign_in_date, douyu_name = eval(
                data[1].replace("\\", "").replace("\n", ""))

            try:
                signin = SignIn()
                signin.douyu_id = douyu_id
                signin.room_id = room_id
                signin.sign_in_time = sign_in_time
                signin.sign_in_date = sign_in_date
                signin.douyu_name = douyu_name

                signin.sign_in_score = 1
                signin.is_continuous = False
                signin.continuous_day = 1

                continuous_reward_score = 1
                before_signin = SignIn.objects.filter(douyu_id=douyu_id).order_by('-sign_in_time').first()
                """
                1. Daily sign-in points +1
                2. After signing in for seven consecutive days, continue to sign in for an extra +1
                3. For every "continuous check-in for 30 days", you can get a "treasure box of points", 
                    with additional points of +5 ~ +10
                """
                if before_signin is None:
                    pass
                elif (sign_in_date - datetime.strptime(before_signin.sign_in_date, "%Y-%m-%d %H:%M:%S")).days > 1:
                    signin.sign_in_score = before_signin.sign_in_score + 1
                    signin.is_continuous = False
                    signin.continuous_day = 1
                elif (sign_in_date - datetime.strptime(before_signin.sign_in_date, "%Y-%m-%d %H:%M:%S")).days == 1:
                    signin.is_continuous = True
                    signin.continuous_day = before_signin.continuous_day + 1
                    if before_signin.continuous_day % 30 == 0:
                        signin.sign_in_score = before_signin.sign_in_score + 1 + random.randint(5, 10)
                    elif before_signin.continuous_day > 7:
                        signin.sign_in_score = before_signin.sign_in_score + 1 + continuous_reward_score
                    else:
                        signin.sign_in_score = before_signin.sign_in_score + 1
                signin.save()
            except Exception as e:
                get_logger().error("Save SignIn Fail")
                get_logger().error(e)
                return False
    print("End write signin {0} data to database".format(file_name))
    return True


def scheduler_database_task():
    try:
        print(F"scheduler_database_task:{time.asctime(time.localtime(time.time()))}")
        room_id = settings.APP_ROOM_ID
        now = datetime.now()
        yesterday = datetime.strftime(now - timedelta(days=1), "%Y-%m-%d")
        if not add_barrage_to_database(room_id, yesterday) or not add_signin_to_database(room_id, yesterday):
            send_email(
                F"scheduler_database_task:{time.asctime(time.localtime(time.time()))} fail",
                "write data to database fail")
    except Exception as e:
        print(e)
        send_email(
            F"scheduler_database_task:{time.asctime(time.localtime(time.time()))} fail, {e}",
            "write data to database fail")
