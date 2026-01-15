from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AuthViewsTestCase(APITestCase):
    def setUp(self):
        self.username = "Bob"
        self.password = "password"
        self.email = "Bob@bob.com"
        self.first_name = "Bob1"
        self.last_name = "Bob2"
        self.full_name = f"{self.first_name} {self.last_name}"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
        )

    def get_access_token(self):
        reponse = self.client.post(
            get_login_url(),
            {"username": self.username, "password": self.password},
            format="json",
        )
        return reponse.data["access"]

    def test_login_success(self):
        response = self.client.post(
            get_login_url(),
            {"username": self.username, "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_miss_username(self):
        response = self.client.post(
            get_login_url(), {"password": self.password}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_login_miss_password(self):
        response = self.client.post(
            get_login_url(), {"username": self.username}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_login_invalid_credentials(self):
        response = self.client.post(
            get_login_url(), {"username": "wrong", "password": "wrong"}, format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_logged_out_successfully(self):
        response = self.client.post(
            get_login_url(),
            {"username": self.username, "password": self.password},
            format="json",
        )
        access_token = response.data["access"]
        refresh_token = response.data["refresh"]

        response = self.client.post(
            get_logout_url(),
            {"refresh": refresh_token},
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(Exception):
            token = RefreshToken(refresh_token)
            token.access_token

    def test_logged_not_authenticated(self):
        response = self.client.post(
            get_login_url(),
            {"username": self.username, "password": self.password},
            format="json",
        )
        access_token = response.data["access"]
        refresh_token = response.data["refresh"]
        response = self.client.post(
            get_logout_url(),
            {"refresh": refresh_token},
        )
        self.assertEqual(response.status_code, 200)

    def test_logged_no_refresh_token(self):
        response = self.client.post(
            get_login_url(),
            {"username": self.username, "password": self.password},
            format="json",
        )
        access_token = response.data["access"]
        refresh_token = response.data["refresh"]
        response = self.client.post(
            get_logout_url(),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_get_session_authenticated(self):
        response = self.client.post(
            get_login_url(),
            {"username": self.username, "password": self.password},
            format="json",
        )
        access_token = response.data["access"]
        response = self.client.get(
            get_session_url(),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"]["username"], self.username)
        self.assertEqual(response.data["user"]["email"], self.email)
        self.assertEqual(response.data["user"]["firstName"], self.first_name)
        self.assertEqual(response.data["user"]["lastName"], self.last_name)
        self.assertEqual(response.data["user"]["fullName"], self.full_name)

    def test_get_session_not_authenticated(self):
        response = self.client.get(get_session_url())
        self.assertEqual(response.status_code, 401)

    def test_register_successful(self):
        username = "Paul"
        response = self.client.post(
            get_register_url(),
            {
                "username": username,
                "password": "password",
                "email": "bob@bob.com",
                "firstName": "Bob",
                "lastName": "Paul",
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username=username).exists())

    def test_register_no_username(self):
        response = self.client.post(
            get_register_url(),
            {
                "password": "password",
                "email": "bob@bob.com",
                "first_name": "Bob",
                "last_name": "Paul",
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_register_no_password(self):
        response = self.client.post(
            get_register_url(),
            {
                "username": "Paul",
                "email": "bob@bob.com",
                "first_name": "Bob",
                "last_name": "Paul",
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_register_invalid_email(self):
        response = self.client.post(
            get_register_url(),
            {
                "username": "Paul",
                "password": "password",
                "email": "bob.com",
                "first_name": "Bob",
                "last_name": "Paul",
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_register_username_already_taken(self):
        response = self.client.post(
            get_register_url(),
            {
                "username": self.username,
                "password": "password",
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_refresh_view(self):
        response = self.client.post(
            get_login_url(),
            {"username": self.username, "password": self.password},
            format="json",
        )
        refresh_token = response.data["refresh"]
        response = self.client.post(
            get_refresh_url(),
            {"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)


def create_user(
    username: str = "Bob",
    password: str = "jjow3d3@",
    email: str = "Bob@bob.com",
    first_name: str = "John",
    last_name: str = "Smith",
) -> User:
    return User.objects.create_user(
        username=username,
        password=password,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )


def batch_create_user(usernames: list) -> list:
    created_users = []
    for username in usernames:
        user = create_user(username)
        created_users.append(user)
    return created_users


def get_login_url():
    return reverse("user:login")


def get_logout_url():
    return reverse("user:logout")


def get_session_url():
    return reverse("user:session")


def get_register_url():
    return reverse("user:register")


def get_refresh_url():
    return reverse("user:refresh")
