# File Usage:
#
# Author:


from django.conf.urls import url
from webServer.views import start_barrage_service, stop_barrage_service, get_barrage, get_barrage_rank, \
    get_service_status, get_barrage_live_rank, get_signin_score, check_wechat_token

urlpatterns = [
    url(r'start_barrage_service/', start_barrage_service),
    url(r'stop_barrage_service/', stop_barrage_service),
    url(r'get_service_status/', get_service_status),
    url(r'get_barrage_rank/', get_barrage_rank),
    url(r'get_barrage/', get_barrage),
    url(r'get_barrage_live_rank/', get_barrage_live_rank),
    url(r'get_signin_score/', get_signin_score),
    url(r'check_wechat_token/', check_wechat_token),
]
