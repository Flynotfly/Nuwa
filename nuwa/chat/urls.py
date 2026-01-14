from django.urls import path

from .views.chat import ChatBotView, GenerateImageView, ComfyWebhookReceiver
from .views.character import CharaterListView


app_name = "chat"


urlpatterns = [
    path("chat", ChatBotView.as_view(), name="chat"),
    path("image", GenerateImageView.as_view(), name="image"),
    path("comfy-webhook", ComfyWebhookReceiver.as_view(), name="webhook-receiver"),

    path("characters", CharaterListView.as_view(), name="characters-list"),
]
