from django.urls import re_path

from game.consumers import FightConsumer

websocket_urlpatterns = [
    re_path(r"ws/fight/(?P<account_id>(\w|\d)+)/?$", FightConsumer.as_asgi()),
]
