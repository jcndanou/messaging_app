# chats/permissions.py
from rest_framework import permissions
from chats import models

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow only participants of a conversation to view, update,
    delete messages within that conversation, or access the conversation itself.
    """
    message = 'You are not a participant of this conversation.'

    def has_permission(self, request, view):
        # Allow POST (create) for new messages/conversations if authenticated
        # or allow listing of conversations if authenticated.
        if request.user and request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission to check if the user is a participant.
        'obj' will be a Conversation or Message instance.
        """
        # S'assurer que l'utilisateur est authentifié
        if not request.user or not request.user.is_authenticated:
            return False

        if isinstance(obj, models.Conversation):
            # Pour une conversation, l'utilisateur doit être un participant
            return request.user in obj.participants.all()
        elif isinstance(obj, models.Message):
            # Pour un message, l'utilisateur doit être un participant de la conversation du message
            return request.user in obj.conversation.participants.all()
        return False