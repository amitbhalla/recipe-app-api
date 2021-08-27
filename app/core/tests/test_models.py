from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user():
    """Creates a sample user for our tests"""
    email = "test@mail.com"
    password = "TestPass123"
    name = "Some Name"
    return get_user_model().objects.create_user(
        email=email, password=password, name=name
    )


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating a new user with email is successful"""
        email = "test@mail.com"
        password = "TestPass123"
        user = get_user_model().objects.create_user(
            email=email, password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = "test@MAIL.com"
        password = "TestPass123"
        user = get_user_model().objects.create_user(
            email=email, password=password
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email creates an error"""
        with self.assertRaises(ValueError):
            password = "TestPass123"
            get_user_model().objects.create_user(email=None, password=password)

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        email = "test@mail.com"
        password = "TestPass123"
        user = get_user_model().objects.create_superuser(
            email=email, password=password
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test that tag string repersentation"""
        tag = models.Tag.objects.create(user=sample_user(), name="Vegan")

        self.assertEqual(str(tag), tag.name)
