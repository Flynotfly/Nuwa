from rest_framework import serializers

from chat.models import Chat, Character


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
        read_only_fields = fields


class ChatCreateSerializer(serializers.Serializer):
    character_id = serializers.IntegerField()

    def validate_character_id(self, value):
        try:
            Character.objects.get(id=value, is_active=True)
        except Character.DoesNotExist:
            raise serializers.ValidationError("Character does not exists")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        character = Character.objects.get(pk=validated_data["character_id"])
        chat = Chat.objects.create(
            owner=user,
            character=character,
            character_name=character.name,
            system_prompt=character.system_prompt,
            description=character.description,
            is_hidden_prompt=character.is_hidden_prompt,
            is_active=True,
        )
        return chat


class ChatDetailSerializer(serializers.ModelSerializer):
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
        read_only_fields = fields

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
