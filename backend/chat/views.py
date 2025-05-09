from rest_framework.views import APIView
from rest_framework.response import Response
#from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth.models import User
from .models import ChatRoom, Message, ChatParticipant
from .serializers import ChatRoomSerializer
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
import requests

class ChatRoomCreateView(APIView):
    permission_classes = [AllowAny]
    #permission_classes = [IsAuthenticated]

    def post(self, request):
        post_id = request.data.get("post_id")
        receiver_id = request.data.get("receiver_id")
        sender = User.objects.get(id=1)
        #sender = request.user

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response({"error": "Invalid receiver_id"}, status=status.HTTP_400_BAD_REQUEST)

        # 중복 채팅방이 있는지 확인하고 없으면 새로 생성
        existing_room = ChatRoom.objects.filter(
            post_id=post_id,
            participants=sender
        ).filter(participants=receiver).first()

        if existing_room:
            room = existing_room
        else:
            room = ChatRoom.objects.create(post_id=post_id)
            room.participants.set([sender, receiver])
            room.save()

        response_data = {
            "chatroom_id": str(room.id),
            "participants": [str(user.id) for user in room.participants.all()],
            "created_at": room.created_at.isoformat()
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
    
# 메시지 전송 API
from rest_framework.parsers import MultiPartParser

class MessageSendView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, room_id):
        content = request.data.get("content")
        message_type = request.data.get("message_type", "text")
        sender = User.objects.get(id=request.data.get("sender_id"))  # 나중엔 request.user로 대체

        try:
            chatroom = ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            return Response({"error": "Invalid chatroom ID"}, status=status.HTTP_404_NOT_FOUND)

        # 메시지 생성 조건 분기
        if message_type == "text":
            content = request.data.get("content")
            if not content:
                return Response({"error": "Text content is required."}, status=400)
            message = Message.objects.create(
                chatroom=chatroom,
                sender=sender,
                content=content
            )

        elif message_type == "image":
            image = request.FILES.get("image")
            if not image:
                return Response({"error": "Image file is required."}, status=400)
            message = Message.objects.create(
                chatroom=chatroom,
                sender=sender,
                image=image
            )

        else:
            return Response({"error": "Invalid message_type."}, status=400)

        # 소켓 서버로 메시지 전송
        socket_data = {
            "roomId": str(chatroom.id),
            "sender_id": sender.id,
            "content": content,
            "message_type": message_type
        }

        try:
            requests.post("http://localhost:3001/socket/message", json=socket_data)
        except Exception as e:
            print("Socket 전송 실패:", e)

        return Response({
            "message_id": message.id,
            "sender_id": sender.id,
            "content": message.content,
            "image_url": message.image.url if message.image else None,
            "message_type": message_type,
            "sent_at": message.timestamp
        }, status=status.HTTP_201_CREATED)

class ReadMessageUpdateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, room_id):
        try:
            user_id = request.data.get("user_id")  # 추후 request.user로 대체
            last_read_message_id = request.data.get("last_read_message_id")

            if not last_read_message_id:
                return Response({"error": "last_read_message_id is required"}, status=400)

            user = User.objects.get(id=user_id)
            chatroom = ChatRoom.objects.get(id=room_id)
            message = Message.objects.get(id=last_read_message_id, chatroom=chatroom)

            participant, created = ChatParticipant.objects.get_or_create(user=user, chatroom=chatroom)
            participant.last_read_message = message
            participant.save()

            return Response({"success": True})

        except User.DoesNotExist:
            return Response({"error": "Invalid user ID"}, status=400)
        except ChatRoom.DoesNotExist:
            return Response({"error": "ChatRoom not found"}, status=404)
        except Message.DoesNotExist:
            return Response({"error": "Message not found in room"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
