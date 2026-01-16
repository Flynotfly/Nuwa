from rest_framework import generics
from django.db.models import Q
from rest_framework.permissions import AllowAny, IsAuthenticated

from chat.models import Character
from chat.serializers.character import CharacterNameSerializer, CharacterFullSerializer


class CharaterListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == "POST":
            return CharacterFullSerializer
        return CharacterNameSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        return Character.objects.filter(is_private=False)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CharacterRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CharacterFullSerializer

    def get_queryset(self):
        return Character.objects.filter(
            Q(owner=self.request.user) | Q(is_private=False)
        )
