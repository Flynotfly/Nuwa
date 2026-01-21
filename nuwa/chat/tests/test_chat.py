from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
#
# from chat.models import Chat, Character
#
# User = get_user_model()
#
#
# class ChatTestCase(APITestCase):
#     def authenticate(self, user):
#         refresh = RefreshToken.for_user(user)
#         self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
#
#     def setUp(self):
#         login_data = {
#             "username": "Bob",
#             "password": "password",
#         }
#         self.user = User.objects.create_user(**login_data)
#         self.character =
#         self.chat = Chat.objets.create(
#
#         )
