from rest_framework import generics
from rest_framework.permissions import AllowAny

from chat.models import Character
from chat.serializers.character import CharacterNameSerializer


class CharaterListView(generics.ListAPIView):
    serializer_class = CharacterNameSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Character.objects.filter(is_private=False)
