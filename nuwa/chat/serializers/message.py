from rest_framework import serializers

from chat.models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "owner",
            "chat",
            "role",
            "media_type",
            "message",
            "media",
            "conducted",
            "history",
        ]
        read_only_fields = ["id", "owner", "chat"]
