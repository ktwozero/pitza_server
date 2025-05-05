from django.urls import path
from .views import ChatRoomCreateView

urlpatterns = [
    path('rooms', ChatRoomCreateView.as_view(), name='chatroom-create'),
]