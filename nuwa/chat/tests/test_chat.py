from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from chat.models import Character

User = get_user_model()


class ChatBotTestCase(APITestCase):
    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def setUp(self):
        self.user = User.objects.create_user(
            username="Bob",
            password="password",
        )
        self.authenticate(self.user)
        self.character = Character.objects.create(
            owner=self.user,
            name="Anna",
            description="Description",
            system_prompt="You are bot",
            is_private=False,
            is_hidden_prompt=False,
        )

    def test_send_message(self):
        response = self.client.post(
            get_chat_url(),
            {
                "message": "Hello my friend! What you did today?",
                "character_id": self.character.pk,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data["response"]) > 0)

    def test_gen_image(self):
        response = self.client.post(get_generate_image_url())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data["image_base64"]) > 0)
        self.assertTrue(len(response.data["filename"]) > 0)


def get_chat_url():
    return reverse("chat:chat")


def get_generate_image_url():
    return reverse("chat:image")
