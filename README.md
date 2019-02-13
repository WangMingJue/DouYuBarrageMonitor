# DouYuBarrageMonitor

这是一个用来收集指定斗鱼房间号弹幕的工具。
然后根据请求来获取日榜，周榜，月榜，年榜，总榜五种弹幕榜单。

This is a tool used to collect barrage for designated douyu room Numbers.
Then according to the request to obtain the daily list, week list, month list, year list, total list five kinds of barrage list.



Stage:
0. modify APP_ROOM_ID in settings.py
1. python manage.py runserver ip:port
2. input [ip:port/web/start_barrage_service/] in browse
3. You can check if the service is started, input [ip:port/web/get_service_status/] in browse
4. you can stop the service, input [ip:port/web/stop_barrage_service/]

Known Issue:
1. 每获取到一条弹幕，都会创建一个子线程去写入数据库，两天后，会造成线程过多，目前是手动重启服务。
(When service get a barrage, it will create an child thread for write barrage info to database. After tow day, there are many threads, please manual restart service.)
