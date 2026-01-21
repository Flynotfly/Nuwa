from rest_framework import generics, status
from rest_framework.response import Response

from chat.models import Chat
from chat.serializers.chat import ChatListSerializer, ChatCreateSerializer, ChatDetailSerializer
from chat.permissions import IsOwnerOrReadOnly


class ChatListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == "POST":
            return ChatCreateSerializer
        return ChatListSerializer

    def get_queryset(self):
        return Chat.objects.filter(owner=self.request.user, is_active=True)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat = serializer.save()
        output_serializer = ChatDetailSerializer(chat)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class ChatRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    serializer_class = ChatDetailSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        return Chat.objects.filter(owner=self.request.user, is_active=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)
