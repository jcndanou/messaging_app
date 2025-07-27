from rest_framework import serializers
from .models import User, Conversation, Message
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 
                 'phone_number', 'role', 'created_at']
        extra_kwargs = {
            'password_hash': {'write_only': True},
            'created_at': {'read_only': True}
        }

    def create(self, validated_data):
        # Hash le mot de passe avant création
        validated_data['password_hash'] = make_password(validated_data.get('password_hash', ''))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Hash le mot de passe si modifié
        if 'password_hash' in validated_data:
            validated_data['password_hash'] = make_password(validated_data['password_hash'])
        return super().update(instance, validated_data)


class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'created_at']
        extra_kwargs = {
            'created_at': {'read_only': True}
        }


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    conversation = serializers.PrimaryKeyRelatedField(
        queryset=Conversation.objects.all()
    )

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'conversation', 
                 'message_body', 'sent_at']
        extra_kwargs = {
            'sent_at': {'read_only': True}
        }


# Serializer pour les réponses détaillées
class MessageDetailSerializer(MessageSerializer):
    sender = UserSerializer(read_only=True)


class ConversationDetailSerializer(ConversationSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ['messages']