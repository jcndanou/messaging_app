from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User, Conversation, Message
from .serializers import (
    UserSerializer,
    ConversationSerializer,
    ConversationDetailSerializer,
    MessageSerializer,
    MessageDetailSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Endpoint pour récupérer l'utilisateur connecté"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Ne retourne que les conversations de l'utilisateur connecté"""
        return Conversation.objects.filter(participants=self.request.user)

    def get_serializer_class(self):
        """Utilise le serializer détaillé pour la récupération"""
        if self.action == 'retrieve':
            return ConversationDetailSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        """Ajoute automatiquement l'utilisateur comme participant"""
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Ajoute un participant à une conversation"""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(pk=user_id)
            conversation.participants.add(user)
            return Response({'status': 'participant added'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filtre les messages visibles par l'utilisateur"""
        return Message.objects.filter(
            conversation__participants=self.request.user
        ).order_by('-sent_at')

    def get_serializer_class(self):
        """Utilise le serializer détaillé pour la récupération"""
        if self.action in ['retrieve', 'list']:
            return MessageDetailSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        """Définit automatiquement l'expéditeur"""
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['get'])
    def conversation_messages(self, request, pk=None):
        """Récupère tous les messages d'une conversation spécifique"""
        conversation = self.get_object()
        messages = Message.objects.filter(
            conversation=conversation
        ).order_by('sent_at')
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)