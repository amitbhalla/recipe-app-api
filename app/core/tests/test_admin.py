from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


class AdminSiteTests(TestCase):
    def setUp(self):
        """Setup by creating a user and a superuser"""
        self.client = Client()
        superuser_email = "superuser@mail.com"
        superuser_password = "TestPass123"
        superuser_name = "Test Super User"
        self.admin_user = get_user_model().objects.create_superuser(
            email=superuser_email,
            password=superuser_password,
            name=superuser_name,
        )
        user_email = "user@mail.com"
        user_password = "TestPass123"
        user_name = "Test User"
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email=user_email, password=user_password, name=user_name
        )

    def test_users_listed(self):
        """Test that users are listed on the admin portal user page"""
        url = reverse("admin:core_user_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)

    def test_user_change_page(self):
        """Test that user edit page works"""
        url = reverse("admin:core_user_change", args=[self.user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
