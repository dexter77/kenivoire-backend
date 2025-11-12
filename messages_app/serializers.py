from rest_framework import serializers
from .models import Conversation, Message
from users.serializers import UserSerializer
from annonces.serializers import AdSerializer
from annonces.models import Ad
from annonces.serializers import AdSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'content', 'created_at', 'read']

# Serializer pour GET (lecture) des conversations
class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    ad = serializers.PrimaryKeyRelatedField(queryset=Ad.objects.all())
    ad = AdSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'ad', 'participants', 'messages', 'created_at']

# Serializer pour POST (création) de conversation
class ConversationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['ad']

    def validate_ad(self, value):
        if value is None:
            raise serializers.ValidationError("L'annonce est obligatoire pour créer une conversation.")
        return value

    def create(self, validated_data):
        # Ajoute automatiquement l'utilisateur connecté comme participant
        user = self.context['request'].user
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.add(user)
        return conversation
