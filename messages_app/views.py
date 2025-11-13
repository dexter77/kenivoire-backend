from rest_framework import viewsets, permissions, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from annonces.models import Ad


# 🔹 Nombre de messages non lus
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_messages_count(request):
    count = Message.objects.filter(
        conversation__participants=request.user,
        read=False
    ).exclude(sender=request.user).count()

    return Response({"unread_count": count})


# 🔹 Gestion des conversations
class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().order_by('-created_at')
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Récupère uniquement les conversations du user connecté
        return Conversation.objects.filter(
            participants=self.request.user
            ).exclude(deleted_for=self.request.user)

    def perform_create(self, serializer):
        ad_id = self.request.data.get('ad')

        if not ad_id:
            raise serializers.ValidationError({"ad": "ID de l'annonce requis."})

        try:
            ad = Ad.objects.get(id=ad_id)
        except Ad.DoesNotExist:
            raise serializers.ValidationError({"ad": "Annonce introuvable."})

        # ✅ Vérifie si une conversation existe déjà entre ces deux utilisateurs pour cette annonce
        existing_conv = Conversation.objects.filter(
            ad=ad,
            participants=self.request.user
        ).first()

        if existing_conv:
            raise serializers.ValidationError({
                "detail": "Une conversation existe déjà pour cette annonce avec ce vendeur.",
                "conversation_id": existing_conv.id
            })

        # ✅ Création de la conversation
        conversation = serializer.save(ad=ad)
        conversation.participants.add(self.request.user)
        if ad.owner != self.request.user:
            conversation.participants.add(ad.owner)
        conversation.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

    # Vérifie que l'utilisateur est bien un participant
        if request.user not in instance.participants.all():
            return Response({"detail": "Action non autorisée."}, status=403)

    # Marque la conversation comme supprimée pour cet utilisateur
        instance.deleted_for.add(request.user)
        instance.save()

    # Si tous les participants l’ont supprimée, on peut la supprimer totalement
        all_deleted = all(
            user in instance.deleted_for.all() for user in instance.participants.all()
        )
        if all_deleted:
            instance.delete()

        return Response({"detail": "Conversation masquée."}, status=204)


# 🔹 Gestion des messages
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

        # ✅ Si l’expéditeur n’est pas encore dans la conversation, on l’ajoute
        if self.request.user not in conversation.participants.all():
            conversation.participants.add(self.request.user)

        # ✅ Enregistrement du message
        serializer.save(sender=self.request.user, conversation=conversation, content=content)


# 🔹 Marquer une conversation comme lue
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_conversation_as_read(request, conversation_id):
    """Marque tous les messages non lus d'une conversation comme lus"""
    try:
        conversation = Conversation.objects.get(id=conversation_id, participants=request.user)
    except Conversation.DoesNotExist:
        return Response({"error": "Conversation introuvable"}, status=status.HTTP_404_NOT_FOUND)

    # ✅ Met à jour uniquement les messages reçus (pas ceux envoyés par soi-même)
    updated_count = Message.objects.filter(
        conversation=conversation,
        read=False
    ).exclude(sender=request.user).update(read=True)

    return Response({
        "status": "ok",
        "updated_messages": updated_count
    }, status=status.HTTP_200_OK)
