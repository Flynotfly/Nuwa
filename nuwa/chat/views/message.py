from rest_framework import generics

from chat.models import Message
from chat.serializers.message import MessageSerializer, MessageUpdateSerializer


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        chat_id = self.kwargs["chat_id"]
        return Message.objects.filter(
            owner=self.request.user, chat__id=chat_id, is_active=True
        )


class MessageUpdateView(generics.UpdateAPIView):
    serializer_class = MessageUpdateSerializer
    http_method_names = ["patch"]

    def get_queryset(self):
        return Message.objects.filter(
            owner=self.request.user,
        )
