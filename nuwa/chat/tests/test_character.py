from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from chat.models import Character

User = get_user_model()


class CharacterTestCase(APITestCase):
    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def setUp(self):
        login_data = {
            "username": "Bob",
            "password": "password",
        }
        self.user = User.objects.create_user(**login_data)
        self.other_user = User.objects.create_user(
            username="John",
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
        self.character_private = Character.objects.create(
            owner=self.user,
            name="Paul",
            system_prompt="You are bot",
            is_private=True,
            is_hidden_prompt=False,
        )
        self.character_other_user = Character.objects.create(
            owner=self.other_user,
            name="Martin",
            system_prompt="You are bot",
            is_private=False,
            is_hidden_prompt=False,
        )
        self.charater_private_other_user = Character.objects.create(
            owner=self.other_user,
            name="Bob",
            system_prompt="You are bot",
            is_private=True,
            is_hidden_prompt=False,
        )

    def test_get_list_of_characters(self):
        response = self.client.get(get_list_url())
        self.assertEqual(response.status_code, 200)
        returned_ids = {character["id"] for character in response.data}
        expected_ids = {self.character.pk, self.character_other_user.pk}
        self.assertEqual(returned_ids, expected_ids)

    def test_get_single_character(self):
        response = self.client.get(get_detail_url(self.character.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["system_prompt"], self.character.system_prompt)
        self.assertEqual(response.data["description"], self.character.description)
        self.assertEqual(response.data["owner_username"], self.character.owner.username)

    def test_get_character_with_hidden_prompt_owner(self):
        char = Character.objects.create(
            owner=self.user,
            name="Anna",
            description="Description",
            system_prompt="You are bot",
            is_private=False,
            is_hidden_prompt=True,
        )
        response = self.client.get(get_detail_url(char.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["system_prompt"], char.system_prompt)

    def test_get_character_with_hidden_prompt_non_owner(self):
        char = Character.objects.create(
            owner=self.other_user,
            name="Bob",
            description="Description",
            system_prompt="You are bot",
            is_private=False,
            is_hidden_prompt=True,
        )
        response = self.client.get(get_detail_url(char.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["system_prompt"], "")


def get_list_url():
    return reverse("chat:characters-list-create")


def get_detail_url(pk: int):
    return reverse("chat:characters-detail", kwargs={"pk": pk})
