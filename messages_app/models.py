from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from annonces.models import Ad

class Conversation(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='conversations')
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not isinstance(self.id, (type(None), int)):
            raise ValidationError({'id': 'L\'ID doit être un nombre entier'})

    def __str__(self):
        return f"Conversation about {self.ad.title}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def clean(self):
        if not isinstance(self.id, (type(None), int)):
            raise ValidationError({'id': 'L\'ID doit être un nombre entier'})

    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.content[:30]}"
