from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:create")


def create_user(**prams):
    """Shortcut for get_user_model's create user function"""
    return get_user_model().objects.create_user(**prams)


class PublicUsersAPITests(TestCase):
    """Test the user's API public"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creatinge a user with valid payload"""
        payload = {
            "email": "test@mail.com",
            "password": "TestPord123",
            "name": "Test User",
        }

        # Create an API with above payload
        response = self.client.post(CREATE_USER_URL, payload)

        # Check if the API returned the correct status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if the password got saved
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload["password"]))

        # Check if the API didn't return the password in the response
        self.assertNotIn("password", response.data)

    def test_user_exists(self):
        """Test creating a user that already exists"""
        payload = {
            "email": "test@mail.com",
            "password": "TestPord123",
            "name": "Test User",
        }
        create_user(**payload)

        # Create an API with above payload
        response = self.client.post(CREATE_USER_URL, payload)

        # Check if the API returned the correct status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """The password should be more than 5 charachters"""
        payload = {
            "email": "test@mail.com",
            "password": "pw",
            "name": "Test User",
        }
        response = self.client.post(CREATE_USER_URL, payload)

        # Check if the API returned the correct status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that the user was never created
        user_exists = (
            get_user_model().objects.filter(email=payload["email"]).exists()
        )
        self.assertFalse(user_exists)
