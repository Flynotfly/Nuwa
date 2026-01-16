from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from chat.models import Character
from chat.permissions import IsOwnerOrReadOnly
from chat.serializers.character import (CharacterFullSerializer,
                                        CharacterNameSerializer)


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
        return Character.objects.filter(is_private=False, is_active=True)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CharacterRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CharacterFullSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        return Character.objects.filter(
            Q(owner=self.request.user) | Q(is_private=False), is_active=True
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)
