from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from chat.views.character import (CharacterListCreateView,
                                  CharacterRetrieveUpdateDestroyView)
from chat.views.chat import ChatListCreateView, ChatRetrieveDestroyView
from chat.views.chat_bot.chat_bot import ChatBotView
from chat.views.message import MessageListView, MessageUpdateView

app_name = "chat"


urlpatterns = [
    path("chat", ChatBotView.as_view(), name="chat"),
    path(
        "characters", CharacterListCreateView.as_view(), name="characters-list-create"
    ),
    path(
        "characters/<int:pk>",
        CharacterRetrieveUpdateDestroyView.as_view(),
        name="characters-detail",
    ),
    path("chats", ChatListCreateView.as_view(), name="chats-list-create"),
    path("chats/<int:pk>", ChatRetrieveDestroyView.as_view(), name="chats-detail"),
    path("chats/<int:chat_id>/messages", MessageListView.as_view(), name="messages"),
    path("messages/<int:pk>", MessageUpdateView.as_view(), name="messages-detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
