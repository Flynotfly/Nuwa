from rest_framework.test import APITestCase
from django.urls import reverse


class ChatBotTestCase(APITestCase):
    def test_send_message(self):
        response = self.client.post(
            get_chat_url(),
            {"message": "Hello my friend! What you did today?"}
        )
        self.assertEqual(response.status_code, 200)
        print(response.data["response"])
        self.assertTrue(len(response.data["response"]) > 0)


def get_chat_url():
    return reverse("chat:chat")
