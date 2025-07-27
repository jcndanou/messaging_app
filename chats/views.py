from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .filters import MessageFilter, ConversationFilter
from .pagination import MessagePagination
from .permissions import IsParticipantOfConversation
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
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ConversationFilter

    def get_queryset(self):
        """Ne retourne que les conversations de l'utilisateur connecté"""
        if self.request.user.is_authenticated:
            # Filtrer les conversations où l'utilisateur est un participant
            return Conversation.objects.filter(participants=self.request.user).order_by('-created_at')
        return Conversation.objects.none() # Aucun résultat si non authentifié

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsParticipantOfConversation])
    def send_message(self, request, pk=None):
        conversation = get_object_or_404(Conversation, pk=pk)
        # La permission IsParticipantOfConversation gère déjà si l'utilisateur est participant

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            # L'expéditeur du message est l'utilisateur authentifié
            message = Message.objects.create(
                conversation=conversation,
                sender=self.request.user, # Utilisez self.request.user comme expéditeur
                message_body=serializer.validated_data['message_body']
            )
            return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    queryset = Message.objects.all().order_by('-sent_at')
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter

    def get_queryset(self):
        """Filtre les messages visibles par l'utilisateur où l'utilisateur est participant"""
        if self.request.user.is_authenticated:
            return Message.objects.filter(
                conversation__participants=self.request.user
            ).order_by('sent_at') # Les messages d'une conversation doivent être triés par date
        return Message.objects.none()

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