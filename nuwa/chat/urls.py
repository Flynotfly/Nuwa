from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views.character import CharacterRetrieveUpdateDestroyView, CharaterListCreateView
from .views.chat import ChatBotView, GenerateImageView

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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
