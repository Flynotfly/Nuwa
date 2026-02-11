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
                "message": "I played tennis today!",
                "is_user_message": "True",
                "chat_id": self.chat.pk,
                "answer_type": "text",
            },
        )
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data["messages"][1]["message"]) > 0)
        self.assertTrue(response.data["messages"][1]["id"])
        messages_ids = [
            response.data["messages"][0]["id"],
            response.data["messages"][1]["id"],
        ]
        response = self.client.post(
            get_chat_url(),
            {
                "message": "What i did today?",
                "is_user_message": "True",
                "chat_id": self.chat.pk,
                "previous_message_id": response.data["messages"][1]["id"],
                "answer_type": "text",
            },
        )
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data["messages"][1]["message"]) > 0)
        self.assertTrue(response.data["messages"][1]["id"])
        messages_ids.append(response.data["messages"][0]["id"])
        messages_ids.append(response.data["messages"][1]["id"])
        last_message = Message.objects.get(pk=messages_ids[-1])
        self.assertEqual(last_message.history, messages_ids[:-1])
        self.chat.refresh_from_db()
        self.assertEqual(self.chat.structure, messages_ids)

    def test_gen_text_without_user_message(self):
        response = self.client.post(
            get_chat_url(),
            {
                "chat_id": self.chat.pk,
                "answer_type": "text",
            },
        )
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data["messages"][0]["message"]) > 0)
        self.assertTrue(response.data["messages"][0]["id"])
        messages_ids = [response.data["messages"][0]["id"]]
        response = self.client.post(
            get_chat_url(),
            {
                "chat_id": self.chat.pk,
                "answer_type": "text",
                "previous_message_id": response.data["messages"][0]["id"],
            },
        )
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data["messages"][0]["message"]) > 0)
        self.assertTrue(response.data["messages"][0]["id"])
        messages_ids.append(response.data["messages"][0]["id"])
        last_message = Message.objects.get(pk=messages_ids[-1])
        self.assertEqual(last_message.history, messages_ids[:-1])
        self.chat.refresh_from_db()
        self.assertEqual(self.chat.structure, messages_ids)

    def test_gen_image_without_user_message(self):
        response = self.client.post(
            get_chat_url(),
            {
                "chat_id": self.chat.pk,
                "answer_type": "image",
            },
        )
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["messages"][0]["media_type"], "image")
        self.assertTrue(response.data["messages"][0]["media"])

    def test_gen_image_with_user_message(self):
        response = self.client.post(
            get_chat_url(),
            {
                "chat_id": self.chat.pk,
                "answer_type": "image",
                "is_user_message": "true",
                "message": "Generate image with blue skirt and white blouse.",
            },
        )
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["messages"][1]["media_type"], "image")
        self.assertTrue(response.data["messages"][1]["media"])
        response = self.client.post(
            get_chat_url(),
            {
                "chat_id": self.chat.pk,
                "answer_type": "image",
                "previous_message_id": response.data["messages"][1]["id"],
                "is_user_message": "true",
                "message": "Add night and stars.",
            },
        )
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["messages"][1]["media_type"], "image")
        self.assertTrue(response.data["messages"][1]["media"])

    def test_detect_message_with_text_answer(self):
        response = self.client.post(
            get_chat_url(),
            {
                "chat_id": self.chat.pk,
                "is_user_message": "true",
                "message": "Hello my love.",
            },
        )
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["messages"][1]["media_type"], "text")

    def test_detect_message_with_image_answer(self):
        response = self.client.post(
            get_chat_url(),
            {
                "chat_id": self.chat.pk,
                "is_user_message": "true",
                "message": "Show me you in skirt.",
            },
        )
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["messages"][1]["media_type"], "image")


def get_chat_url():
    return reverse("chat:chat")
