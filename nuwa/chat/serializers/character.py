from rest_framework import serializers

from ..models import Character


class CharacterNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = ["id", "name", "description"]


class CharacterFullSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Character
        fields = [
            "id",
            "owner",
            "owner_username",
            "name",
            "description",
            "system_prompt",
            "is_private",
            "is_hidden_prompt",
        ]
        read_only_fields = ["id", "owner"]

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
