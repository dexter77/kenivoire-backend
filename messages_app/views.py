from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from annonces.models import Ad

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    def create(self, request, *args, **kwargs):
        ad_id = request.data.get('ad')
        ad = Ad.objects.get(id=ad_id)

        # Vérifie si une conversation existe déjà entre les deux utilisateurs pour cette annonce
        existing = Conversation.objects.filter(
            ad=ad, participants=request.user
        ).first()

        if existing:
            return Response(ConversationSerializer(existing).data)

        conversation = Conversation.objects.create(ad=ad)
        conversation.participants.add(request.user, ad.owner)
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(conversation__participants=self.request.user)

    def perform_create(self, serializer):
        conversation_id = self.request.data.get('conversation')
        conversation = Conversation.objects.get(id=conversation_id)

        if self.request.user not in conversation.participants.all():
            raise PermissionError("Vous ne pouvez pas envoyer de message dans cette conversation.")

        serializer.save(sender=self.request.user, conversation=conversation)
