from rest_framework import serializers

from ..models import Character


class CharacterNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = ["id", "name", "description"]


class CharacterFullSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Character
        fields = [
            "id",
            "owner",
            "name",
            "description",
            "system_prompt",
            "is_private",
            "is_hidden_prompt",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.is_hidden_prompt:
            data["system_prompt"] = ""
        return data
