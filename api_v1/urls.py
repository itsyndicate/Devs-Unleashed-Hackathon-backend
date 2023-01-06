from django.urls import path
from .views import RegisterPlayerView, TaskogotchiView

urlpatterns = [
    path('register-user', RegisterPlayerView.as_view(), name='register-user'),
    path('taskogotchi', TaskogotchiView.as_view(), name='taskogotchi'),
]
