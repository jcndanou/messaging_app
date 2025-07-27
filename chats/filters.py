import django_filters
from .models import Message, Conversation
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageFilter(django_filters.FilterSet):
    """
    Filtre pour le modèle Message.
    Permet de filtrer les messages par expéditeur (ID) et par plage de date.
    """
    # Filtrer par l'ID de l'expéditeur
    sender = django_filters.UUIDFilter(field_name='sender__user_id') # Ou 'sender__id' si votre PK est 'id'

    # Filtrer par plage de temps (avant/après une certaine date)
    sent_at_before = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    sent_at_after = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')

    class Meta:
        model = Message
        fields = ['sender', 'sent_at_before', 'sent_at_after', 'conversation']

class ConversationFilter(django_filters.FilterSet):
    """
    Filtre pour le modèle Conversation.
    Permet de filtrer les conversations par participant.
    """
    # Filtrer par l'ID d'un participant
    participant = django_filters.UUIDFilter(field_name='participants__user_id') # Ou 'participants__id'

    class Meta:
        model = Conversation
        fields = ['participant']