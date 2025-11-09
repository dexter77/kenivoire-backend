from ads.models import Ad
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async
from .models import Conversation, Message

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f"chat_{self.conversation_id}"

        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
        else:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is not None:
            data = json.loads(text_data)
        elif bytes_data is not None:
            try:
                data = json.loads(bytes_data.decode())
            except Exception:
                # Invalid payload, ignore
                return
        else:
            return

        message = data.get('message')
        user = self.scope['user']

        msg = await self.save_message(self.conversation_id, user, message)

        # Envoyer le message à tous les membres du chat
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': msg['content'],
                'sender': msg['sender'],
                'receiver': msg['receiver'],
                'timestamp': msg['timestamp'],
                'is_read': msg['is_read']
            }
        )

        # 🔔 Envoyer une notification spéciale au destinataire
        await self.channel_layer.group_send(
            f"notifications_{msg['receiver_id']}",
            {
                'type': 'new_message_notification',
                'message': f"Nouveau message de {msg['sender']}",
                'conversation_id': self.conversation_id,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'receiver': event['receiver'],
            'timestamp': event['timestamp'],
            'is_read': event['is_read']
        }))

    async def new_message_notification(self, event):
        """Envoi d'une notification push au destinataire"""
        await self.send(text_data=json.dumps({
            'notification': event['message'],
            'conversation_id': event['conversation_id']
        }))

    @sync_to_async
    def save_message(self, conversation_id, sender, content):
        conversation = Conversation.objects.get(id=conversation_id)
        receiver = conversation.participants.exclude(id=sender.id).first()
        msg = Message.objects.create(
            conversation=conversation,
            sender=sender,
            receiver=receiver,
            content=content,
            is_read=False
        )
        return {
            'sender': sender.username,
            'receiver': receiver.username,
            'receiver_id': receiver.id,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'is_read': msg.is_read
        }
