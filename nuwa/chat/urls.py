from django.urls import path

from .views.character import CharaterListView
from .views.chat import ChatBotView, ComfyWebhookReceiver, GenerateImageView

app_name = "chat"


urlpatterns = [
    path("chat", ChatBotView.as_view(), name="chat"),
    path("image", GenerateImageView.as_view(), name="image"),
    path("comfy-webhook", ComfyWebhookReceiver.as_view(), name="webhook-receiver"),
    path("characters", CharaterListView.as_view(), name="characters-list"),
]
