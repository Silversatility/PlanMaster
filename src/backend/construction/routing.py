from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/calendar/(?P<contractor_pk>\d+)/$', consumers.CalendarConsumer),
]
