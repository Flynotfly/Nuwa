from rest_framework import serializers

from chat.models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "role",
            "media_type",
            "message",
            "media",
            "conducted",
            "history",
        ]


class MessageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "message",
        ]
