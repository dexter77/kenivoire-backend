from rest_framework import viewsets, permissions, generics, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from annonces.models import Ad



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_messages_count(request):
    count = Message.objects.filter(
        conversation__participants=request.user,
        read=False
    ).exclude(sender=request.user).count()

    return Response({"unread_count": count})

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().order_by('-created_at')
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # return self.request.user.conversations.all()
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Vérifie que l'utilisateur est participant
        if request.user not in instance.participants.all():
            return Response({"detail": "Action non autorisée."}, status=403)
        self.perform_destroy(instance)
        return Response(status=204)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by('created_at')
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        conversation_id = self.request.data.get('conversation')
        content = self.request.data.get('content')

        if not conversation_id:
            raise serializers.ValidationError({"conversation": "ID de conversation requis"})

        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            raise serializers.ValidationError({"conversation": "Conversation introuvable"})

        serializer.save(sender=self.request.user, conversation=conversation, content=content)
