from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from chat.views.character import (
    CharacterRetrieveUpdateDestroyView,
    CharaterListCreateView,
)
from chat.views.chat import ChatListCreateView, ChatRetrieveDestroyView
from chat.views.chatting import ChatBotView, GenerateImageView
from chat.views.message import MessageListView

app_name = "chat"


urlpatterns = [
    path("chat", ChatBotView.as_view(), name="chat"),
    path("image", GenerateImageView.as_view(), name="image"),
    path("characters", CharaterListCreateView.as_view(), name="characters-list-create"),
    path(
        "characters/<int:pk>",
        CharacterRetrieveUpdateDestroyView.as_view(),
        name="characters-detail",
    ),
    path("chats", ChatListCreateView.as_view(), name="chats-list-create"),
    path("chats/<int:pk>", ChatRetrieveDestroyView.as_view(), name="chats-detail"),
    path("chats/<int:chat_id>/messages", MessageListView.as_view(), name="messages"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
