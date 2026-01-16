from django.urls import path

from .views.character import (CharacterRetrieveUpdateDestroyView,
                              CharaterListCreateView)
from .views.chat import ChatBotView, ComfyWebhookReceiver, GenerateImageView

app_name = "chat"


urlpatterns = [
    path("chat", ChatBotView.as_view(), name="chat"),
    path("image", GenerateImageView.as_view(), name="image"),
    path("comfy-webhook", ComfyWebhookReceiver.as_view(), name="webhook-receiver"),
    path("characters", CharaterListCreateView.as_view(), name="characters-list-create"),
    path(
        "characters/<int:pk>",
        CharacterRetrieveUpdateDestroyView.as_view(),
        name="characters-detail",
    ),
]
