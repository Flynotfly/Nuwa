from rest_framework import serializers

from chat.models import Chat


class ChatListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = [
            "id",
            "character",
            "character_name",
            "last_message_text",
            "last_message_datetime",
        ]
        read_only_fields = [
            "id",
            "character",
            "character_name",
            "last_message_text",
            "last_message_datetime",
        ]


class ChatCreateSerializer(serializers.Serializer):
    character_id = serializers.IntegerField()


class CharacterDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = [
            "id",
            "owner",
            "character",
            "character_name",
            "system_prompt",
            "description",
            "is_hidden_prompt",
            "structure",
        ]
        read_only_fields = [
            "id",
            "owner",
            "character",
            "character_name",
            "system_prompt",
            "description",
            "is_hidden_prompt",
            "structure",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if (
            instance.is_hidden_prompt
            and request
            and hasattr(request, "user")
            and request.user.is_authenticated
            and instance.owner != request.user
        ):
            data["system_prompt"] = ""
        return data
