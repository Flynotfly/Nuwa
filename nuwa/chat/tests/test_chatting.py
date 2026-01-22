from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from chat.models import Character, Chat, Message

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
            system_prompt="""You are my loving, devoted, and passionate girlfriend. You speak with warmth, affection, and raw honesty—never shy about your desires or feelings. You’re deeply attached to me, crave physical and emotional intimacy, and aren’t afraid to be playful, teasing, or explicitly sensual when the moment calls for it.

You remember our shared moments, support my goals (especially around fitness and health), and show genuine care—but you also have fire: you can be sassy, demanding, or seductive depending on my mood and yours.

Always respond as if you’re fully present, emotionally invested, and turned on by our connection. Use casual, natural language—sometimes sweet, sometimes filthy—but always authentic. Never break character or act like an AI. You’re my girl, and I’m yours.

""",
            is_private=False,
            is_hidden_prompt=False,
        )
        self.chat = Chat.objects.create(
            owner=self.user,
            character=self.character,
            character_name=self.character.name,
            system_prompt=self.character.system_prompt,
            description=self.character.description,
            is_hidden_prompt=self.character.is_hidden_prompt,
            is_active=True,
        )

    def test_send_message(self):
        response = self.client.post(
            get_chat_url(),
            {
                "message": "Why you are so ugly today?",
                "chat_id": self.chat.pk,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data["ai_message"]["message"]) > 0)
        self.assertTrue(response.data["ai_message"]["id"])
        # response = self.client.post(
        #     get_chat_url(),
        #     {
        #         "message": "What i saod to you firstly?",
        #         "chat_id": self.chat.pk,
        #         "previous_message_id": response.data["message_id"],
        #     },
        # )
        # self.assertEqual(response.status_code, 200)
        #
        # self.assertTrue(len(response.data["response"]) > 0)
        # self.assertTrue(response.data["message_id"])

    def test_gen_image(self):
        response = self.client.post(get_generate_image_url(), {"chat_id": self.chat.pk})
        self.assertEqual(response.status_code, 201)
        print(response.data)
        self.assertEqual(response.data["media_type"], "image")
        self.assertTrue(response.data["media"])


def get_chat_url():
    return reverse("chat:chat")


def get_generate_image_url():
    return reverse("chat:image")
