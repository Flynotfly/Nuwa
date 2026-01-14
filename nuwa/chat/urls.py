from django.urls import path

from .views import ChatBotView, GenerateImageView, ComfyWebhookReceiver


app_name = "chat"


urlpatterns = [
    path("chat", ChatBotView.as_view(), name="chat"),
    path("image", GenerateImageView.as_view(), name="image"),
    path("comfy-webhook", ComfyWebhookReceiver.as_view(), name="webhook-receiver"),
]
