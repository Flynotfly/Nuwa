from rest_framework import serializers

from ..models import Character


class CharacterNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = ["id", "name"]
