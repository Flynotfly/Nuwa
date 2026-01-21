from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from chat.models import Character, Chat

User = get_user_model()


class ChatTestCase(APITestCase):
    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def setUp(self):
        login_data = {
            "username": "Bob",
            "password": "password",
        }
        self.user = User.objects.create_user(**login_data)
        self.authenticate(self.user)
        self.character = Character.objects.create(
            owner=self.user,
            name="Anna",
            description="Description",
            system_prompt="""You are bot""",
            is_private=False,
            is_hidden_prompt=False,
        )
        self.chat = Chat.objects.create(
            owner=self.user,
            character=self.character,
            character_name="Chat1",
            system_prompt="Prompt1",
            description="Test1",
            is_hidden_prompt=False,
            is_active=True,
        )
        self.chat_2 = Chat.objects.create(
            owner=self.user,
            character=self.character,
            character_name="Chat2",
            system_prompt="Prompt2",
            description="Test2",
            is_hidden_prompt=True,
            is_active=True,
        )

    def test_get_all_chats(self):
        response = self.client.get(get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn(response.data[0]["character_name"], ["Chat1", "Chat2"])

    def test_get_chat_non_hidden_prompt(self):
        response = self.client.get(get_detail_url(self.chat.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["system_prompt"], self.chat.system_prompt)

    def test_get_chat_hidden_prompt(self):
        response = self.client.get(get_detail_url(self.chat_2.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["system_prompt"], "")

    def test_create_chat(self):
        response = self.client.post(
            get_create_url(), {"character_id": self.character.id}
        )
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


def get_list_url():
    return reverse("chat:chats-list-create")


def get_create_url():
    return reverse("chat:chats-list-create")


def get_detail_url(pk: int):
    return reverse("chat:chats-detail", kwargs={"pk": pk})
