from django.urls import re_path
from .views import RegisterPlayerView, TaskogotchiView, OpponentsListView, FightChallengeView

urlpatterns = [
    re_path(r'register-player/?', RegisterPlayerView.as_view(), name='register-player'),
    re_path(r'taskogotchi/?', TaskogotchiView.as_view(), name='taskogotchi'),
    re_path(r'available-opponents/?', OpponentsListView.as_view(), name='available-opponents'),
    re_path(r'fight/?', FightChallengeView.as_view(), name='fight'),
]
