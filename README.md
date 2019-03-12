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


ChangList：

2019-03-11:

1.添加了微信公众号自定义回复内容

2.添加了监控弹幕时，实时添加签到和弹幕量缓存

3.下一步准备将所有缓存都换成Redis

4.使用了crontab技术和Django-crontab组件，进行定时开启和关闭服务，并定时写数据到数据库中
