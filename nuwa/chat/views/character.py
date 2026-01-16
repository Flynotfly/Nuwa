from rest_framework import generics
from django.db.models import Q
from rest_framework.permissions import AllowAny

from chat.models import Character
from chat.serializers.character import CharacterNameSerializer, CharacterFullSerializer


class CharaterListView(generics.ListAPIView):
    serializer_class = CharacterNameSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Character.objects.filter(is_private=False)


class CharacterCreateView(generics.CreateAPIView):
    serializer_class = CharacterFullSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CharacterRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CharacterFullSerializer

    def get_queryset(self):
        return Character.objects.filter(
            Q(owner=self.request.user) | Q(is_private=False)
        )
