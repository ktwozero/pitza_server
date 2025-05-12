from rest_framework import serializers
from .models import ChatRoom, Message
from django.contrib.auth.models import User

class ChatRoomSerializer(serializers.ModelSerializer):
    participants = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='username'  # 혹은 id로 바꿔도 됨
    )

    class Meta:
        model = ChatRoom
        fields = ['id', 'participants', 'post_id', 'created_at']
        read_only_fields = ['id', 'participants', 'created_at']