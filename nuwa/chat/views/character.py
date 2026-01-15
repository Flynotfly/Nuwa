from django.db.models import Q
from rest_framework import generics

from chat.models import Character
from chat.serializers.character import CharacterNameSerializer


class CharaterListView(generics.ListAPIView):
    serializer_class = CharacterNameSerializer

    def get_queryset(self):
        return Character.objects.filter(is_private=False)
