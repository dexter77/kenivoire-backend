from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet, unread_messages_count, mark_conversation_as_read

router = DefaultRouter()
router.register('conversations', ConversationViewSet, basename='conversation')
router.register('messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
    path('unread/', unread_messages_count, name='unread_messages_count'),
    path('mark-read/<int:conversation_id>/', mark_conversation_as_read, name='mark_conversation_as_read'),

]
