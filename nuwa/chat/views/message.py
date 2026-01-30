from rest_framework import generics

from chat.models import Message
from chat.serializers.message import MessageSerializer


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        chat_id = self.kwargs["chat_id"]
        return Message.objects.filter(
            owner=self.request.user, chat__id=chat_id, is_active=True
        )
