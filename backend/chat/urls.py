from django.urls import path
from .views import ChatRoomCreateView, MessageSendView, ReadMessageUpdateView

urlpatterns = [
    path('rooms', ChatRoomCreateView.as_view(), name='chatroom-create'),
    path('rooms/<int:room_id>/messages', MessageSendView.as_view(), name='message-send'),
    path('rooms/<int:room_id>/messages/read', ReadMessageUpdateView.as_view(), name='read-message-update'),
]