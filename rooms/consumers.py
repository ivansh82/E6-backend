import json
from channels.generic.websocket import AsyncWebsocketConsumer
import datetime
from chats.models import ProfileData, Message, Chat
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        created = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'username': str(self.scope["user"]),
                'userID': str(self.scope["user"].pk),
                'created': created,
                'message': message
            }
        )
        await self.create_message(message)

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def profile_photo(self):
        try:
            profile = ProfileData.objects.get(owner__pk = self.scope["user"].pk).avatar_photo
        except ObjectDoesNotExist:
            profile = 'none'
        return profile

    @database_sync_to_async
    def create_message(self, message):
        try:
            chat = Chat.objects.get(id = int(self.room_name))
            Message.objects.create(chat = chat, author = self.scope["user"], content = message)
        except ObjectDoesNotExist:
            print('chat not found')

